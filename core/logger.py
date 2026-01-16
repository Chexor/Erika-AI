
import logging
import os
import sys
import asyncio
import traceback
from logging.handlers import RotatingFileHandler

LOG_DIR = "erika_home/logs"
LOG_FILE = "erika_debug.log"
FULL_LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with rotating file handler and console handler.
    """
    # Create directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers already exist to avoid duplicates
    if logger.handlers:
        return logger
        
    logger.propagate = False
    
    # File Handler (Rotating)
    # 5MB max size, 5 backups, utf-8
    file_handler = RotatingFileHandler(
        FULL_LOG_PATH, 
        maxBytes=5*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(FORMATTER)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Clean console
    console_handler.setFormatter(FORMATTER)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ---------------------------------------------------------------------
# Global Crash Handlers
# ---------------------------------------------------------------------

def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler for unhandled exceptions.
    Ignores KeyboardInterrupt to allow clean exit.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    root_logger = logging.getLogger("Root")
    if not root_logger.handlers:
        setup_logger("Root")
        
    root_logger.critical(
        "Uncaught exception", 
        exc_info=(exc_type, exc_value, exc_traceback)
    )

def handle_async_exception(loop, context):
    """
    Global exception handler for asyncio loops.
    """
    msg = context.get("message", "")
    exception = context.get("exception")
    
    root_logger = logging.getLogger("AsyncRoot")
    if not root_logger.handlers:
        setup_logger("AsyncRoot")
        
    if exception:
        root_logger.critical(f"Async Uncaught exception: {msg}", exc_info=exception)
    else:
        root_logger.critical(f"Async Uncaught exception: {msg}")

# Apply the global exception hook immediately
sys.excepthook = handle_exception
