import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def configure_system_logging(log_dir="logs"):
    """
    Configures the logging system to route logs from different domains to separate files.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 1. Root Logger (Console Output Only)
    # We keep the root logger clean to avoid double logging if we propagate.
    # But usually, we want everything to eventually hit the console (or at least INFO+).
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) 
    
    # Clear existing handlers to prevent duplicates during reloads
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Domain Routing Map
    # Prefix -> Filename
    # If a logger starts with 'domain.memory', it goes to 'memory.log'
    domain_map = {
        "engine": "engine.log",
        "interface": "interface.log",
        "domain.memory": "memory.log",
        "domain.persona": "persona.log",
        "domain.subconscious": "subconscious.log",
        "infrastructure": "infrastructure.log",
        "application": "application.log"
    }

    # 3. Configure Specific Loggers
    # We attach FileHandlers to these parent loggers.
    # By default, propagate=True, so they also go to Console (Root).
    for namespace, filename in domain_map.items():
        logger = logging.getLogger(namespace)
        logger.setLevel(logging.DEBUG) # capture everything for file
        
        # Check if handler already exists to avoid duplication
        # (Naive check: if any FileHandler matches filename)
        has_file_handler = any(
            isinstance(h, RotatingFileHandler) and filename in h.baseFilename 
            for h in logger.handlers
        )
        
        if not has_file_handler:
            file_path = os.path.join(log_dir, filename)
            fh = RotatingFileHandler(
                file_path, 
                maxBytes=5*1024*1024, 
                backupCount=5, 
                encoding='utf-8'
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    # 4. Specialized: 'engine' often catches the root basics if not careful.
    # But with this setup, 'engine' namespace goes to 'engine.log'.
    # Any library logs (e.g. urllib3) go to Root -> Console only (no file), which is good.

    logging.info(f"System Logging Configured. Logs directory: {os.path.abspath(log_dir)}")
