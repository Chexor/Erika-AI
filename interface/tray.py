import pystray
from pystray import MenuItem as item
from PIL import Image
import os
import threading
from engine.logger import setup_engine_logger

# Use Engine Logger for Tray as well
logger = setup_engine_logger("INTERFACE.Tray")

class ErikaTray:
    def __init__(self, shutdown_callback, on_show_callback=None, on_restart_callback=None, on_restart_agent_callback=None):
        self.shutdown_callback = shutdown_callback
        self.on_show_callback = on_show_callback
        self.on_restart_callback = on_restart_callback
        self.on_restart_agent_callback = on_restart_agent_callback
        self.icon = None
        
        # Load Icon
        self.image = self._load_icon()
        
        # Build Menu
        self.menu = pystray.Menu(
            item('Show Erika', self.on_show, default=True),
            item('Restart Window', self.on_restart),
            item('Restart Agent', self.on_restart_agent),
            item('Exit', self.on_exit)
        )
        
        self.icon = pystray.Icon("Erika AI", self.image, "Erika AI", self.menu)

    def _load_icon(self):
        """Loads icon from assets or generates fallback."""
        icon_path = os.path.join("assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception as e:
                logger.error(f"Failed to load icon file: {e}")
        
        # Fallback: Blue Square
        logger.info("Using fallback icon.")
        return Image.new('RGB', (64, 64), color=(73, 109, 137))

    def on_show(self, icon, item):
        """Handler for 'Show Erika'."""
        logger.info("Tray: User requested UI (Show Erika).")
        if self.on_show_callback:
            self.on_show_callback()

    def on_restart(self, icon, item):
        """Handler for 'Restart UI'."""
        logger.info("Tray: User requested UI Restart.")
        if self.on_restart_callback:
            self.on_restart_callback()

    def on_restart_agent(self, icon, item):
        """Handler for 'Restart Agent'."""
        logger.info("Tray: User requested Agent Restart.")
        if self.on_restart_agent_callback:
            self.on_restart_agent_callback()
        
    def on_exit(self, icon, item):
        """Handler for 'Exit'."""
        logger.info("Tray: Exit requested.")
        if self.icon:
            self.icon.stop()
            
        if self.shutdown_callback:
            logger.info("Tray: Triggering shutdown callback...")
            self.shutdown_callback()

    def run(self):
        """Blocking run call for the tray."""
        logger.info("Tray: Starting icon loop...")
        self.icon.run() 
