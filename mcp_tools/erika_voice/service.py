import os
import time
import json
import datetime
import sounddevice as sd
import threading
import logging
import glob
import numpy as np
from typing import Optional, Callable

# Try importing the correct class from pocket_tts
try:
    from pocket_tts import TTSModel
except ImportError:
    TTSModel = None

logger = logging.getLogger("TOOLS.TTSService")

# Maximum age of temp files before cleanup (in seconds)
TEMP_FILE_MAX_AGE = 3600  # 1 hour

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), 'erika_home', 'temp')
        os.makedirs(self.output_dir, exist_ok=True)

        # Clean up old temp files on startup
        self._cleanup_temp_files()

        # Initialize TTS
        self.tts_model: Optional[object] = None
        self.current_voice = 'azelma'  # Default voice
        self.stop_event = threading.Event()
        self.is_speaking = False
        self.volume = 1.0
        self._speak_lock = threading.Lock()

        # Advanced Inference settings
        self.temperature = 0.7
        self.lsd_decode_steps = 1
        self.eos_threshold = -4.0

        # Enforce offline mode by default, allow periodic update checks
        self._tts_settings = self._load_tts_settings()
        self._offline_mode = bool(self._tts_settings.get("tts_offline_mode", True))
        self._update_days = int(self._tts_settings.get("tts_update_days", 7))
        
        # Sync advanced settings from loaded config
        self.temperature = float(self._tts_settings.get("tts_temperature", 0.7))
        self.lsd_decode_steps = int(self._tts_settings.get("tts_decode_steps", 1))
        self.eos_threshold = float(self._tts_settings.get("tts_eos_threshold", -4.0))
        self._update_check_path = os.path.join(os.getcwd(), "logs", "tts_update_check.txt")
        self._update_log_path = os.path.join(os.getcwd(), "logs", "tts_update.log")
        os.makedirs(os.path.dirname(self._update_check_path), exist_ok=True)

        if TTSModel:
            try:
                allow_online = self._offline_mode and self._should_allow_update_check()
                cache_dir = self._get_hf_cache_dir() if allow_online else None
                start_time = time.time() if allow_online else None

                if self._offline_mode:
                    self._set_hf_offline(not allow_online)

                logger.info("Loading PocketTTS Model...")
                self.tts_model = TTSModel.load_model()
                logger.info("PocketTTS Model loaded successfully.")

                if allow_online and self.tts_model:
                    updated = self._detect_cache_updates(cache_dir, start_time)
                    if updated:
                        self._write_update_log(updated)
                        logger.info("TTSService: TTS update detected details logged.")
                    else:
                        logger.info("TTSService: No TTS cache updates detected.")
                    self._write_update_check()
            except (ImportError, RuntimeError, OSError) as e:
                logger.error(f"Failed to init TTSModel: {e}")
            finally:
                if self._offline_mode:
                    self._set_hf_offline(True)
        else:
            logger.warning("PocketTTS module not found. Audio will be simulated.")

    def _load_tts_settings(self) -> dict:
        settings_path = os.path.join(os.getcwd(), "config", "user.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
        return {}

    def _set_hf_offline(self, offline: bool) -> None:
        val = "1" if offline else "0"
        os.environ["HF_HUB_OFFLINE"] = val
        os.environ["TRANSFORMERS_OFFLINE"] = val

    def _should_allow_update_check(self) -> bool:
        if not self._offline_mode or self._update_days <= 0:
            return False
        if not os.path.exists(self._update_check_path):
            return True
        try:
            with open(self._update_check_path, 'r', encoding='utf-8') as f:
                raw = f.read().strip()
            if not raw:
                return True
            last = datetime.datetime.fromisoformat(raw)
            if last.tzinfo is None:
                last = last.replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            return (now - last) >= datetime.timedelta(days=self._update_days)
        except Exception:
            return True

    def _write_update_check(self) -> None:
        try:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with open(self._update_check_path, 'w', encoding='utf-8') as f:
                f.write(now)
        except Exception as e:
            logger.debug(f"Failed to write update check: {e}")

    def _get_hf_cache_dir(self) -> str:
        env_cache = os.environ.get("HUGGINGFACE_HUB_CACHE") or os.environ.get("HF_HUB_CACHE")
        if env_cache:
            return env_cache
        hf_home = os.environ.get("HF_HOME")
        if hf_home:
            return os.path.join(hf_home, "hub")
        return os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")

    def _detect_cache_updates(self, cache_dir: Optional[str], start_time: Optional[float]) -> list:
        if not cache_dir or start_time is None:
            return []
        if not os.path.exists(cache_dir):
            return []
        updates = []
        try:
            for root, _, files in os.walk(cache_dir):
                for name in files:
                    path = os.path.join(root, name)
                    try:
                        mtime = os.path.getmtime(path)
                        if mtime >= start_time:
                            rel = os.path.relpath(path, cache_dir)
                            size = os.path.getsize(path)
                            updates.append((rel, size))
                    except OSError:
                        continue
        except OSError:
            return []
        return updates

    def _write_update_log(self, updates: list) -> None:
        try:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            lines = [f"[{timestamp}] TTS cache updates detected:"]
            for rel, size in updates[:50]:
                lines.append(f"- {rel} ({size} bytes)")
            if len(updates) > 50:
                lines.append(f"... truncated, total files: {len(updates)}")
            lines.append("")
            with open(self._update_log_path, 'a', encoding='utf-8') as f:
                f.write("\n".join(lines))
        except Exception as e:
            logger.debug(f"Failed to write update log: {e}")

    def _cleanup_temp_files(self):
        try:
            current_time = time.time()
            cleanup_count = 0
            for filepath in glob.glob(os.path.join(self.output_dir, '*')):
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > TEMP_FILE_MAX_AGE:
                        os.remove(filepath)
                        cleanup_count += 1
                except OSError as e:
                    logger.debug(f"Failed to remove temp file {filepath}: {e}")
            if cleanup_count > 0:
                logger.info(f"Cleaned up {cleanup_count} old temp files")
        except OSError as e:
            logger.warning(f"Error during temp cleanup: {e}")

    def set_voice(self, voice_name: str):
        if voice_name:
            self.current_voice = voice_name
            logger.info(f"Voice set to: {voice_name}")

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume set to: {self.volume:.2f}")

    def set_temperature(self, temp: float):
        self.temperature = max(0.0, min(2.0, temp))
        logger.info(f"TTS Personality (Temperature) set to: {self.temperature:.2f}")

    def set_decode_steps(self, steps: int):
        self.lsd_decode_steps = max(1, min(10, steps))
        logger.info(f"TTS Clarity (Decode Steps) set to: {self.lsd_decode_steps}")

    def set_eos_threshold(self, threshold: float):
        self.eos_threshold = max(-10.0, min(0.0, threshold))
        logger.info(f"TTS Sensitivity (EOS Threshold) set to: {self.eos_threshold:.2f}")

    def stop(self):
        if self.is_speaking:
            self.stop_event.set()
            logger.info("Stop requested.")

    def speak(self, text: str, on_finished: Optional[Callable[[], None]] = None) -> bool:
        if not text:
            return False

        with self._speak_lock:
            if self.is_speaking:
                self.stop()
                start_wait = time.time()
                while self.is_speaking and (time.time() - start_wait < 1.0):
                    time.sleep(0.05)
            
            self.stop_event.clear()
            self.is_speaking = True

            t = threading.Thread(target=self._speak_thread, args=(text, on_finished), daemon=True)
            t.start()
        return True

    def _speak_thread(self, text, on_finished):
        try:
            if self.tts_model:
                # Apply current inference settings to the model
                self.tts_model.temp = self.temperature
                self.tts_model.lsd_decode_steps = self.lsd_decode_steps
                self.tts_model.eos_threshold = self.eos_threshold
                
                logger.debug(f"Synthesizing: {text[:30]}... (Voice: {self.current_voice}, Temp: {self.temperature})")
                try:
                    voice_state = self.tts_model.get_state_for_audio_prompt(self.current_voice)
                    stream_gen = self.tts_model.generate_audio_stream(voice_state, text)
                    fs = self.tts_model.sample_rate

                    with sd.OutputStream(samplerate=fs, channels=1) as sd_stream:
                        for chunk in stream_gen:
                            if self.stop_event.is_set():
                                logger.info("Playback interrupted.")
                                break
                            audio_np = chunk.cpu().numpy()
                            if len(audio_np.shape) > 1:
                                audio_np = audio_np.flatten()
                            audio_np = audio_np * self.volume
                            sd_stream.write(audio_np.astype(np.float32))
                    logger.debug("Playback finished.")
                except Exception as e:
                     logger.error(f"Generation/Playback error: {e}")
            else:
                logger.info(f"Simulating TTS: {text}")
                for _ in range(3):
                    if self.stop_event.is_set(): break
                    time.sleep(0.5)
        except Exception as e:
            logger.error(f"Thread error: {e}")
        finally:
            if on_finished and not self.stop_event.is_set():
                 try:
                     on_finished()
                 except Exception as e:
                     logger.error(f"Callback error: {e}")
            self.is_speaking = False
