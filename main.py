from nicegui import ui, app

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

app.on_startup(force_silence_logs)
app.add_static_files('/assets', 'assets')

@ui.page('/')
def main_page():
    # 2. Setup Page Context
    ui.colors(primary='#f3f4f6', secondary='#262626', accent='#111b21', dark='#1d1d1d')
    ui.query('body').classes('bg-[#212121] text-white p-0 m-0') 
    ui.query('.q-page').classes('flex flex-col h-screen w-full p-0 m-0 overflow-hidden') # FORCE no padding, no scroll on page root
    
    state, controller = init_app()

    # 3. Define UI Refresh Logic
    async def update_ui():
        """Refreshes reactive components."""
        chat_container.refresh()
        # Scroll logic might be needed here

    # Hook Controller to UI
    controller.refresh_ui = update_ui

    # 4. Layout
    
    # Left Sidebar
    Sidebar(
        history=controller.memory.list_all_chats(), 
        on_select=lambda chat_id: print(f"Select {chat_id}"), 
        on_new=controller.handle_new_chat,
        on_settings=lambda: ui.notify("Settings clicked")
    )

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
    
    # Initialize Tray (needs to access controller? For now, we instantiate a dummy or hook later)
    # Ideally, tray needs access to the main controller or app state if it wants to control it.
    # But main_page() creates controller lazily per-client.
    # We will pass None or a global shutdown hook for now.
    
    tray = ErikaTray(controller=None) 
    tray.run()
    
    ui.run(title="Erika AI", dark=True, reload=False)
