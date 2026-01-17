import unittest
from unittest.mock import MagicMock, patch
import threading
import time

# We don't have interface.tray yet, so this import will fail (RED)
# simulating the import error or verifying logic once it exists.
try:
    from interface.tray import ErikaTray
except ImportError:
    ErikaTray = None

class TestTray(unittest.TestCase):
    def setUp(self):
        self.mock_controller = MagicMock()
        # Mocking shutdown method
        self.mock_controller.shutdown = MagicMock()

    def test_import_exists(self):
        """Verify ErikaTray class exists."""
        self.assertIsNotNone(ErikaTray, "ErikaTray class not found in interface.tray")

    @patch('interface.tray.pystray.Icon')
    @patch('interface.tray.Image.open')
    def test_initialization(self, mock_img_open, mock_icon):
        """Verify tray initializes with icon and menu."""
        if ErikaTray is None: self.fail("ErikaTray not imported")
        
        tray = ErikaTray(self.mock_controller)
        
        # Check image loading
        mock_img_open.assert_called()
        
        # Check icon creation
        mock_icon.assert_called()
        
    @patch('interface.tray.sys.exit')
    def test_quit_action(self, mock_exit):
        """Verify quit menu item triggers shutdown."""
        if ErikaTray is None: self.fail("ErikaTray not imported")

        tray = ErikaTray(self.mock_controller)
        
        # Simulate quit action
        tray.on_quit(None)
        
        # Controller shutdown should be called
        # self.mock_controller.shutdown.assert_called() # If we add shutdown to controller
        
        # Or at least sys.exit or stop logic
        # For this test, we assume tray handles the exit call.
        mock_exit.assert_called()

if __name__ == '__main__':
    unittest.main()
