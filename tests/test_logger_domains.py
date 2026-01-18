import logging
import shutil
import os
import time
import logging
import shutil
import os
import time
from engine.logger import configure_system_logging

# Start fresh for tests
TEST_LOG_DIR = "test_logs"

def setup_module():
    if os.path.exists(TEST_LOG_DIR):
        shutil.rmtree(TEST_LOG_DIR)
    os.makedirs(TEST_LOG_DIR)

def test_domain_log_separation():
    # 1. Configure Logging with test directory
    # Note: We need to modify the logger to accept a log_dir arg for TDD to work cleanly without enforcing side effects on production logs
    configure_system_logging(log_dir=TEST_LOG_DIR)
    
    # 2. Log to different domains
    mem_logger = logging.getLogger("domain.memory")
    ui_logger = logging.getLogger("interface.view")
    persona_logger = logging.getLogger("domain.persona")
    
    mem_logger.info("Memory Test Message")
    ui_logger.info("UI Test Message")
    persona_logger.info("Persona Test Message")
    
    # Allow flush
    logging.shutdown()
    
    # 3. Verify Files exist and contain content
    assert os.path.exists(os.path.join(TEST_LOG_DIR, "memory.log")), "memory.log should be created"
    assert os.path.exists(os.path.join(TEST_LOG_DIR, "interface.log")), "interface.log should be created"
    
    with open(os.path.join(TEST_LOG_DIR, "memory.log"), "r") as f:
        content = f.read()
        assert "Memory Test Message" in content
        assert "UI Test Message" not in content
        
    with open(os.path.join(TEST_LOG_DIR, "interface.log"), "r") as f:
        content = f.read()
        assert "UI Test Message" in content
        assert "Memory Test Message" not in content

if __name__ == "__main__":
    try:
        setup_module()
        test_domain_log_separation()
        print("Test Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")
