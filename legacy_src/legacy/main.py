from nicegui import ui, app
from typing import Optional

# Architecture Imports
from interface.state import AppState
from interface.controller import ErikaController
from interface.components import Sidebar, HeroSection, ChatArea, InputPill
from core.logger import setup_logger, setup_global_capture

logger = setup_logger("ASSEMBLER.Main")

def init_app():
    # 1. Initialize Core & State
    state = AppState()
    controller = ErikaController(state)
    
    return state, controller

def force_silence_logs():
    import logging
    # Force silence again after NiceGUI/Uvicorn startup
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logger.info("Enforced log silencing.")

    logger.info("Enforced log silencing.")

from core.singleton import SingletonLock
import sys

# 5. Global State Holders (for lifecycle access)
tray: Optional['ErikaTray'] = None
active_controllers: list[ErikaController] = []
singleton_lock = SingletonLock()

async def startup():
    """Application startup hook."""
    # 0. Gatekeeper: Singleton Lock
    if not singleton_lock.acquire():
        logger.error("Erika is already running. Exiting.")
        # Ensure we don't start the UI or Tray
        # If ui.run is already passed, we need to kill the process
        print("Erika is already running. Please close the existing instance.")
        app.shutdown() 
        sys.exit(0)
    
    logger.info("Initializing Core Services...")
    
    # Initialize Core Managers explicitly if needed, but Controller handles it.
    # We could pre-warm models here.
    
    # Initialize Tray
    global tray
    # We need a way to stop the app from the tray.
    # Since ui.run() blocks, we can't easily pass 'app.shutdown'.
    # But checking docs, app.shutdown() is available.
    def shutdown_app():
        logger.info("Shutdown requested via Tray.")
        app.shutdown() 

    tray = ErikaTray(shutdown_callback=shutdown_app)
    tray.run()
    
    # Background logic to hook the native window once created
    import asyncio
    import webview
    
    async def hook_native_window():
        logger.info("Background Hook: Started waiting for native window...")
        attempts = 0
        
        # Wait for pywebview to actually initialize the window list
        while len(webview.windows) == 0:
            if attempts % 10 == 0:
                logger.info(f"Background Hook: Waiting for webview.windows... (Attempt {attempts})")
            await asyncio.sleep(0.5)
            attempts += 1
            if attempts > 60: # 30 seconds
                 logger.warning("Background Hook: Timed out waiting for webview window!")
                 return
        
        # Access the real pywebview window (not NiceGUI's proxy)
        window = webview.windows[0] 
        logger.info(f"Native window captured (Real): {window}")
        tray.window = window

        # Hook Closing Event to Minimize/Hide
        def on_closing():
            logger.info("UI Detached: Window close requested. Hiding window.")
            try:
                window.hide()
            except Exception as e:
                logger.error(f"Error hiding window: {e}")
            return False # Prevent actual closing
            
        # Hook into pywebview events
        try:
            # window.events.closing is a standard pywebview event
            window.events.closing += on_closing
            logger.info("Window closing event hooked successfully.")
        except Exception as e:
             logger.error(f"Failed to hook window events: {e}")
        
    # Schedule the hook
    asyncio.create_task(hook_native_window())

async def shutdown():
    """Application shutdown hook."""
    logger.info("Graceful shutdown initiated...")
    
    # Release Lock
    try:
        singleton_lock.release()
    except Exception as e:
        # On Windows, sometimes releasing a locked file fails if still open/locked.
        # Safe to ignore on shutdown as OS cleans up.
        logger.warning(f"Note: Error releasing singleton lock (expected on Windows): {e}")

    # Stop Tray
    global tray
    if tray:
        tray.stop()
        logger.info("Tray stopped.")
        
    # Cleanup Controllers
    for c in active_controllers:
        try:
            c.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up controller: {e}")
            
    logger.info("Shutdown complete.")

app.on_startup(force_silence_logs)
app.on_startup(startup)
app.on_shutdown(shutdown)

app.add_static_files('/assets', 'assets')

@ui.page('/')
async def main_page():
    # 2. Setup Page Context
    ui.colors(primary='#f3f4f6', secondary='#262626', accent='#111b21', dark='#1d1d1d')
    ui.query('body').classes('bg-[#212121] text-white p-0 m-0') 
    ui.query('.q-page').classes('flex flex-col h-screen w-full p-0 m-0 overflow-hidden') # FORCE no padding, no scroll on page root
    
    # Init App & Track Controller
    state, controller = init_app()
    active_controllers.append(controller)
    
    # Pre-load Data
    await controller.load_all_chats()

    # 4. Layout
    
    # Left Sidebar 
    # Sidebar returns the refreshable component function for the history list
    history_list_refresher = Sidebar(
        history=state.sidebar_history, 
        on_select=controller.load_chat, 
        on_new=controller.handle_new_chat,
        on_settings=lambda: ui.notify("Settings clicked")
    )

    # 3. Define UI Refresh Logic (Moved down to capture history_list_refresher)
    async def update_ui():
        """Refreshes reactive components."""
        chat_container.refresh()
        # Refresh the history list with new data
        history_list_refresher.refresh(state.sidebar_history, controller.load_chat)

    # Hook Controller to UI
    controller.refresh_ui = update_ui

    # Main Content Area - constrained to screen height, NO overflow on parent
    with ui.column().classes('w-full h-screen relative p-0 m-0 gap-0 overflow-hidden'):
        
        # Chat History / Hero (Refreshable)
        @ui.refreshable
        def chat_container():
            # Use flex-grow to take available space. overflow-y-auto to scroll THIS container, not the page.
            # pb-32 to allow scrolling past the fixed input pill.
            with ui.column().classes('w-full h-full overflow-y-auto pb-32 no-scrollbar'):
                if not state.messages:
                    HeroSection()
                else:
                    ChatArea(state.messages)
                    
                    if state.is_loading:
                        # Loading Indicator
                        with ui.row().classes('w-full justify-start px-4'):
                             ui.spinner('dots', size='lg', color='gray')

        chat_container()

        # Input Area (Fixed Bottom)
        # We perform a check to ensure dependencies are loaded
        valid_models = controller.brain.get_available_models()
        valid_models = valid_models if valid_models else ["No Models Found"]
        
        with ui.column().classes('absolute bottom-0 w-full items-center z-20 pointer-events-none'):
             # InputPill needs wrapper to re-enable pointer events since parent disables them (to let clicks pass through to chat)
             with ui.column().classes('w-full items-center pointer-events-auto'):
                InputPill(
                    models=valid_models,
                    on_send=controller.handle_send, # Mapped to controller
                    on_tool_toggle=lambda: ui.notify("Upload/Tools")
                )

from interface.tray import ErikaTray

# 5. Launch
if __name__ in {"__main__", "__mp_main__"}:
    setup_global_capture()
    logger.info("Starting Erika-AI Interface...")
    
    # Note: native=True requires pywebview. If missing, NiceGUI might warn or fail gracefully.
    # We use a try-block for safety if we wanted, but ui.run doesn't throw easily.
    # We enable native mode as requested.
    ui.run(
        title="Erika AI",
        dark=True,
        reload=False,
        native=True,
        window_size=(1200, 800),
        frameless=False
    )
