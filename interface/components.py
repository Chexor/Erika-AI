"""interface/components.py
Pure UI rendering functions for Erika AI.
"""

from nicegui import ui
from typing import List, Dict



def ChatBubble(message: Dict, on_regenerate=None, on_copy=None, on_speak=None):
    """Renders a single chat bubble with actions for assistant messages."""
    role = message['role']
    content = message['content']
    
    if role == 'user':
        with ui.row().classes('w-full justify-end mb-4 group'):
            ui.label(content).classes('bg-gray-700 text-white rounded-3xl px-5 py-3 max-w-[85%] text-base leading-relaxed break-words')
    else:
        with ui.row().classes('w-full justify-start mb-6 gap-4 items-start group relative'):
            # Avatar
            with ui.element('div').classes('min-w-[32px] pt-1'):
                 if message.get('avatar'):
                        ui.image(message['avatar']).classes('w-8 h-8 rounded-full bg-gray-800')
            
            # Message Content & Actions Container
            with ui.column().classes('max-w-full flex-grow'):
                # Markdown Content
                md = ui.markdown(content, extras=['fenced-code-blocks', 'tables', 'latex']).classes('text-gray-100 text-base leading-relaxed max-w-full prose prose-invert break-words')
                
                # Action Row
                with ui.row().classes('opacity-0 group-hover:opacity-100 transition-opacity duration-200 gap-1 mt-1'):
                    if on_regenerate:
                        ui.button(icon='refresh', on_click=on_regenerate).props('flat round dense size=sm color=grey').tooltip('Regenerate')
                    if on_copy:
                        ui.button(icon='content_copy', on_click=lambda: on_copy(content)).props('flat round dense size=sm color=grey').tooltip('Copy')
                    if on_speak:
                        ui.button(icon='volume_up', on_click=lambda: on_speak(content)).props('flat round dense size=sm color=grey').tooltip('Read Aloud')

                return md 
    return None


def render_chat_messages(chat_container, messages: List[Dict], on_regenerate, on_copy, on_speak):
    """Renders the chat messages into the container."""
    current_response_ui = None
    
    with chat_container:
        if not messages:
            with ui.column().classes('w-full h-full justify-center items-center gap-6 opacity-40 select-none mt-32'):
                ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-32 opacity-80 mix-blend-screen')
                ui.label('How can I help you today?').classes('text-2xl font-semibold text-gray-500')
            return None

        for msg in messages:
            # We pass callbacks down
            # Note: For efficiency, we might only want actions on the *last* assistant message?
            # Or all of them. Let's do all.
            md = ChatBubble(msg, on_regenerate, on_copy, on_speak)
            if msg['role'] == 'assistant':
                current_response_ui = md
                    
    return current_response_ui


class InputControl:
    """Controller object for the InputBar component."""
    def __init__(self, txt, send_btn, stop_btn):
        self._txt = txt
        self._send_btn = send_btn
        self._stop_btn = stop_btn

    def set_loading(self, is_loading: bool):
        """Updates the visibility of buttons based on loading state."""
        self._send_btn.set_visibility(not is_loading)
        self._stop_btn.set_visibility(is_loading)

def render_sidebar(user_name: str, on_new_chat, on_history_click, on_settings_click, history_sections: dict, current_chat_id: str = None):
    """Render the left drawer (sidebar)."""
    # New Chat Button
    ui.button('New Chat', icon='add', on_click=on_new_chat) \
        .classes('w-full border border-gray-700 hover:bg-gray-800 text-white rounded-md text-left px-3 py-2 transition-colors') \
        .props('flat no-caps align=left')

    # History Column (refreshable)
    # We render directly into the active context (the drawer).
    # We create a column for history items so we can clear it later if needed, 
    # BUT the caller currently clears the *entire* drawer content. 
    # So we just render into the flow.
    ui.label('History').classes('hidden') # Placeholder if needed or just remove unused var return.

    def render_section(title, chats):
        if not chats:
            return
        ui.label(title).classes('text-xs font-bold text-gray-500 px-2 mt-4 mb-1 uppercase')
        for chat in chats:
            active = chat.get('id') == current_chat_id
            btn = ui.button(chat.get('title', 'Untitled'), icon='chat_bubble_outline', on_click=lambda _, cid=chat.get('id'): on_history_click(cid))
            btn.classes(
                f'w-full text-left truncate text-sm rounded px-2 py-1 transition-colors ' 
                f"{'bg-gray-700 text-white' if active else 'text-gray-400 hover:bg-gray-800'}"
            ).props('flat no-caps align=left')

    for sec_title, sec_chats in history_sections.items():
        render_section(sec_title, sec_chats)

    # Bottom user profile
    with ui.row().classes('w-full items-center gap-3 pt-4 border-t border-gray-800 cursor-pointer hover:bg-gray-800 p-2 rounded transition-colors group').on('click', on_settings_click):
        ui.avatar(icon='person', color='gray-700', text_color='white').props('size=sm')
        ui.label(user_name).classes('text-sm font-medium text-white group-hover:text-blue-400 transition-colors')
        ui.icon('settings', color='gray-500').classes('ml-auto text-xs group-hover:text-white transition-colors')       


def InputBar(model_name: str, on_send, on_stop) -> InputControl:
    """Render the floating input bar.
    Returns:
        InputControl: An object to manipulate the input bar state (e.g. set_loading).
    """
    with ui.page_sticky(position='bottom').classes('w-full flex justify-center pb-8 px-4'):
        with ui.row().classes('w-full max-w-5xl bg-[#2f2f2f] rounded-2xl shadow-xl border border-white/10 p-2 pl-4 items-end'):
            ui.chip(model_name, icon='psychology').props('outline color=grey-4').classes('text-xs font-bold mr-2 mb-2 uppercase select-none opacity-50')

            txt = ui.textarea(placeholder='Send a message') \
                .props('autogrow rows=1 borderless input-class="text-white placeholder-gray-500"') \
                .classes('flex-grow text-white text-base min-h-[44px] max-h-[160px] mx-2 py-2')

            with ui.row().classes('items-center gap-2 pr-1 mb-1'):
                stop_btn = ui.button(icon='stop_circle', on_click=on_stop).props('flat round color=red').classes('hover:bg-gray-800 transition-colors')
                def handle_send():
                    val = txt.value
                    if val:
                        txt.value = ''
                        on_send(val)
                send_btn = ui.button(icon='arrow_upward', on_click=handle_send).props('round color=white text-color=black').classes('shadow-lg hover:bg-gray-200 transition-colors')
                
                # Default state
                stop_btn.set_visibility(False)

    return InputControl(txt, send_btn, stop_btn)