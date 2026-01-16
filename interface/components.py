"""interface/components.py
Pure UI rendering functions for Erika AI.
"""

from nicegui import ui


def render_sidebar(user_name: str, on_new_chat, on_history_click, on_settings_click, history_sections: dict):
    """Render the left drawer (sidebar).
    Args:
        user_name: Display name for the profile.
        on_new_chat: Callable for the "New Chat" button.
        on_history_click: Callable that receives a chat_id when a history item is clicked.
        on_settings_click: Callable to open the Settings modal.
        history_sections: Dict with keys like 'Today', 'Yesterday', 'Older' mapping to lists of chat dicts.
    """
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px'):
        # New Chat Button
        ui.button('New Chat', icon='add', on_click=on_new_chat) \
            .classes('w-full border border-gray-700 hover:bg-gray-800 text-white rounded-md text-left px-3 py-2 transition-colors') \
            .props('flat no-caps align=left')

        # History Column (refreshable)
        history_column = ui.column().classes('flex-grow overflow-y-auto gap-2')

        def render_section(title, chats):
            if not chats:
                return
            ui.label(title).classes('text-xs font-bold text-gray-500 px-2 mt-4 mb-1 uppercase')
            for chat in chats:
                active = chat.get('id') == getattr(on_history_click, 'current_chat_id', None)
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

    return history_column  # Return the column so the controller can refresh it



def InputBar(model_name: str, on_send, on_stop):
    """Render the floating input bar.
    Args:
        model_name: Name of the currently loaded model.
        on_send: Callable to trigger sending the message, receives the text content.
        on_stop: Callable to stop generation.
    """
    with ui.page_sticky(position='bottom').classes('w-full flex justify-center pb-8 px-4'):
        with ui.row().classes('w-full max-w-5xl bg-[#2f2f2f] rounded-2xl shadow-xl border border-white/10 p-2 pl-4 items-end'):
            ui.chip(model_name, icon='psychology').props('outline color=grey-4').classes('text-xs font-bold mr-2 mb-2 uppercase select-none opacity-50')
            
            txt = ui.textarea(placeholder='Send a message') \
                .props('autogrow rows=1 borderless input-class="text-white placeholder-gray-500"') \
                .classes('flex-grow text-white text-base min-h-[44px] max-h-[160px] mx-2 py-2')
            
            with ui.row().classes('items-center gap-2 pr-1 mb-1'):
                stop_btn = ui.button(icon='stop_circle', on_click=on_stop).props('flat round color=red').classes('hover:bg-gray-800 transition-colors')
                send_btn = ui.button(icon='arrow_upward', on_click=lambda: on_send(txt.value)).props('round color=white text-color=black').classes('shadow-lg hover:bg-gray-200 transition-colors')

    return txt, send_btn, stop_btn
