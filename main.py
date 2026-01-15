import threading
import pystray
from PIL import Image, ImageDraw
from interface.ui import run_interface
import os
import webbrowser

def create_icon():
    # Create a simple icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(55, 55, 55))
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=(100, 200, 255))
    return image

def on_open(icon, item):
    print("Open clicked")
    # In native mode, the window is already managed by pywebview.
    # If we were in browser mode, we could do:
    # webbrowser.open('http://localhost:8080')
    pass

def on_exit(icon, item):
    icon.stop()
    # Force exit to kill NiceGUI/Uvicorn
    os._exit(0)

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
    print("Starting Erika UI...")
    run_interface()
