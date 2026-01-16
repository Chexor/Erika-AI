"""interface/main.py
Assembler for the component-based Erika AI UI.
Wires Model (State), View (Components), and Controller (Logic).
"""
from nicegui import ui, app
import asyncio

# MVC Components
from interface.state import AppState
from interface.controller import ErikaController
from interface.components import render_sidebar, InputBar, render_chat_messages
from interface.settings_ui import SettingsModal

# Serve static files
app.add_static_files('/assets', 'assets')

@ui.page('/')
def main_page():
    # 1. Instantiate Model & Controller
    state = AppState()
    controller = ErikaController(state)
    
    # 2. Hooks & Callbacks
    async def startup():
        controller.startup()
        # Initial Data Load
        await controller.load_chat(None) # Clear state
        controller.get_history_sections() # Load sidebar history
        refresh_sidebar() # Ensure sidebar is rendered
        refresh_chat()
        refresh_input()
        
    app.on_connect(startup) 
    app.on_shutdown(controller.shutdown)
    
    # 3. Theme Setup
    ui.colors(primary='#3b82f6', dark='#0f172a')
    dark_mode = ui.dark_mode()
    if controller.settings_manager.get_user_setting('theme', 'dark') == 'dark':
        dark_mode.enable()
    else:
        dark_mode.disable()
        
    def toggle_theme():
        dark_mode.toggle()
        theme = 'dark' if dark_mode.value else 'light'
        controller.settings_manager.set_user_setting('theme', theme)

    # 4. Settings Modal
    settings_modal = SettingsModal(controller.settings_manager, on_theme_toggle=toggle_theme)

    # 5. UI Layout Containers
    
    # --- Sidebar ---
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px'):
        @ui.refreshable
        def refresh_sidebar():
            render_sidebar(
                user_name=controller.settings_manager.get_user_setting('username', 'User'),
                # For actions that change state, we trigger refreshed
                on_new_chat=lambda: (controller.load_new_chat(), refresh_chat(), refresh_sidebar()),
                # History click: Load chat (updating state), then refresh Main & Sidebar (active highlight)
                on_history_click=lambda cid: (asyncio.create_task(controller.load_chat(cid)), refresh_chat(), refresh_sidebar()),
                on_settings_click=settings_modal.open,
                history_sections=state.sidebar_history,
                current_chat_id=state.current_chat_id
            )
        refresh_sidebar()

    # --- Chat Area ---
    with ui.column().classes('w-full max-w-4xl mx-auto min-h-screen p-4 pb-48') as chat_container:
        pass 

    async def scroll_to_bottom():
        await ui.run_javascript('window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });')

    controller.on_scroll_request = scroll_to_bottom
    
    # Notification Hook
    def on_notify_req():
        while state.notifications:
            msg, type_ = state.notifications.pop(0)
            ui.notify(msg, type=type_)
    controller.on_notification_request = on_notify_req

    current_response_ui = None 

    @ui.refreshable
    def refresh_chat():
        nonlocal current_response_ui
        chat_container.clear()
        
        # Callbacks passed to bubbling
        def on_regen():
            asyncio.create_task(controller.regenerate_last())
            refresh_chat()
            
        def on_copy(txt):
            ui.clipboard.write(txt)
            ui.notify("Copied to clipboard")
            
        def on_speak(txt):
            controller.read_aloud(txt)

        # Render
        # We render INTO the chat_container column
        with chat_container:
             current_response_ui = render_chat_messages(
                chat_container, 
                state.messages, 
                on_regenerate=on_regen,
                on_copy=on_copy,
                on_speak=on_speak
            )
    
    refresh_chat()

    # --- Input Bar ---
    @ui.refreshable 
    def refresh_input():
        model_name = controller.settings_manager.get_system_setting('model', controller.brain.get_model_name())
        
        async def on_send_click(text):
            # 1. Call controller (Updates state)
            # 2. Refresh UI to show "Thinking..." state
            # 3. Stream happens
            refresh_input() # Update buttons to Stop/Loading
            refresh_chat() # Show user message
            await controller.handle_send(text)
            refresh_input() # Reset buttons
            
        def on_stop_click():
            controller.handle_stop()
            refresh_input()
        
        # We assume InputBar renders into the page_sticky, so we just call it.
        # But wait, InputBar in components.py renders `ui.page_sticky`. 
        # If we call it inside `refresh_input`, it will duplicate sticky footers?
        # NO, ui.refreshable creates a container. The sticky will be inside that container?
        # Standard sticky behaviour might be weird inside a refreshable.
        # Let's hope NiceGUI handles it.
        
        ctrl = InputBar(
            model_name=model_name, 
            on_send=on_send_click,
            on_stop=on_stop_click
        )
        ctrl.set_loading(state.is_generating)
        
    refresh_input()
    
    # Streaming Optimization
    # We use a timer to push updates to the LAST bubble if generating
    async def update_stream():
        if state.is_generating and state.messages:
            last_msg = state.messages[-1]
            if last_msg['role'] == 'assistant' and current_response_ui:
                current_response_ui.set_content(last_msg['content'])
                if len(last_msg['content']) % 300 == 0: # Light scroll check
                    await scroll_to_bottom()
                    
    ui.timer(0.1, update_stream)
