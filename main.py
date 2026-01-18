import os
# Force Offline Mode for Hugging Face
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import asyncio
import threading
import sys
import subprocess
from nicegui import ui, app

import logging
from engine.logger import configure_system_logging
from engine.singleton import WindowsSingleton
from engine.brain import Brain
from engine.memory import Memory
from interface.tray import ErikaTray
from interface.controller import Controller
from interface.view import build_ui

# Setup Global Logger
configure_system_logging()
logger = logging.getLogger("engine")

# Global State with Thread Safety
_state_lock = threading.Lock()
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
    global lock, shutting_down, window_process, controller

    with _state_lock:
        if shutting_down:
            return
        shutting_down = True

    logger.info("Engine: Cleanup initiated.")

    # Stop System Monitor
    if controller and hasattr(controller, 'system_monitor'):
        try:
            controller.system_monitor.stop()
        except (RuntimeError, AttributeError) as e:
            logger.warning(f"Error stopping system monitor: {e}")

    try:
        if tray and tray.icon:
            tray.icon.stop()
    except (RuntimeError, AttributeError) as e:
        logger.warning(f"Error stopping tray: {e}")

    # Kill window process if active
    if window_process:
        try:
            window_process.terminate()
            logger.info("Engine: Window process terminated.")
        except (OSError, ProcessLookupError) as e:
            logger.warning(f"Error terminating window process: {e}")

    if lock:
        try:
            lock.release()
            logger.info("Engine: Lock released.")
        except (IOError, OSError) as e:
            logger.error(f"Error releasing lock: {e}")

    logger.info("Engine: Graceful Shutdown.")
    # Force exit to kill any hanging threads and avoid SystemExit exception in pystray
    os._exit(0)

def spawn_window():
    """Spawns the detached window client."""
    global window_process

    with _state_lock:
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
        except (OSError, subprocess.SubprocessError) as e:
            logger.error(f"Engine: Failed to spawn window: {e}")

def restart_window():
    """Restarts the window process."""
    global window_process
    logger.info("Engine: Restarting UI Window...")

    with _state_lock:
        if window_process:
            try:
                window_process.terminate()
                # Give it a moment to die gracefully
                try:
                    window_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    window_process.kill()
            except (OSError, ProcessLookupError) as e:
                logger.error(f"Engine: Error killing window: {e}")
            window_process = None

    spawn_window()

def restart_agent():
    """Restarts the entire agent process."""
    global lock, tray, window_process
    logger.info("Engine: Restarting Agent (Full Process)...")

    # 1. Kill Window
    if window_process:
        try:
            window_process.terminate()
        except (OSError, ProcessLookupError) as e:
            logger.warning(f"Engine: Error terminating window for restart: {e}")

    # 2. Stop Tray (Important to remove icon)
    if tray and tray.icon:
        try:
            tray.icon.stop()
        except (RuntimeError, AttributeError) as e:
            logger.warning(f"Engine: Error stopping tray for restart: {e}")

    # 3. Release Lock
    if lock:
        try:
            lock.release()
            logger.info("Engine: Lock released for restart.")
        except (IOError, OSError) as e:
            logger.error(f"Engine: Error releasing lock: {e}")

    # 4. Restart Process - use explicit script path instead of sys.argv for security
    python = sys.executable
    script_path = os.path.abspath(__file__)
    os.execl(python, python, script_path)

def start_tray_thread(shutdown_cb, restart_cb, restart_agent_cb):
    """Starts the tray icon in a separate thread."""
    global tray
    
    # This runs in a thread, so it can call spawn_window directly (subprocess is thread-safe)
    def on_show_request():
        spawn_window()

    tray = ErikaTray(
        shutdown_callback=shutdown_cb, 
        on_show_callback=on_show_request,
        on_restart_callback=restart_cb,
        on_restart_agent_callback=restart_agent_cb
    )
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
    logger.info("Engine: System Monitor Active.")
    
    # 3. Build UI
    app.add_static_files('/assets', 'assets')
    @ui.page('/')
    def main_page():
        build_ui(controller)
        # Load history on page load
        if controller.current_chat_id:
             asyncio.create_task(controller.load_chat_session(controller.current_chat_id))
        else:
             asyncio.create_task(controller.load_history())

    # 4. Start Tray in Background Thread
    # Pass cleanup as shutdown callback and restart_window as restart callback.
    # NOTE: nicegui app.shutdown only stops the server. We want FULL process cleanup.
    # So tray exit -> cleanup() -> sys.exit().
    t = threading.Thread(target=start_tray_thread, args=(cleanup, restart_window, restart_agent), daemon=True)
    t.start()
    
    # Register NiceGUI shutdown hook to cleanup if server stops naturally
    app.on_shutdown(cleanup)
    
    # 5. Auto-Launch UI on Startup
    app.on_startup(spawn_window)

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
