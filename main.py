import threading
import pystray
from PIL import Image, ImageDraw
from nicegui import ui
import interface.ui  # Import to register the page layout
import os
import sys
from core.brain import Brain
from core.settings import SYS_CONF_PATH
from core.logger import setup_logger
import logging
import traceback

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


def create_icon(color="blue"):
    # Try to load custom logo
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'Erika-AI_logo2_transparant.png')
    if os.path.exists(logo_path):
        try:
            return Image.open(logo_path)
        except Exception as e:
            logger.error(f"Error loading logo: {e}")

    # Fallback: Create a simple 64x64 icon with dynamic color
    # color map
    colors = {
        "blue": (100, 200, 255),
        "green": (50, 200, 50),
        "red": (255, 50, 50)
    }
    fill_color = colors.get(color, colors["blue"])
    
    width = 64
    height = 64
    # Use RGBA
    image = Image.new('RGBA', (width, height), color=(255, 255, 255, 255))
    dc = ImageDraw.Draw(image)
    # Draw a rectangle/square in the middle
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=fill_color)
    return image

import webbrowser


def on_open(icon, item):
    logger.info("Tray: Opening UI...")
    # Open the browser to the NiceGUI app
    webbrowser.open('http://localhost:8080')

def on_settings(icon, item):
    logger.info("Tray: Settings clicked. Opening app...")
    webbrowser.open('http://localhost:8080')

def on_system_settings(icon, item):
    logger.info("Tray: Opening system config file...")
    try:
        os.startfile(SYS_CONF_PATH)
    except Exception as e:
        logger.error(f"Tray: Error opening config: {e}")

def on_restart(icon, item):
    logger.info("Tray: Restarting...")
    icon.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

def on_exit(icon, item):
    logger.info("Tray: Exiting...")
    icon.stop()
    ui.shutdown()

def setup_tray(initial_status: bool):
    logger.debug(f"Starting tray with status={initial_status}")
    color = "green" if initial_status else "red"
    
    # Menu Definition
    # 'default=True' makes 'Open Erika' trigger on left-click (Windows behavior varies, usually double-click)
    menu = pystray.Menu(
        pystray.MenuItem("Open Erika", on_open, default=True),
        pystray.MenuItem("Settings (UI)", on_settings),
        pystray.MenuItem("System Settings", on_system_settings),
        pystray.MenuItem("Restart", on_restart),
        pystray.MenuItem("Quit", on_exit)
    )

    icon = pystray.Icon("Erika", create_icon(color), menu=menu)
    logger.info("Tray icon created. Running icon loop...")
    icon.run()
    logger.debug("Tray icon loop ended.")

if __name__ == '__main__':
    # Initial Health Check
    logger.info("🧠 Checking Brain Health...")
    brain = Brain()
    is_alive = brain.status_check()
    if is_alive:
        logger.info("✅ Brain is connected.")
    else:
        logger.warning("❌ Brain disconnected (Ollama not visible).")

    # Start tray in a separate thread so NiceGUI can be main thread
    tray_thread = threading.Thread(target=setup_tray, args=(is_alive,), daemon=True)
    tray_thread.start()
    
    # Run UI
    # Browser Mode
    logger.info("🚀 Starting NiceGUI Server...")
    ui.run(native=False, title="Erika AI", reload=False, show=True)
