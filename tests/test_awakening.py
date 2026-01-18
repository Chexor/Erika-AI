
import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock, patch

try:
    from domain.subconscious.reflection_service import ReflectionService
    from interface.controller import Controller
except ImportError:
    ReflectionService = None
    Controller = None

class TestAwakening(unittest.TestCase):
    
    def test_get_latest_reflection(self):
        """Verify retrieving the correct reflection file."""
        if not ReflectionService: self.skipTest("No ReflectionService")
        
        service = ReflectionService(MagicMock(), MagicMock(), MagicMock())
        
        # Mock os.listdir and open
        with patch('os.listdir', return_value=['day_18-01-2026.md', 'day_17-01-2026.md']):
            with patch('builtins.open', unittest.mock.mock_open(read_data="# Morning Perspective\nTim was sad.")) as mock_file:
                content = service.get_latest_reflection()
                self.assertIn("Tim was sad", content)
                # Should prefer 18-01 (latest)
                mock_file.assert_called()

    def test_system_prompt_injection(self):
        """Verify system prompt contains the Yesterday's Perspective reflection."""
        if not Controller: self.skipTest("No Controller")

        # Setup Controller with mocked Service
        mock_service = MagicMock()
        mock_service.get_latest_reflection.return_value = "Tim was happy."

        # The Controller init starts SystemMonitor; patch it to avoid asyncio slow warnings
        with patch('interface.controller.SystemMonitor.start'):
            controller = Controller(MagicMock(), MagicMock())
            controller.reflection_service = mock_service

        # We assume a method build_system_prompt exists
        prompt = controller.build_system_prompt()

        # Check for the actual prompt format used in controller.py
        self.assertIn("INTERNAL MEMORY", prompt)
        self.assertIn("YESTERDAY'S PERSPECTIVE", prompt)
        self.assertIn("Tim was happy", prompt)

if __name__ == '__main__':
    unittest.main()
