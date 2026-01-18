import os
import time
import sounddevice as sd
import threading
import logging
import glob
import numpy as np
from typing import Optional

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

        if TTSModel:
            try:
                logger.info("Loading PocketTTS Model (this may download weights)...")
                self.tts_model = TTSModel.load_model()
                logger.info("PocketTTS Model loaded successfully.")
            except (ImportError, RuntimeError, OSError) as e:
                logger.error(f"Failed to init TTSModel: {e}")
        else:
            logger.warning("PocketTTS module not found. Audio will be simulated.")

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

    def speak(self, text: str) -> bool:
        """Synthesizes text and plays audio asynchronously."""
        if not text:
            return False

        with self._speak_lock:
            # Stop any existing playback
            self.stop()
            # Wait a moment for previous thread to notice stop
            self.stop_event.clear()
            self.is_speaking = True

            # Run in thread
            t = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
            t.start()
        return True

    def _speak_thread(self, text):
        try:
            # 1. Synthesize & Stream
            if self.tts_model:
                logger.info(f"Synthesizing stream: {text[:30]}... (Voice: {self.current_voice})")
                
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
                
                logger.info("Playback finished.")
                
            else:
                # Mock simulation
                logger.info(f"Simulating TTS: {text}")
                for _ in range(3):
                    if self.stop_event.is_set(): break
                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"Speech error: {e}")
        finally:
            self.is_speaking = False
