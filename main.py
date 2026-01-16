import threading
from nicegui import ui
import interface.main  # Import to register the page layout
import os
import sys
import logging
from core.brain import Brain
# from core.settings import SYS_CONF_PATH # Removed as it's used in tray now
from core.logger import setup_logger
from interface.tray import setup_tray

logger = setup_logger("Main")

# ------------------- Global Exception & Warning Handling -------------------

def log_unhandled_exception(exc_type, exc_value, tb):
    """Log unhandled exceptions to our log file."""
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, tb))

# Set the global exception hook
sys.excepthook = log_unhandled_exception

# Redirect warnings to the logging system
logging.captureWarnings(True)
# Also log warnings to the console for visibility during development
warnings_logger = logging.getLogger('py.warnings')
warnings_logger.addHandler(logging.StreamHandler())

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Initial Health Check
    logger.info("🧠 Checking Brain Health...")
    brain = Brain()
    is_alive = brain.status_check()
    if is_alive:
        logger.info("✅ Brain is connected.")
    else:
        logger.warning("❌ Brain disconnected (Ollama not visible).")

    # Start tray in a separate thread
    setup_tray(is_alive)
    
    # Run UI
    # Browser Mode
    logger.info("🚀 Starting NiceGUI Server...")
    ui.run(native=False, title="Erika AI", reload=False, show=True)