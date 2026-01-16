from typing import List, Callable, Dict, Any, Optional
from nicegui import ui

# --- Styles ---
DRAWER_STYLE = "background-color: #0d0d0d; border-right: 1px solid #333;"
INPUT_PILL_STYLE = "border: 1px solid #444; border-radius: 9999px; background-color: #1a1a1a;"

def Sidebar(
    history: List[Dict[str, Any]], 
    on_select: Callable[[str], None], 
    on_new: Callable[[], None],
    on_settings: Callable[[], None]
):
    """Left drawer with chat history."""
    with ui.left_drawer().style(DRAWER_STYLE).props('width=260 behavior=desktop'):
        with ui.column().classes('w-full p-2 gap-2'):
            # New Chat Button
            ui.button('New Chat', on_click=on_new).classes(
                'w-full text-white bg-transparent border border-gray-700 hover:bg-gray-800 rounded-md'
            )
            
            ui.separator().classes('bg-gray-700 my-2')
            
            # History List (Grouped by "Today" mostly for visual mock, simplistic list here)
            ui.label('History').classes('text-xs text-gray-500 font-bold px-2')
            
            with ui.scroll_area().classes('h-full w-full'):
                if not history:
                    ui.label('No history').classes('text-gray-600 text-sm px-2')
                    
                for chat in history:
                    # Using a flat button for each chat item
                    # Text truncation logic would go here or in preview data
                    ui.button(
                        chat.get('preview', 'Chat'), 
                        on_click=lambda c=chat: on_select(c.get('id'))
                    ).classes('w-full text-left text-gray-300 text-sm bg-transparent hover:bg-gray-800 rounded px-2 py-1 truncate')

            # Bottom Settings Alignment
            with ui.row().classes('w-full mt-auto p-2'):
                 ui.button(icon='settings', on_click=on_settings).props('flat round color=white')

def HeroSection():
    """Centered logo for empty state."""
    with ui.column().classes('w-full h-full justify-center items-center'):
        # Custom Avatar
        ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-32 opacity-20 mb-4 filter grayscale')
        ui.label('How can I help you today?').classes('text-2xl text-white font-semibold opacity-50')

def ChatArea(messages: List[Dict[str, Any]]):
    """Scrollable message list."""
    with ui.column().classes('w-full max-w-3xl mx-auto p-4 gap-6'):
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                with ui.row().classes('w-full justify-end'):
                    with ui.card().classes('bg-gray-700 text-white p-3 rounded-2xl rounded-tr-sm max-w-xl'):
                        ui.markdown(content)
            else:
                 with ui.row().classes('w-full justify-start items-start gap-4'):
                    ui.image('/assets/Erika-AI_logo2_transparant.png').classes('w-8 h-8 rounded-full bg-gray-800 p-1 mt-2')
                    with ui.column().classes('flex-1'):
                        ui.markdown(content).classes('text-gray-200')

def InputPill(
    models: List[str], 
    on_send: Callable[[str], None], 
    on_tool_toggle: Callable[[], None]
):
    """Floating prompt input."""
    with ui.row().classes('w-[90%] max-w-3xl mx-auto mb-6 items-center p-2 gap-2').style(INPUT_PILL_STYLE):
        # File Upload / Tools
        ui.button(on_click=on_tool_toggle, icon='add').props('flat round dense color=gray')
        
        # Web Search Toggle
        ui.button(on_click=lambda: None, icon='language').props('flat round dense color=gray')
        
        # Input Text
        text_input = ui.input(placeholder='Message Erika...').props('borderless input-class="text-white"').classes('flex-1 bg-transparent')
        
        async def send_and_clear():
            val = text_input.value
            if val:
                text_input.set_value('')
                result = on_send(val)
                if result is not None and hasattr(result, '__await__'):
                    await result

        text_input.on('keydown.enter', send_and_clear)
        
        # Model Selector (Small)
        if models:
            ui.select(models, value=models[0]).props('borderless dense options-dense behavior=menu').classes('w-32 text-xs text-gray-400')
            
        # Send Button
        ui.button(on_click=send_and_clear, icon='arrow_upward').classes('bg-white text-black rounded-full shadow-md')
