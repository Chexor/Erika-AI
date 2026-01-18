import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import threading
import time

# Mock dependencies before importing SpeechEngine
sys.modules['sounddevice'] = MagicMock()
sys.modules['pocket_tts'] = MagicMock()

# Import target
from tools.speech_engine import SpeechEngine

class TestSpeechEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SpeechEngine()
        
        # Configure the mock TTS model to yield some chunks so the thread stays alive
        # providing time to assert is_speaking=True
        if self.engine.tts_model:
            def delayed_generator(*args, **kwargs):
                for _ in range(3):
                    time.sleep(0.1)
                    yield MagicMock()
            
            self.engine.tts_model.generate_audio_stream.side_effect = delayed_generator
        
    def tearDown(self):
        self.engine.stop()

    def test_speak_returns_true(self):
        """Test that speak returns True for valid text."""
        result = self.engine.speak("Hello World")
        self.assertTrue(result)
        self.assertTrue(self.engine.is_speaking)
        
    def test_speak_empty_returns_false(self):
        """Test that speak returns False for empty text."""
        result = self.engine.speak("")
        self.assertFalse(result)
        self.assertFalse(self.engine.is_speaking)

    def test_stop_sets_event(self):
        """Test that stop sets the threading event."""
        self.engine.is_speaking = True # Force state
        self.engine.start_wait = 0 # Hack to bypass wait loop for test
        self.engine.stop()
        self.assertTrue(self.engine.stop_event.is_set())

    def test_set_voice(self):
        """Test setting voice."""
        self.engine.set_voice("test_voice")
        self.assertEqual(self.engine.current_voice, "test_voice")

    def test_set_volume(self):
        """Test setting volume."""
        self.engine.set_volume(0.5)
        self.assertEqual(self.engine.volume, 0.5)
        
        # Test clamping
        self.engine.set_volume(1.5)
        self.assertEqual(self.engine.volume, 1.0)
        self.engine.set_volume(-0.5)
        self.assertEqual(self.engine.volume, 0.0)

if __name__ == '__main__':
    unittest.main()
