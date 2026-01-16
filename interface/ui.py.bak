from nicegui import ui, app
from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager
from core.logger import setup_logger
from interface.settings_ui import SettingsModal
import asyncio
from datetime import datetime, timedelta

logger = setup_logger("UI")

# These will be initialized on startup
my_brain: Brain | None = None
memory_manager: MemoryManager | None = None
settings_manager: SettingsManager | None = None

@app.on_startup
async def initialize_core():
    global my_brain, memory_manager, settings_manager
    logger.info("Initializing core components...")
    my_brain = Brain()
    memory_manager = MemoryManager()
    settings_manager = SettingsManager()
    # Optional: await my_brain.warm_up() if you have such method

# ────────────────────────────────────────────────
# Connection & global status check
# ────────────────────────────────────────────────

async def on_connect_handler(client):
    logger.info(f"New client connected: {client.id}")
    await check_brain_status()

app.on_connect(on_connect_handler)

async def check_brain_status():
    if my_brain is None:
        ui.notify('⚠️ Core not initialized yet', type='warning')
        return
    is_connected = await asyncio.to_thread(my_brain.status_check)
    if not is_connected:
        ui.notify('⚠️ Brain Disconnected: Is Ollama running?', type='negative', close_button=True, timeout=0)

app.add_static_files('/assets', 'assets')

# ────────────────────────────────────────────────
# Main page
# ────────────────────────────────────────────────

@ui.page('/')
def main_page():
    if my_brain is None or memory_manager is None or settings_manager is None:
        ui.label('Application starting... please wait.').classes('text-xl text-center mt-20')
        return

    current_chat_id = None
    is_generating = False
    stop_generation_flag = False

    # Theme & settings
    dark_mode = ui.dark_mode()
    u_name = settings_manager.get_user_setting("username", "User")
    u_theme = settings_manager.get_user_setting("theme", "dark")
    # u_persona = settings_manager.get_user_setting("persona", "You are Erika, a helpful AI.")

    if u_theme == 'dark':
        dark_mode.enable()
    else:
        dark_mode.disable()

    def toggle_theme():
        if dark_mode.value:
            dark_mode.disable()
            settings_manager.set_user_setting("theme", "light")
        else:
            dark_mode.enable()
            settings_manager.set_user_setting("theme", "dark")

    settings_modal = SettingsModal(settings_manager, on_theme_toggle=toggle_theme)

    # -------------------  Function Definitions -------------------

    async def scroll_to_bottom(smooth=True):
        behavior = "smooth" if smooth else "auto"
        await ui.run_javascript(f'window.scrollTo({{ top: document.body.scrollHeight, behavior: "{behavior}" }});')

    async def render_message(role: str, content: str):
        # This function will be defined properly below, but we need the reference
        pass

    def refresh_history_ui():
        # This function will be defined properly below
        pass

    async def load_new_chat():
        nonlocal current_chat_id
        current_chat_id = None
        chat_container.clear()
        empty_state.move(chat_container)
        empty_state.set_visibility(True)
        refresh_history_ui()
        await scroll_to_bottom(smooth=False)

    async def load_specific_chat(chat_id):
        nonlocal current_chat_id
        current_chat_id = chat_id
        data = memory_manager.load_chat(chat_id)
        if not data:
            ui.notify("Chat not found", type='negative')
            return

        chat_container.clear()
        empty_state.set_visibility(False)

        for msg in data.get('messages', []):
            await render_message(msg['role'], msg['content'])

        refresh_history_ui()
        await scroll_to_bottom(smooth=False)

    async def send():
        nonlocal current_chat_id, is_generating, stop_generation_flag

        user_msg = text_input.value.strip()
        if not user_msg or is_generating:
            return

        text_input.value = ''
        is_generating = True
        stop_generation_flag = False

        send_btn.set_visibility(False)
        stop_btn.set_visibility(True)

        if current_chat_id is None:
            current_chat_id = memory_manager.create_chat()
            empty_state.set_visibility(False)

        await render_message('user', user_msg)

        with chat_container:
            response_row = ui.row().classes('w-full justify-start mb-6 gap-4 items-start')
            with response_row:
                with ui.element('div').classes('min-w-[32px] pt-1'):
                    ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800')
                response_content = ui.markdown(extras=['fenced-code-blocks', 'tables', 'latex']) \
                    .classes('text-gray-100 text-base leading-relaxed max-w-full prose prose-invert')
                loading = ui.spinner(size='lg', color='primary').classes('mt-3')

        await scroll_to_bottom()

        full_response = ""
        history = memory_manager.get_messages(current_chat_id)
        if len(history) > 20:
            history = history[-20:]
        context = history + [{"role": "user", "content": user_msg}]

        try:
            async for chunk in my_brain.think_stream(context):
                if stop_generation_flag:
                    break
                full_response += chunk
                response_content.set_content(full_response)
                if len(full_response) % 300 == 0:
                    await scroll_to_bottom()

            loading.delete()
            memory_manager.save_turn(current_chat_id, user_msg, full_response)
            refresh_history_ui()

        except Exception as e:
            loading.delete()
            response_content.set_content(f"**Error**: {str(e)}")
            ui.notify(f"Generation failed: {str(e)}", type='negative')

        finally:
            is_generating = False
            stop_generation_flag = False
            stop_btn.set_visibility(False)
            send_btn.set_visibility(True)
            await scroll_to_bottom()

    def stop_generation():
        nonlocal stop_generation_flag
        stop_generation_flag = True
        ui.notify("Stopping generation...")

    # ------------------- UI Layout -------------------
    # Re-define functions that interact with UI elements

    # ── Sidebar ───────────────────────────────────────
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px') as left_drawer:
        ui.button('New Chat', icon='add', on_click=load_new_chat) \
            .classes('w-full border border-gray-700 hover:bg-gray-800 text-white rounded-md text-left px-3 py-2 transition-colors') \
            .props('flat no-caps align=left')

        history_column = ui.column().classes('flex-grow overflow-y-auto gap-2')

        with ui.row().classes('w-full items-center gap-3 pt-4 border-t border-gray-800 cursor-pointer hover:bg-gray-800 p-2 rounded transition-colors group').on('click', settings_modal.open):
            ui.avatar(icon='person', color='gray-700', text_color='white').props('size=sm')
            user_name_label = ui.label(u_name).classes('text-sm font-medium text-white group-hover:text-blue-400 transition-colors')
            ui.icon('settings', color='gray-500').classes('ml-auto text-xs group-hover:text-white transition-colors')

    # ── Main chat area ────────────────────────────────
    with ui.column().classes('w-full max-w-4xl mx-auto min-h-screen p-4 pb-48 relative') as chat_container:
        empty_state = ui.column().classes('w-full h-full justify-center items-center gap-6 opacity-40 select-none mt-32')
        with empty_state:
            ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-32 opacity-80 mix-blend-screen')
            ui.label('How can I help you today?').classes('text-2xl font-semibold text-gray-500')
        ui.element('div').classes('h-48 w-full')

    # Now, properly define the functions that interact with the UI
    async def render_message(role: str, content: str):
        with chat_container:
            if role == 'user':
                with ui.row().classes('w-full justify-end mb-4'):
                    ui.label(content).classes('bg-gray-700 text-white rounded-3xl px-5 py-3 max-w-[85%] text-base leading-relaxed')
            elif role == 'assistant':
                with ui.row().classes('w-full justify-start mb-6 gap-4 items-start'):
                    with ui.element('div').classes('min-w-[32px] pt-1'):
                        ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800')
                    ui.markdown(
                        content,
                        extras=['fenced-code-blocks', 'tables', 'latex']
                    ).classes('text-gray-100 text-base leading-relaxed max-w-full prose prose-invert')
        await scroll_to_bottom()

    def refresh_history_ui():
        history_column.clear()
        chats = memory_manager.list_chats()
        if not chats:
            with history_column:
                ui.label('No chats yet').classes('text-xs text-gray-600 px-2 italic')
            return

        today_chats, yesterday_chats, older_chats = [], [], []
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)

        for chat in chats:
            try:
                chat_date = datetime.fromisoformat(chat['updated_at']).date()
            except:
                chat_date = datetime.min.date()

            if chat_date == today:
                today_chats.append(chat)
            elif chat_date == yesterday:
                yesterday_chats.append(chat)
            else:
                older_chats.append(chat)

        with history_column:
            def render_section(title, chat_list):
                if not chat_list:
                    return
                ui.label(title).classes('text-xs font-bold text-gray-500 px-2 mt-4 mb-1 uppercase')
                for chat in chat_list:
                    active = chat['id'] == current_chat_id
                    ui.button(
                        chat['title'],
                        icon='chat_bubble_outline',
                        on_click=lambda _, c=chat['id']: load_specific_chat(c)
                    ).classes(
                        f'w-full text-left justify-start truncate text-sm rounded px-2 py-1 transition-colors '
                        f'{"bg-gray-700 text-white" if active else "text-gray-400 hover:bg-gray-800"}'
                    ).props('flat no-caps align=left')

            render_section('Today', today_chats)
            render_section('Yesterday', yesterday_chats)
            render_section('Older', older_chats)

    # ── Floating input bar ────────────────────────────
    with ui.page_sticky(position='bottom').classes('w-full flex justify-center pb-8 px-4'):
        with ui.row().classes('w-full max-w-4xl bg-[#2f2f2f] rounded-2xl shadow-xl border border-white/10 p-2 pl-4 items-end'):
            model_name = settings_manager.get_system_setting('model', my_brain.get_model_name())
            ui.chip(model_name, icon='psychology').props('outline color=grey-4').classes('text-xs font-bold mr-2 mb-2 uppercase select-none opacity-50')

            text_input = ui.textarea(placeholder='Send a message') \
                .props('autogrow rows=1 borderless input-class="text-white placeholder-gray-500"') \
                .classes('flex-grow text-white text-base min-h-[44px] max-h-[160px] mx-2 py-2') \
                .on('keydown.enter.prevent', send)

            with ui.row().classes('items-center gap-2 pr-1 mb-1'):
                stop_btn = ui.button(icon='stop_circle', on_click=stop_generation) \
                    .props('flat round color=red') \
                    .classes('hover:bg-gray-800 transition-colors')
                stop_btn.set_visibility(False)

                send_btn = ui.button(on_click=send) \
                    .props('round icon=arrow_upward color=white') \
                    .classes('shadow-lg hover:bg-gray-300 transition-colors')

    # Initial load
    refresh_history_ui()