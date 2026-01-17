import os
import sys
import logging
import warnings
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

class StderrWrapper:
    """Redirects stderr to logger while keeping original stderr."""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.logger = logging.getLogger("STDERR")

    def write(self, message):
        if message.strip():
            self.logger.warning(message.rstrip())
        self.original_stderr.write(message)

    def flush(self):
        self.original_stderr.flush()

def setup_global_capture():
    """Redirects warnings and external logs to our file."""
    # 1. Capture Python Warnings
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    
    # 2. Capture Stderr
    if not isinstance(sys.stderr, StderrWrapper):
        sys.stderr = StderrWrapper(sys.stderr)
    
    # 3. Attach file handler to Root and Libs
    file_path = os.path.join(LOG_DIR, LOG_FILE)
    formatter = logging.Formatter(FORMAT_STR)
    handler = RotatingFileHandler(file_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    handler.setFormatter(formatter)
    
    # Attach to root logger
    root_log = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root_log.handlers):
        root_log.addHandler(handler)
        root_log.setLevel(logging.DEBUG)

    # Propagate libs
    for lib in ["uvicorn", "uvicorn.error", "uvicorn.access", "nicegui", "watchfiles"]:
        logging.getLogger(lib).propagate = True

    # Silence noisy libraries
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)



def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception hook to log unhandled crashes."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("CRASH_HANDLER")
    logger.critical("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

# Install Exception Hook
sys.excepthook = handle_exception
