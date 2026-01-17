import unittest
import os
import sys
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We expect this import to fail initially or the class to not exist
try:
    from core.singleton import SingletonLock
except ImportError:
    SingletonLock = None

class TestSingletonLock(unittest.TestCase):
    def setUp(self):
        if SingletonLock:
            self.lock1 = SingletonLock()
            self.lock2 = SingletonLock()
        
    def tearDown(self):
        if SingletonLock:
            try:
                self.lock1.release()
            except:
                pass
            try:
                self.lock2.release()
            except:
                pass

    def test_double_acquire(self):
        """Test that acquiring the lock twice fails."""
        if not SingletonLock:
            self.fail("SingletonLock class not implemented yet (RED state verified)")
            
        # First acquire should succeed
        success1 = self.lock1.acquire()
        self.assertTrue(success1, "First lock acquisition should succeed")
        
        # Second acquire should fail
        # Note: In a real scenario, this would be a separate process. 
        # But for msvcrt locking on the SAME file from the SAME process, 
        # behavior depends on implementation (file handle sharing).
        # To truly test "Single Instance", we usually need separate processes.
        # BUT, if we implement it such that we hold a file handle, 
        # trying to open it again in exclusive mode might fail even in same process
        # or we mock the file locking.
        
        # Let's assume we want to verify the API contract first.
        # If we can't test separate process easily in unittest without subprocess,
        # we will rely on integration test or just checking the logic.
        
        # However, for the purpose of the "RED" test step requested by user:
        # "The test must attempt to instantiate a SingletonLock twice."
        # "It must verify that the second attempt raises a ProcessLookupError or returns False."
        
        success2 = False
        try:
            success2 = self.lock2.acquire()
        except (ProcessLookupError, IOError, BlockingIOError):
            success2 = False
            
        self.assertFalse(success2, "Second lock acquisition should fail")

if __name__ == '__main__':
    unittest.main()
