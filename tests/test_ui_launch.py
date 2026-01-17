import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestUILaunch(unittest.TestCase):
    def test_view_structure(self):
        """Test that View builder functions exist."""
        try:
            import interface.view as view
        except ImportError:
            self.fail("interface.view module not found (RED)")
            
        self.assertTrue(hasattr(view, 'build_ui'), "View should have build_ui function")

if __name__ == '__main__':
    unittest.main()
