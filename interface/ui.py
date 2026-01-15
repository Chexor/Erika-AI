from nicegui import ui, app
from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager
from core.logger import setup_logger
from interface.settings_ui import SettingsModal
import asyncio
from datetime import datetime, timedelta

# Instantiate Brain at top level to keep it alive
logger = setup_logger("UI")
my_brain = Brain()
memory_manager = MemoryManager()
settings_manager = SettingsManager()

# --- Connection Logic ---
async def on_connect_handler(client):
    logger.info(f"New client connected: {client.id}")
    await check_brain_status()

app.on_connect(on_connect_handler)
app.add_static_files('/assets', 'assets')

async def check_brain_status():
    is_connected = await asyncio.to_thread(my_brain.status_check)
    if not is_connected:
        ui.notify('⚠️ Brain Disconnected: Is Ollama running?', type='negative', close_button=True, timeout=0)

# --- UI Definition ---
@ui.page('/')
def main_page():
    # State
    current_chat_id = None
    
    # 1. Global Theme & Dark Mode
    ui.colors(primary='#3b82f6', dark='#0f172a') # Blue-500, Slate-900
    dark_mode = ui.dark_mode()
    
    # Load User Settings
    u_name = settings_manager.get_user_setting("username", "User")
    u_theme = settings_manager.get_user_setting("theme", "dark")
    u_persona = settings_manager.get_user_setting("persona", "You are Erika, a helpful AI.") # Load persona
    
    if u_theme == 'dark':
        dark_mode.enable()
    else:
        dark_mode.disable()
    
    # State for generation control
    is_generating = False 
    stop_generation_flag = False

    # Force background color for the body
    ui.query('body').style('background-color: #212121;')
    ui.query('body').classes('text-gray-100 font-sans antialiased')

    # --- SETTINGS MODAL ---
    def toggle_theme():
        if dark_mode.value: # Currently Dark
            dark_mode.disable()
            settings_manager.set_user_setting("theme", "light")
        else:
            dark_mode.enable()
            settings_manager.set_user_setting("theme", "dark")
            
    settings_modal = SettingsModal(settings_manager, on_theme_toggle=toggle_theme)

    # --- UI Layout Containers ---
    # We define placeholders for dynamic content
    
    # Sidebar
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px'):
        # New Chat Button
        ui.button('New Chat', icon='add', on_click=lambda: load_new_chat()) \
            .classes('w-full border border-gray-700 hover:bg-gray-800 text-white rounded-md text-left px-3 py-2 transition-colors') \
            .props('flat no-caps align=left')

        # History Column (REFRESHABLE)
        history_column = ui.column().classes('flex-grow overflow-y-auto gap-2')
        
        # User Profile (Bottom)
        with ui.row().classes('w-full items-center gap-3 pt-4 border-t border-gray-800 cursor-pointer hover:bg-gray-800 p-2 rounded transition-colors').on('click', settings_modal.open):
            ui.avatar(icon='person', color='gray-700', text_color='white').props('size=sm')
            user_name_label = ui.label(u_name).classes('text-sm font-medium text-white')
            ui.icon('settings', color='gray-500').classes('ml-auto text-xs')

    # Main Chat Area
    with ui.column().classes('w-full max-w-3xl mx-auto h-screen p-4 pb-32 relative') as chat_container:
        # Empty State (Initial)
        empty_state = ui.column().classes('w-full h-full justify-center items-center gap-6 opacity-40 select-none')
        with empty_state:
            ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-32 opacity-80')
            ui.label('How can I help you today?').classes('text-2xl font-semibold text-gray-500')

    # --- Logic Functions ---

    def render_message(role, content):
        """Renders a single message bubble."""
        with chat_container:
            if role == 'user':
                with ui.row().classes('w-full justify-end mb-4'):
                    ui.label(content).classes('bg-gray-700 text-white rounded-3xl px-5 py-3 max-w-[85%] text-base leading-relaxed')
            elif role == 'assistant':
                with ui.row().classes('w-full justify-start mb-6 gap-4 items-start'):
                     with ui.element('div').classes('min-w-[32px] pt-1'):
                         ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800')
                     # Markdown Extras enabled
                     ui.markdown(content, extras=['fenced-code-blocks', 'tables', 'latex']).classes('text-gray-100 text-base leading-relaxed max-w-full overflow-hidden prose prose-invert')

    def load_new_chat():
        nonlocal current_chat_id
        current_chat_id = None
        chat_container.clear()
        
        # Re-add empty state
        with chat_container:
            # We recreate the empty state structure since clear() wiped it
            nonlocal empty_state 
            empty_state = ui.column().classes('w-full h-full justify-center items-center gap-6 opacity-40 select-none')
            with empty_state:
                ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-32 opacity-80')
                ui.label('How can I help you today?').classes('text-2xl font-semibold text-gray-500')
        
        refresh_history_ui()

    def load_specific_chat(chat_id):
        nonlocal current_chat_id
        current_chat_id = chat_id
        
        data = memory_manager.load_chat(chat_id)
        if not data:
            return

        chat_container.clear()
        # No empty state
        
        # Render past messages
        for msg in data.get('messages', []):
            render_message(msg['role'], msg['content'])
            
        refresh_history_ui()

    def refresh_history_ui():
        history_column.clear()
        chats = memory_manager.list_chats()
        
        # Buckets
        today_chats = []
        yesterday_chats = []
        older_chats = []
        
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        for chat in chats:
            try:
                # updated_at is ISO string
                chat_date = datetime.fromisoformat(chat['updated_at']).date()
            except Exception:
                # Fallback if date parsing fails
                chat_date = datetime.min.date()
                
            if chat_date == today:
                today_chats.append(chat)
            elif chat_date == yesterday:
                yesterday_chats.append(chat)
            else:
                older_chats.append(chat)
        
        with history_column:
            if not chats:
                ui.label('No chats yet').classes('text-xs text-gray-600 px-2 italic')
                return

            def render_section(title, chat_list):
                if not chat_list:
                    return
                ui.label(title).classes('text-xs font-bold text-gray-500 px-2 mt-4 mb-1 uppercase')
                for chat in chat_list:
                    bg_class = 'bg-gray-800' if chat['id'] == current_chat_id else 'hover:bg-gray-800'
                    ui.button(chat['title'], on_click=lambda c=chat['id']: load_specific_chat(c)) \
                        .classes(f'w-full text-left text-sm text-gray-400 {bg_class} rounded px-2 py-1 truncate transition-colors') \
                        .props('flat no-caps')

            render_section('Today', today_chats)
            render_section('Yesterday', yesterday_chats)
            render_section('Older', older_chats)

    async def send():
        nonlocal current_chat_id, is_generating, stop_generation_flag
        user_msg = text_input.value
        if not user_msg:
            return
        
        # Don't send if already generating
        if is_generating:
            return

        text_input.value = ''
        
        # UI State Update
        is_generating = True
        stop_generation_flag = False
        
        # Toggle buttons based on state
        send_btn.set_visibility(False)
        stop_btn.set_visibility(True)
        
        # Determine if New Chat
        if current_chat_id is None:
            current_chat_id = memory_manager.create_chat()
            empty_state.set_visibility(False) # Hide empty state if it exists
        else:
             # Ensure empty state is gone if we are adding to existing
             empty_state.set_visibility(False)

        # 1. Render User Message
        render_message('user', user_msg)

        # 2. Render Erika Placeholder
        with chat_container:
            response_row = ui.row().classes('w-full justify-start mb-6 gap-4 items-start')
            with response_row:
                 with ui.element('div').classes('min-w-[32px] pt-1'):
                     ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800')
                 response_content = ui.markdown(extras=['fenced-code-blocks', 'tables', 'latex']).classes('text-gray-100 text-base leading-relaxed max-w-full overflow-hidden prose prose-invert')
                 
        # 3. Stream
        full_response = ""
        
        # Prepare Context
        # Load existing history (stripped to role/content)
        history = memory_manager.get_messages(current_chat_id)
        
        # Sliding Window: Keep only the last 20 messages to prevent overflow
        if len(history) > 20:
            history = history[-20:]
            
        # Add current message
        current_context = history + [{"role": "user", "content": user_msg}]
        
        try:
            # Pass constrained context to think_stream
            async for chunk in my_brain.think_stream(current_context):
                if stop_generation_flag:
                    break
                full_response += chunk
                response_content.set_content(full_response)
                # await asyncio.sleep(0) # Not needed with async iterator, but harmless
            
            # 4. Save to Memory
            memory_manager.save_turn(current_chat_id, user_msg, full_response)
            
            # 5. Refresh sidebar (update titles etc)
            refresh_history_ui()
            
        except Exception as e:
            ui.notify(f"Error: {e}", type='negative')
        finally:
            # Reset UI State
            is_generating = False
            stop_generation_flag = False
            stop_btn.set_visibility(False)
            send_btn.set_visibility(True)

    def stop_generation():
        nonlocal stop_generation_flag
        stop_generation_flag = True
        ui.notify("Stopping generation...")
    
    # --- Floating Input Bar ---
    with ui.page_sticky(position='bottom', x_offset=0, y_offset=40).classes('w-full flex justify-center px-4'):
        with ui.row().classes('w-full max-w-3xl bg-gray-700/90 backdrop-blur-sm rounded-full p-2 pl-4 items-center shadow-2xl border border-gray-600'):
            # Model Chip (Read Only)
            model_name = my_brain.get_model_name()
            ui.chip(model_name, icon='psychology').props('outline color=grey-4').classes('text-xs font-bold mr-2 uppercase select-none opacity-80')
            
            text_input = ui.textarea(placeholder='Send a message') \
                .props('autogrow rows=1 borderless input-class="text-white placeholder-gray-400"') \
                .classes('col-grow text-white text-base max-h-40 mx-2') \
                .on('keydown.enter.prevent', lambda: asyncio.create_task(send())) 
            
            with ui.row().classes('items-center gap-2 pr-1'):
                # Stop Button (Hidden by default)
                stop_btn = ui.button(icon='stop_circle', on_click=stop_generation) \
                    .props('flat round color=red') \
                    .classes('hover:bg-gray-800 transition-colors') 
                stop_btn.set_visibility(False)

                # Send Button
                send_btn = ui.button(on_click=lambda: asyncio.create_task(send())) \
                    .props('round icon=arrow_upward color=white text-color=black') \
                    .classes('shadow-lg hover:bg-gray-200 transition-colors')

    # Initial Load
    refresh_history_ui()
