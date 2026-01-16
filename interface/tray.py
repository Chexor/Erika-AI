import os
import threading
import pystray
from PIL import Image
from pystray import MenuItem as item
import webbrowser
from core.logger import setup_logger

logger = setup_logger("INTERFACE.Tray")

class ErikaTray:
    def __init__(self, controller):
        self.controller = controller
        self.icon = None
        self.thread = None
        
        # Load Icon
        # Try assets first, generate fallback if missing
        icon_path = os.path.join("assets", "icon.png") # Or use the transparent logo
        if not os.path.exists(icon_path):
             icon_path = os.path.join("assets", "Erika-AI_logo2_transparant.png")
             
        try:
            self.image = Image.open(icon_path)
        except Exception as e:
            logger.error(f"Failed to load icon: {e}")
            # Fallback: Create simple block
            self.image = Image.new('RGB', (64, 64), color = (73, 109, 137))
            
        self.menu = pystray.Menu(
            item('Open WebUI', self.on_open, default=True),
            item('Quit', self.on_quit)
        )
        
        self.icon = pystray.Icon("Erika AI", self.image, "Erika AI", self.menu)

    def on_open(self, icon, item):
        logger.info("Tray: Opening WebUI...")
        webbrowser.open("http://localhost:8080")

    def on_quit(self, icon, item):
        logger.info("Tray: Quit requested")
        if self.icon:
            self.icon.stop()
        
        # Cleanup Controller if needed
        # self.controller.shutdown()
        
        logger.info("Tray: Exiting process...")
        os._exit(0) # Force exit

    def run(self):
        """Runs the tray icon in a separate thread."""
        logger.info("Starting System Tray...")
        self.thread = threading.Thread(target=self._run_icon, daemon=True)
        self.thread.start()

    def _run_icon(self):
        try:
            self.icon.run()
        except Exception as e:
            logger.error(f"Tray crashed: {e}")
