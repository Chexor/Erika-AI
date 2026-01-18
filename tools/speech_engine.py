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

logger = logging.getLogger("TOOLS.SpeechEngine")

# Maximum age of temp files before cleanup (in seconds)
TEMP_FILE_MAX_AGE = 3600  # 1 hour


class SpeechEngine:
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

        # Enforce offline mode by default, allow periodic update checks
        self._tts_settings = self._load_tts_settings()
        self._offline_mode = bool(self._tts_settings.get("tts_offline_mode", True))
        self._update_days = int(self._tts_settings.get("tts_update_days", 7))
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
                        logger.info("SpeechEngine: TTS update detected. See tts_update_log.txt for details.")
                    else:
                        logger.info("SpeechEngine: No TTS cache updates detected.")
                    self._write_update_check()
            except (ImportError, RuntimeError, OSError) as e:
                logger.error(f"Failed to init TTSModel: {e}")
            finally:
                if self._offline_mode:
                    self._set_hf_offline(True)
        else:
            logger.warning("PocketTTS module not found. Audio will be simulated.")

    def _load_tts_settings(self) -> dict:
        """Loads TTS settings from config/user.json."""
        settings_path = os.path.join(os.getcwd(), "config", "user.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"SpeechEngine: Failed to load settings: {e}")
        return {}

    def _set_hf_offline(self, offline: bool) -> None:
        """Controls HF/transformers offline mode."""
        val = "1" if offline else "0"
        os.environ["HF_HUB_OFFLINE"] = val
        os.environ["TRANSFORMERS_OFFLINE"] = val

    def _should_allow_update_check(self) -> bool:
        """Returns True if the periodic online check is due."""
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
        """Updates the last successful online check timestamp."""
        try:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with open(self._update_check_path, 'w', encoding='utf-8') as f:
                f.write(now)
        except Exception as e:
            logger.debug(f"SpeechEngine: Failed to write update check: {e}")

    def _get_hf_cache_dir(self) -> str:
        """Returns the HuggingFace cache directory, if available."""
        env_cache = os.environ.get("HUGGINGFACE_HUB_CACHE") or os.environ.get("HF_HUB_CACHE")
        if env_cache:
            return env_cache
        hf_home = os.environ.get("HF_HOME")
        if hf_home:
            return os.path.join(hf_home, "hub")
        return os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")

    def _detect_cache_updates(self, cache_dir: Optional[str], start_time: Optional[float]) -> list:
        """Returns a list of updated cache files since start_time."""
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
        """Writes update details to the log file."""
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
            logger.debug(f"SpeechEngine: Failed to write update log: {e}")

    def _cleanup_temp_files(self):
        """Removes old temporary files to prevent accumulation."""
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
                logger.info(f"SpeechEngine: Cleaned up {cleanup_count} old temp files")
        except OSError as e:
            logger.warning(f"SpeechEngine: Error during temp cleanup: {e}")

    def set_voice(self, voice_name: str):
        """Sets the active voice for TTS."""
        if voice_name:
            self.current_voice = voice_name
            logger.info(f"Voice set to: {voice_name}")

    def set_volume(self, volume: float):
        """Sets the volume multiplier (0.0 - 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume set to: {self.volume:.2f}")

    def stop(self):
        """Stops the current speech playback."""
        if self.is_speaking:
            self.stop_event.set()
            logger.info("SpeechEngine: Stop requested.")

    def speak(self, text: str, on_finished: Optional[Callable[[], None]] = None) -> bool:
        """Synthesizes text and plays audio asynchronously."""
        if not text:
            return False

        with self._speak_lock:
            # 1. Stop any existing playback
            if self.is_speaking:
                self.stop()
                # Wait for previous thread to exit (max 1s) to prevent overlap
                start_wait = time.time()
                while self.is_speaking and (time.time() - start_wait < 1.0):
                    time.sleep(0.05)
            
            # Reset stop signal for new playback
            self.stop_event.clear()
            self.is_speaking = True

            # Run in thread
            t = threading.Thread(target=self._speak_thread, args=(text, on_finished), daemon=True)
            t.start()
        return True

    def _speak_thread(self, text, on_finished):
        try:
            # 1. Synthesize & Stream
            if self.tts_model:
                logger.debug(f"Synthesizing stream: {text[:30]}... (Voice: {self.current_voice})")
                
                voice_state = self.tts_model.get_state_for_audio_prompt(self.current_voice)
                stream_gen = self.tts_model.generate_audio_stream(voice_state, text)
                
                # Get correct sample rate
                fs = self.tts_model.sample_rate

                # Stream to audio device
                with sd.OutputStream(samplerate=fs, channels=1) as sd_stream:
                    for chunk in stream_gen:
                        # Check stop signal
                        if self.stop_event.is_set():
                            logger.info("Playback interrupted by user.")
                            break
                            
                        # Convert tensor to numpy
                        audio_np = chunk.cpu().numpy()
                        
                        # Ensure 1D array
                        if len(audio_np.shape) > 1:
                            audio_np = audio_np.flatten()
                        
                        # Apply Volume
                        audio_np = audio_np * self.volume
                            
                        # Write to device
                        sd_stream.write(audio_np.astype(np.float32))
                
                logger.debug("Playback finished.")
                
            else:
                # Mock simulation
                logger.info(f"Simulating TTS: {text}")
                for _ in range(3):
                    if self.stop_event.is_set(): break
                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"Speech error: {e}")
        finally:
            # Fire callback if it exists and we weren't just interrupted by a new track.
            # CRITICAL: Check stop_event BEFORE setting is_speaking=False.
            # calling start() -> stop() -> wait() -> clear() -> start()
            # If we set is_speaking=False first, the new start() clears the flag 
            # before we check it, causing false firing.
            if on_finished and not self.stop_event.is_set():
                 try:
                     on_finished()
                 except Exception as e:
                     logger.error(f"Callback error: {e}")
            
            # Now we are truly done
            self.is_speaking = False
