
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_DIR = "erika_home/logs"
LOG_FILE = "erika.log"
FULL_LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with rotating file handler and console handler.
    
    Args:
        name (str): The name of the logger (e.g., "Main", "Brain").
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers already exist to avoid duplicates
    if logger.handlers:
        return logger
        
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler (Rotating)
    # 5MB max size, 3 backups
    file_handler = RotatingFileHandler(
        FULL_LOG_PATH, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) # Clean console
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
