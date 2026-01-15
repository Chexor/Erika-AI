from nicegui import ui, app
from core.brain import Brain
import asyncio

# Instantiate Brain at top level to keep it alive
my_brain = Brain()

# Connection Check on UI Load
app.on_connect(lambda: check_brain_status())

async def check_brain_status():
    is_connected = await asyncio.to_thread(my_brain.status_check)
    if not is_connected:
        ui.notify('⚠️ Brain Disconnected: Is Ollama running?', type='negative', close_button=True, timeout=0)

@ui.page('/')
def main_page():
    # Window settings via native mode happen in ui.run, 
    # but we can set some page styles here if needed.
    # ui.colors(primary='#5898d4') 
    
    with ui.column().classes('w-full h-screen no-wrap items-stretch'):
        # Header
        ui.markdown('# 🧠 Erika AI').classes('text-2xl font-bold p-4 bg-gray-100 dark:bg-gray-800')
        
        # Chat Container (Scrollable area)
        chat_container = ui.column().classes('w-full flex-grow p-4 overflow-y-auto')
        
        # Footer / Input Area
        with ui.row().classes('w-full p-4 bg-gray-100 dark:bg-gray-800 items-center gap-2'):
            text_input = ui.input(placeholder='Message Erika...').classes('flex-grow').props('outlined rounded rounded-full bg-white dark:bg-gray-700')
            send_button = ui.button(icon='send').props('round flat color=primary')

        async def send():
            user_msg = text_input.value
            if not user_msg:
                return
            
            text_input.value = ''
            
            # 1. Display User Message
            with chat_container:
                ui.chat_message(user_msg, name='You', sent=True)
            
            # Scroll to bottom
            # (NiceGUI usually handles this if we use ui.chat_message inside container?) 
            # We can force scroll manually if needed, but let's trust default layout first.
            
            # 2. Create Empty Erika Message with Spinner
            with chat_container:
                message_row = ui.chat_message(name='Erika', sent=False)
                with message_row:
                    spinner = ui.spinner('dots')
                    response_label = ui.markdown() # Placeholder for text
            
            # 3. Streaming Logic
            try:
                response_text = ""
                started = False
                
                # We iterate over the generator. 
                # Note: think_stream is synchronous generator, so we block slightly between chunks.
                # typical chunks are small, so it's fine. await asyncio.sleep(0) allows UI updates.
                for chunk in my_brain.think_stream(user_msg):
                    if not started:
                        spinner.delete()
                        started = True
                    
                    response_text += chunk
                    response_label.set_content(response_text)
                    
                    # Yield control to event loop to allow UI to redraw
                    await asyncio.sleep(0)
                    
                if not started:
                    # If no chunks were yield (e.g. immediate empty return?), remove spinner
                    spinner.delete()
                    response_label.set_content("...")

            except Exception as e:
                spinner.delete()
                response_label.set_content(f"⚠️ Error: {str(e)}")
        
        # Wire up events
        text_input.on('keydown.enter', send)
        send_button.on_click(send)

