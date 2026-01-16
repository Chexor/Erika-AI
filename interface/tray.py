"""interface/tray.py
System Tray integration for Erika AI.
"""
import sys
import os
import threading
import webbrowser
import pystray
from PIL import Image, ImageDraw
from nicegui import ui
from core.settings import SYS_CONF_PATH
from core.logger import setup_logger

logger = setup_logger("Tray")

def create_icon(color="blue"):
    # Try to load custom logo. 
    # Note: We assume this file is relative to the project root or we find it relative to this file.
    # __file__ is interface/tray.py. Project root is one level up.
    # Original code: os.path.join(os.path.dirname(__file__), 'assets', ...) in main.py
    # New code: We need to go up one level from 'interface' to get to root, then 'assets'.
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, 'assets', 'Erika-AI_logo2_transparant.png')
    
    if os.path.exists(logo_path):
        try:
            return Image.open(logo_path)
        except Exception as e:
            logger.error(f"Error loading logo: {e}")

    # Fallback: Create a simple 64x64 icon with dynamic color
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

def run_tray(initial_status: bool):
    """Internal function to run the tray icon, blocking."""
    logger.debug(f"Starting tray with status={initial_status}")
    color = "green" if initial_status else "red"
    
    # 'default=True' makes 'Open Erika' trigger on left-click
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

def setup_tray(initial_status: bool):
    """Starts the system tray in a separate daemon thread."""
    tray_thread = threading.Thread(target=run_tray, args=(initial_status,), daemon=True)
    tray_thread.start()
