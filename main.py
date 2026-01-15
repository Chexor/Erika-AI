import threading
import pystray
from PIL import Image, ImageDraw
from nicegui import ui
import interface.ui  # Import to register the page layout
import os
import sys

def create_icon():
    # Create a simple 64x64 blue icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(55, 55, 55))
    dc = ImageDraw.Draw(image)
    # Draw a blue rectangle/square in the middle
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=(0, 0, 255))
    return image

def on_open(icon, item):
    print("Opening...")
    # NiceGUI window is already open or managed by ui.run

def on_exit(icon, item):
    icon.stop()
    ui.shutdown()

def setup_tray():
    icon = pystray.Icon("Erika", create_icon(), menu=pystray.Menu(
        pystray.MenuItem("Open Erika", on_open),
        pystray.MenuItem("Exit", on_exit)
    ))
    icon.run()

if __name__ == '__main__':
    # Start tray in a separate thread so NiceGUI can be main thread
    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()
    
    # Run UI
    # Native mode uses pywebview
    ui.run(native=True, title="Erika AI", reload=False)
