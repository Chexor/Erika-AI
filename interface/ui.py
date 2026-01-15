from nicegui import ui, app
from core.brain import Brain
import asyncio

# Instantiate Brain at top level to keep it alive
my_brain = Brain()

# --- Connection Logic ---
async def on_connect_handler(client):
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
    # 1. Global Theme & Dark Mode
    ui.colors(primary='#3b82f6', dark='#0f172a') # Blue-500, Slate-900
    ui.dark_mode().enable()
    
    # Force background color for the body to match dark theme preference (Gray-800/900 mix or #212121)
    ui.query('body').style('background-color: #212121;')
    ui.query('body').classes('text-gray-100 font-sans antialiased')

    # --- Sidebar (Left Drawer) ---
    with ui.left_drawer(value=True).classes('bg-gray-900 border-r border-gray-800 flex flex-col gap-4 p-4').style('width: 260px'):
        # New Chat Button
        ui.button('New Chat', icon='add', on_click=lambda: ui.notify('New Chat Checked (Placeholder)')) \
            .classes('w-full border border-gray-700 hover:bg-gray-800 text-white rounded-md text-left px-3 py-2 transition-colors') \
            .props('flat no-caps align=left')

        # History / Spacer
        with ui.column().classes('flex-grow overflow-y-auto gap-2'):
            ui.label('Today').classes('text-xs font-semibold text-gray-500 px-2 mt-2')
            # Placeholder history items
            for i in range(3):
                ui.label(f'Previous Chat {i+1}').classes('text-sm text-gray-400 hover:bg-gray-800 rounded px-2 py-1 cursor-pointer truncate w-full')

        # User Profile (Bottom)
        with ui.row().classes('w-full items-center gap-3 pt-4 border-t border-gray-800'):
            ui.avatar(icon='person', color='gray-700', text_color='white').props('size=sm')
            ui.label('Tim').classes('text-sm font-medium text-white')

    # --- Main Content Area ---
    # We use a column for the chat, ensuring it has padding at bottom for the floating input
    with ui.column().classes('w-full max-w-3xl mx-auto h-screen p-4 pb-32 relative') as chat_container:
        
        # Empty State (Initial)
        # We can toggle this visibility based on message count
        empty_state = ui.column().classes('w-full h-full justify-center items-center gap-6 opacity-40 select-none')
        with empty_state:
            ui.image('/assets/Erika-AI_logo_transparant.png').classes('w-32 opacity-80')
            ui.label('How can I help you today?').classes('text-2xl font-semibold text-gray-500')

    # --- Interaction Logic & Messages ---
    async def send():
        user_msg = text_input.value
        if not user_msg:
            return
        
        text_input.value = ''
        empty_state.set_visibility(False) # Hide empty state
        
        # 1. User Message
        with chat_container:
            with ui.row().classes('w-full justify-end mb-4'):
                ui.label(user_msg).classes('bg-gray-700 text-white rounded-3xl px-5 py-3 max-w-[85%] text-base leading-relaxed')

        # 2. Erika Response Container
        with chat_container:
            # Container for the response (Avatar + Text)
            response_row = ui.row().classes('w-full justify-start mb-6 gap-4 items-start')
            with response_row:
                # Avatar
                with ui.element('div').classes('min-w-[32px] pt-1'):
                     ui.image('/assets/Erika-AI_logo_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800')
                
                # Text Area
                response_content = ui.markdown().classes('text-gray-100 text-base leading-relaxed max-w-full overflow-hidden prose prose-invert')
                
        # 3. Streaming
        try:
            full_response = ""
            # Scroll to bottom before starting (simple js approach)
            # ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
            
            for chunk in my_brain.think_stream(user_msg):
                full_response += chunk
                response_content.set_content(full_response)
                await asyncio.sleep(0)
                
        except Exception as e:
            ui.notify(f"Error: {e}", type='negative')

    # --- Floating Input Bar ---
    # page_sticky puts it at the bottom of the viewport
    with ui.page_sticky(position='bottom', x_offset=0, y_offset=40).classes('w-full flex justify-center px-4'):
        # Input Container
        with ui.row().classes('w-full max-w-3xl bg-gray-700/90 backdrop-blur-sm rounded-full p-2 pl-4 items-center shadow-2xl border border-gray-600'):
            
            # Plus / Attach Button
            ui.button(icon='add_circle').props('flat round color=gray-400').classes('hover:text-white transition-colors')
            
            # Text Input
            text_input = ui.textarea(placeholder='Send a message') \
                .props('autogrow rows=1 borderless input-class="text-white placeholder-gray-400"') \
                .classes('col-grow text-white text-base max-h-40 mx-2') \
                .on('keydown.enter.prevent', lambda: asyncio.create_task(send())) 
                # .prevent stops the newline insert on enter
            
            # Right Actions Group
            with ui.row().classes('items-center gap-2 pr-1'):
                # Model Badge
                ui.label(my_brain.get_model_name()).classes('text-xs font-bold text-gray-400 border border-gray-500 rounded px-2 py-0.5 uppercase select-none')
                
                # Send Button
                ui.button(on_click=lambda: asyncio.create_task(send())) \
                    .props('round icon=arrow_upward color=white text-color=black') \
                    .classes('shadow-lg hover:bg-gray-200 transition-colors')

