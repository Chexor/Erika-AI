"""interface/main.py
Assembler for the component-based Erika AI UI.
"""
from nicegui import ui, app
from interface.manager import ChatController
from interface.components import render_sidebar, InputBar, render_chat_messages
from interface.settings_ui import SettingsModal
import asyncio

# ---------------------------------------------------------------------
# Main Page Layout
# ---------------------------------------------------------------------

# Serve static files for assets (logo, avatars)
# We assume 'assets' folder is in the project root (relative to running directory)
app.add_static_files('/assets', 'assets')

@ui.page('/')
def main_page():
    
    # Instantiate Controller per-session (per-tab)
    controller = ChatController()
    
    # Theme handling
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

    # Shared Settings Modal
    settings_modal = SettingsModal(controller.settings_manager, on_theme_toggle=toggle_theme)

    # ---------------------------------------------------------
    # UI Elements & Containers
    # ---------------------------------------------------------

    # 1. Sidebar Drawer
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px') as left_drawer:
        drawer_content = ui.column().classes('w-full')

    # 2. Main Chat Area
    with ui.column().classes('w-full max-w-4xl mx-auto min-h-screen p-4 pb-48') as chat_container:
        pass # Will be populated by render_chat

    # 3. Input Bar
    model_name = controller.settings_manager.get_system_setting('model', controller.brain.get_model_name())
    # We define input bar here but it will be rendered sticky at bottom
    # We need to bind the on_send to controller.send_message
    
    async def handle_send(text):
        await controller.send_message(text)

    # Note: InputBar renders itself into a ui.page_sticky, so just calling it is enough
    input_control = InputBar(
        model_name=model_name,
        on_send=handle_send, 
        on_stop=controller.stop_generation,
    )

    # ---------------------------------------------------------
    # Render Logic
    # ---------------------------------------------------------

    async def scroll_to_bottom():
        await ui.run_javascript('window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });')

    async def render_sidebar_content():
        sections = controller.get_history_sections()
        drawer_content.clear()
        with drawer_content:
            render_sidebar(
                user_name=controller.settings_manager.get_user_setting('username', 'User'),
                on_new_chat=controller.load_new_chat,
                on_history_click=controller.load_chat,
                on_settings_click=settings_modal.open,
                history_sections=sections,
                current_chat_id=controller.current_chat_id,
            )

    # State variable to hold the markdown element of the active response
    current_response_ui = None

    async def render_chat():
        nonlocal current_response_ui
        chat_container.clear()
        
        # Delegate rendering to component
        current_response_ui = render_chat_messages(chat_container, controller.messages)
        
        await scroll_to_bottom()
        update_input_state()

    async def stream_update(text):
        if current_response_ui:
            current_response_ui.set_content(text)
            # Optional: Scroll every X chars logic is in manager? No, manager just sends text.
            # We can scroll every time or use a throttle.
            # For now, scroll every time might be jittery but correct.
            # Let's check length for scroll
            if len(text) % 300 == 0:
                await scroll_to_bottom()
    
    def update_input_state():
        # Update InputBar state via the controller object
        input_control.set_loading(controller.is_generating)

    # ---------------------------------------------------------
    # Hook up Callbacks
    # ---------------------------------------------------------
    
    controller.refresh_history_callback = render_sidebar_content
    controller.refresh_chat_callback = render_chat
    controller.stream_update_callback = stream_update
    
    # ---------------------------------------------------------
    # Initial Load
    # ---------------------------------------------------------
    
    # Since render_sidebar refers to controller.current_chat_id, we just load sidebar
    # We should probably initialize the controller state if needed, but it starts empty.
    # We need to run the render functions once.
    
    # Use lifecycle hook to run async functions after connection
    async def startup():
        await render_sidebar_content()
        await render_chat()
        
    # We can call them immediately since we are in the page builder (they build initial state)
    # But they are async functions (render_sidebar_content uses async clear?) No clear is sync usually.
    # `container.clear()` is sync.
    # However, `render_sidebar_content` is defined as async above to match callback signature?
    # Actually manager defines callbacks as Coroutine.
    
    # Let's run them.
    # Note: Can't await directly in page builder unless it's an async page?
    # Page function is sync `def main_page():`.
    # So we use `app.on_connect` or `ui.timer` with 0 delay.
    
    ui.timer(0, startup, once=True)
