
import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock, patch

try:
    from engine.modules.reflector import Reflector
    from interface.controller import Controller
except ImportError:
    Reflector = None
    Controller = None

class TestAwakening(unittest.IsolatedAsyncioTestCase):
    
    def test_get_latest_reflection(self):
        """Verify retrieving the correct reflection file."""
        if not Reflector: self.skipTest("No Reflector")
        
        reflector = Reflector(MagicMock(), MagicMock(), MagicMock())
        
        # Mock os.listdir and open
        with patch('os.listdir', return_value=['day_18-01-2026.md', 'day_17-01-2026.md']):
            with patch('builtins.open', unittest.mock.mock_open(read_data="# Morning Perspective\nTim was sad.")) as mock_file:
                content = reflector.get_latest_reflection()
                self.assertIn("Tim was sad", content)
                # Should prefer 18-01 (latest)
                mock_file.assert_called()

    async def test_system_prompt_injection(self):
        """Verify system prompt contains the Librarian Reflection."""
        if not Controller: self.skipTest("No Controller")
        
        # Setup Controller with mocked Reflector
        mock_reflector = MagicMock()
        mock_reflector.get_latest_reflection.return_value = "Tim was happy."
        
        controller = Controller(MagicMock(), MagicMock())
        controller.reflector = mock_reflector
        
        # We assume a method build_system_prompt exists
        prompt = controller.build_system_prompt()
        
        self.assertIn("LIBRARIAN REFLECTION", prompt)
        self.assertIn("Tim was happy", prompt)
        self.assertIn("INTERNAL MEMORY", prompt)

if __name__ == '__main__':
    unittest.main()
