import asyncio
import threading
import sys
import atexit
import subprocess
import os
from nicegui import ui, app

from engine.logger import setup_engine_logger
from engine.singleton import WindowsSingleton
from engine.brain import Brain
from engine.memory import Memory
from interface.tray import ErikaTray
from interface.controller import Controller
from interface.view import build_ui

# Setup Global Logger
logger = setup_engine_logger("ENGINE")

# Global State
lock = None
tray = None
brain = None
memory = None
controller = None
shutting_down = False
window_process = None
UI_PORT = 3333

def cleanup():
    """Cleanup handler."""
    global lock, shutting_down, window_process
    if shutting_down:
        return
    shutting_down = True
    
    logger.info("Engine: Cleanup initiated.")
    try:
        if tray and tray.icon:
            tray.icon.stop()
    except Exception:
        pass
    
    # Kill window process if active
    if window_process:
        try:
            window_process.terminate()
            logger.info("Engine: Window process terminated.")
        except Exception:
            pass

    if lock:
        try:
            lock.release()
            logger.info("Engine: Lock released.")
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            
    logger.info("Engine: Graceful Shutdown.")
    # Force exit to kill any hanging threads and avoid SystemExit exception in pystray
    os._exit(0)

def spawn_window():
    """Spawns the detached window client."""
    global window_process
    
    # Check if already running
    if window_process and window_process.poll() is None:
        logger.info("Engine: Window already active.")
        return

    logger.info("Engine: Spawning UI Window...")
    script_path = os.path.join(os.path.dirname(__file__), 'interface', 'window_client.py')
    url = f"http://localhost:{UI_PORT}"
    
    # Use same python interpreter
    python_exe = sys.executable
    
    try:
        # Popen is non-blocking
        window_process = subprocess.Popen([python_exe, script_path, "--url", url, "--title", "Erika AI"])
        logger.info(f"Engine: Window spawned (PID: {window_process.pid})")
    except Exception as e:
        logger.error(f"Engine: Failed to spawn window: {e}")

def start_tray_thread(shutdown_cb):
    """Starts the tray icon in a separate thread."""
    global tray
    
    # This runs in a thread, so it can call spawn_window directly (subprocess is thread-safe)
    def on_show_request():
        spawn_window()

    tray = ErikaTray(shutdown_callback=shutdown_cb, on_show_callback=on_show_request)
    tray.run()

def main():
    global lock, tray, brain, memory, controller
    
    logger.info("Engine: Bootstrapping Service...")
    
    # 1. Acquire Lock
    lock = WindowsSingleton()
    if not lock.acquire():
        logger.warning("Engine: Instance already active, exiting.")
        sys.exit(0)
    
    logger.info("Engine: Singleton lock acquired.")
    
    # 2. Init Core Components
    logger.info("Engine: Initializing Brain & Memory...")
    memory = Memory()
    brain = Brain()
    controller = Controller(brain, memory)
    
    # 3. Build UI
    @ui.page('/')
    def main_page():
        build_ui(controller)
        # Load history on page load
        if controller.current_chat_id:
             asyncio.create_task(controller.load_chat_session(controller.current_chat_id))
        else:
             asyncio.create_task(controller.load_history())

    # 4. Start Tray in Background Thread
    # Pass cleanup as shutdown callback. 
    # NOTE: nicegui app.shutdown only stops the server. We want FULL process cleanup.
    # So tray exit -> cleanup() -> sys.exit().
    t = threading.Thread(target=start_tray_thread, args=(cleanup,), daemon=True)
    t.start()
    
    # Register NiceGUI shutdown hook to cleanup if server stops naturally
    app.on_shutdown(cleanup)

    # 6. Run Server using Uvicorn (Blocking)
    logger.info(f"Engine: Starting Server at port {UI_PORT}...")
    # native=False -> Browser Mode (Server only)
    # show=False -> Don't open system browser
    # reload=False
    try:
        ui.run(native=False, port=UI_PORT, show=False, reload=False, title="Erika AI")
    except Exception as e:
        logger.error(f"Engine: Server crashed: {e}")
        cleanup()

if __name__ == "__main__":
    main()
