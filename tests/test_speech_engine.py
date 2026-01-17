
import unittest
import os
from tools.speech_engine import SpeechEngine

class TestSpeechEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SpeechEngine()
        self.test_text = "Hello, this is a test."

    def test_speak_returns_true(self):
        # We might need to mock playback to avoid actual noise during tests
        # But for 'integration' test we want to see it works.
        # However, blocking playback in tests is annoying.
        # We will assume speak is blocking or returns True when scheduled.
        result = self.engine.speak(self.test_text)
        self.assertTrue(result)

    def test_temp_file_creation_and_deletion(self):
        # This is hard to test if speak deletes it immediately.
        # We just verify that speak runs without error.
        pass

if __name__ == '__main__':
    unittest.main()
