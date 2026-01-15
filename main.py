import threading
import pystray
from PIL import Image, ImageDraw
from nicegui import ui
import interface.ui  # Import to register the page layout
import os
import sys
from core.brain import Brain

def create_icon(color="blue"):
    # Create a simple 64x64 icon with dynamic color
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

def on_open(icon, item):
    print("Opening...")
    # NiceGUI window is already open or managed by ui.run

def on_exit(icon, item):
    icon.stop()
    ui.shutdown()

def setup_tray(initial_status: bool):
    print(f"DEBUG: Starting tray with status={initial_status}")
    color = "green" if initial_status else "red"
    icon = pystray.Icon("Erika", create_icon(color), menu=pystray.Menu(
        pystray.MenuItem("Open Erika", on_open),
        pystray.MenuItem("Exit", on_exit)
    ))
    print("DEBUG: Tray icon created. Running icon loop...")
    icon.run()
    print("DEBUG: Tray icon loop ended.")

if __name__ == '__main__':
    # Initial Health Check
    print("🧠 Checking Brain Health...")
    brain = Brain()
    is_alive = brain.status_check()
    if is_alive:
        print("✅ Brain is connected.")
    else:
        print("❌ Brain disconnected (Ollama not visible).")

    # Start tray in a separate thread so NiceGUI can be main thread
    tray_thread = threading.Thread(target=setup_tray, args=(is_alive,), daemon=True)
    tray_thread.start()
    
    # Run UI
    # Native mode uses pywebview
    # switching to False for debugging
    ui.run(native=False, title="Erika AI", reload=False)
