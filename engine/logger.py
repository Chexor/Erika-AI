import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_engine_logger(name="ENGINE"):
    """
    Sets up a robust logger that captures stderr/stdout and logs to file/console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File Handler
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    fh = RotatingFileHandler(
        os.path.join(log_dir, "erika_engine.log"), 
        maxBytes=5*1024*1024, 
        backupCount=5,
        encoding='utf-8' # Good practice
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger
