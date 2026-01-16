import unittest
import os
import shutil
import logging
from core.logger import setup_logger

class TestCoreLogger(unittest.TestCase):
    def setUp(self):
        # Setup clean environment
        self.log_dir = os.path.join(os.getcwd(), 'logs')
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
        
    def tearDown(self):
        # Clean up handlers to release file locks
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            handler.close()
            
    def test_logger_initialization_and_file_creation(self):
        # Action
        logger = setup_logger("TEST_CORE")
        logger.info("Test log entry")
        
        # Verification 1: Directory Creation
        self.assertTrue(os.path.exists(self.log_dir), "Log directory was not created")
        
        # Verification 2: File Creation
        log_file = os.path.join(self.log_dir, "erika_debug.log")
        self.assertTrue(os.path.exists(log_file), "Log file was not created")
        
        # Verification 3: Content
        # We need to ensure the handler has flushed
        for handler in logger.handlers:
            handler.flush()
            
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn("TEST_CORE", content, "Log content missing logger name")
            self.assertIn("Test log entry", content, "Log content missing message")

if __name__ == '__main__':
    unittest.main()
