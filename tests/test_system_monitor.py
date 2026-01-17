import unittest
import sys
import os
import time

# Add project root to path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.modules.system_monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SystemMonitor(interval=1)

    def test_get_stats_returns_dict(self):
        """Verify that get_stats returns a dictionary with the expected keys."""
        # Allow some time for background thread (if any) or just call update manually if needed
        # Assuming get_stats() triggers a read or returns last read
        self.monitor.update_stats() 
        stats = self.monitor.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('cpu', stats)
        self.assertIn('ram', stats)
        self.assertIn('gpu', stats)
        self.assertIn('vram', stats)
        
        self.assertIsInstance(stats['cpu'], float)
        self.assertIsInstance(stats['ram'], float)
        # GPU/VRAM might be None if no GPU, but requirement says "float" or fallback
        # Let's assume they should be floats (0.0 if not present) or handle None
        
    def test_values_are_reasonable(self):
        """Verify that the values are within 0-100 range."""
        self.monitor.update_stats()
        stats = self.monitor.get_stats()
        
        self.assertTrue(0.0 <= stats['cpu'] <= 100.0)
        self.assertTrue(0.0 <= stats['ram'] <= 100.0)
        if stats['gpu'] is not None:
             self.assertTrue(0.0 <= stats['gpu'] <= 100.0)

if __name__ == '__main__':
    unittest.main()
