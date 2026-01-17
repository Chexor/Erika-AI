from nicegui import ui
from interface.controller import Controller

def build_ui(controller: Controller):
    """Builds the main UI layout."""
    
    # Theme & Style
    ui.add_head_html("""
        <style>
            body { background-color: #0f172a; color: #e2e8f0; }
            .erika-gradient { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }
            .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
            .chat-bubble-user { background-color: #2563eb; color: white; border-radius: 12px 12px 0 12px; }
            .chat-bubble-ai { background-color: #1e293b; color: #e2e8f0; border-radius: 12px 12px 12px 0; border: 1px solid #334155; }
        </style>
    """)
    
    # Layout
    with ui.row().classes('w-full h-screen no-wrap gap-0'):
        # Sidebar
        with ui.column().classes('w-64 h-fullerika-gradient border-r border-slate-700 p-4 gap-2'):
            ui.label('ERIKA AI').classes('text-xl font-bold tracking-wider text-blue-400 mb-4')
            
            ui.button('New Chat', on_click=controller.new_chat).classes('w-full mb-4 bg-blue-600 hover:bg-blue-500')
            
            with ui.scroll_area().classes('w-full flex-grow'):
                history_list = ui.column().classes('w-full gap-1')
        
        # Main Chat Area
        with ui.column().classes('flex-grow h-full relative bg-slate-900'):
            # Messages
            with ui.scroll_area().classes('w-full flex-grow p-4') as scroll_container:
                messages_container = ui.column().classes('w-full max-w-3xl mx-auto gap-4 pb-24')
            
            # Floating Input Pill
            with ui.row().classes('absolute bottom-6 left-1/2 transform -translate-x-1/2 w-full max-w-2xl'):
                with ui.row().classes('w-full glass rounded-full p-2 items-center gap-2 shadow-2xl'):
                    input_field = ui.input(placeholder='Message Erika...').classes('flex-grow px-4 border-none focus:outline-none bg-transparent text-white').props('dark')
                    
                    async def send():
                        text = input_field.value
                        if not text: return
                        input_field.value = ''
                        await controller.handle_user_input(text)
                    
                    input_field.on('keydown.enter', send)
                    ui.button(icon='arrow_up', on_click=send).props('round flat color=blue').classes('mr-1')

    # Refresh Logic
    async def refresh():
        messages_container.clear()
        with messages_container:
            for msg in controller.chat_history:
                align = 'items-end self-end' if msg['role'] == 'user' else 'items-start self-start'
                bubble = 'chat-bubble-user' if msg['role'] == 'user' else 'chat-bubble-ai'
                with ui.column().classes(f'w-full {align}'):
                    ui.markdown(msg['content']).classes(f'p-3 {bubble} max-w-xl text-sm leading-relaxed')
        
        # Reload history list (simplified for now)
        # Note: In real app, we'd optimize this to not reload every message
        chats = await controller.load_history()
        history_list.clear()
        with history_list:
            for chat in chats:
                with ui.row().classes('w-full p-2 hover:bg-slate-800 rounded cursor-pointer group items-center').on('click', lambda c=chat['id']: controller.load_chat_session(c)):
                    ui.label(chat['preview'] or 'New Chat').classes('text-xs text-slate-400 truncate flex-grow group-hover:text-blue-300')
                    
    controller.bind_view(refresh)
    # Initial load
    # ui.timer(0.1, lambda: asyncio.create_task(controller.load_history()), once=True)
    # Actually wait for startup
