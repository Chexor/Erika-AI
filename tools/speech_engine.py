
import os
import time
import pygame
import threading
import logging
import uuid
import torch
import scipy.io.wavfile
import numpy as np

# Try importing the correct class from pocket_tts
try:
    from pocket_tts import TTSModel
except ImportError:
    TTSModel = None

logger = logging.getLogger("TOOLS.SpeechEngine")

class SpeechEngine:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), 'erika_home', 'temp')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Pygame Mixer
        try:
            pygame.mixer.init()
            logger.info("Pygame mixer initialized.")
        except Exception as e:
            logger.error(f"Failed to init pygame mixer: {e}")
            
        # Initialize TTS
        self.tts_model = None
        self.current_voice = 'azelma' # Default voice (Valid options: alba, marius, javert, jean, fantine, cosette, eponine, azelma)
        
        if TTSModel:
            try:
                logger.info("Loading PocketTTS Model (this may download weights)...")
                # Load default model
                self.tts_model = TTSModel.load_model()
                logger.info("PocketTTS Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to init TTSModel: {e}")
        else:
            logger.error("PocketTTS module not found. Audio will be simulated.")

    def set_voice(self, voice_name: str):
        """Sets the active voice for TTS."""
        if voice_name:
            self.current_voice = voice_name
            logger.info(f"Voice set to: {voice_name}")

    def speak(self, text: str):
        """Synthesizes text and plays audio asynchronously."""
        if not text:
            return False
        
        # Run in thread
        t = threading.Thread(target=self._speak_thread, args=(text,))
        t.start()
        return True

    def _speak_thread(self, text):
        filename = f"speech_{uuid.uuid4().hex}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # 1. Synthesize
            if self.tts_model:
                logger.info(f"Synthesizing: {text[:30]}... (Voice: {self.current_voice})")
                # Get conditioning state (voice)
                # We use a default pre-defined voice 'af'
                voice_state = self.tts_model.get_state_for_audio_prompt(self.current_voice)
                
                # Generate audio tensor [channels, samples]
                audio_tensor = self.tts_model.generate_audio(voice_state, text)
                
                # Convert to numpy for saving
                audio_np = audio_tensor.cpu().numpy()
                
                # Scipy expects (samples, channels) or (samples,)
                if audio_np.shape[0] == 1:
                    audio_np = audio_np.squeeze(0)
                else:
                    audio_np = audio_np.T
                    
                # Save to WAV
                scipy.io.wavfile.write(filepath, self.tts_model.sample_rate, audio_np)
                
            else:
                # Mock create file
                time.sleep(1) # Simulate generation
                # We need a dummy wav file to play? Or just skip play.
                logger.info(f"Simulated TTS: {text}")
                return

            # 2. Play
            if os.path.exists(filepath):
                logger.info(f"Playing audio: {filepath}")
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                
                # Block until finished
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
                # 3. Cleanup
                # Unload to release file lock
                pygame.mixer.music.unload()
                os.remove(filepath)
                logger.info("Playback finished and file removed.")
                
        except Exception as e:
            logger.error(f"Speech error: {e}")
            # Try cleanup
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
