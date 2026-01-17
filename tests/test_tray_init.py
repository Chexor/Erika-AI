import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTrayInit(unittest.TestCase):
    def test_tray_initialization(self):
        """Test that ErikaTray can be initialized with a callback."""
        # We need to mock pystray because we can't create actual icons in headless test environment reliably often
        # But for 'init' it might simple load image.
        
        # Check if module exists
        try:
            from interface.tray import ErikaTray
        except ImportError:
            self.fail("interface.tray module not found (RED)")

        # Test init
        mock_callback = MagicMock()
        
        # We assume ErikaTray uses pystray.Icon, blocking call? No, usually .run() is blocking.
        # We just want to init it.
        # We probably need to mock Image.open if assets missing
        
        with patch('interface.tray.Image') as mock_image, \
             patch('interface.tray.pystray.Icon') as mock_icon:
            
            tray = ErikaTray(shutdown_callback=mock_callback)
            self.assertIsNotNone(tray)
            self.assertEqual(tray.shutdown_callback, mock_callback)

if __name__ == '__main__':
    unittest.main()
