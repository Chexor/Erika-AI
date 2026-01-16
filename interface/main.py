"""interface/main.py
Assembler for the component-based Erika AI UI.
"""
from typing import List, Dict
from nicegui import ui, app
from interface.manager import ChatController
from interface.components import render_sidebar, InputBar
from interface.settings_ui import SettingsModal

# ---------------------------------------------------------------------
# Global initialization and Controller Instantiation
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# Main Page Layout
# ---------------------------------------------------------------------
@ui.page('/')
def main_page():
    
    # --- Helper function to refresh the sidebar ---
    async def refresh_sidebar():
        # This is a bit of a hack to get the new history to show up,
        # by replacing the content of the drawer.
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

    # --- UI Definition ---
    
    # We need a container for the sidebar content to be able to refresh it
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800') as left_drawer:
        drawer_content = ui.column().classes('w-full')

    # Main chat area that is bound to the controller's message list
    chat_messages = ui.chat_message(
        on_send=controller.send_message,
    ).classes('w-full max-w-4xl mx-auto min-h-screen p-4 pb-48')
    
    # Bind the chat message content to the controller's list of messages.
    # This is the core of the new architecture. The UI will automatically update
    # whenever the controller modifies `controller.messages`.
    chat_messages.bind_content_from(controller, 'messages')
    
    # The input bar is a separate component at the bottom
    model_name = controller.settings_manager.get_system_setting('model', controller.brain.get_model_name())
    txt_input, send_btn, stop_btn = InputBar(
        model_name=model_name,
        on_send=chat_messages.send, # Use the chat_message's own send method
        on_stop=controller.stop_generation,
    )
    
    # Bind button visibility to the controller's 'is_generating' state
    send_btn.bind_visibility_from(controller, 'is_generating', backward=lambda x: not x)
    stop_btn.bind_visibility_from(controller, 'is_generating')

    # --- Initial State and Callbacks ---

    # Set the controller's callback to our refresh function
    controller.refresh_history_callback = refresh_sidebar
    
    # Load initial history
    app.on_startup(refresh_sidebar)