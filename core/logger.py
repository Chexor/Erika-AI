import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Constants
LOG_DIR = "logs"
LOG_FILE = "erika_debug.log"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5
FORMAT_STR = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a logger with console and file handlers."""
    
    # 1. Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(FORMAT_STR)

    # 2. File Handler (Rotating)
    file_path = os.path.join(LOG_DIR, LOG_FILE)
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=MAX_BYTES, 
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 3. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook to log unhandled crashes."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("CRASH_HANDLER")
    logger.critical("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

# Install Exception Hook
sys.excepthook = handle_exception
