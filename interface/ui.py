from nicegui import ui
from core.brain import process_input

def run_interface():
    @ui.page('/')
    def main_page():
        ui.markdown('# Chat with Erika')
        
        # Chat container
        chat_container = ui.column().classes('w-full')
        
        def send():
            if not text_input.value:
                return
            
            user_msg = text_input.value
            text_input.value = ''
            
            with chat_container:
                ui.chat_message(user_msg, name='You', sent=True)
                
            # Get response from brain
            response = process_input(user_msg)
            
            with chat_container:
                ui.chat_message(response, name='Erika', sent=False)
                
        # Input area
        with ui.row().classes('w-full items-center'):
            text_input = ui.input(placeholder='Type a message...').classes('flex-grow').on('keydown.enter', send)
            ui.button('Send', on_click=send)

    # Run the UI
    # Native mode uses pywebview
    ui.run(title='Erika AI', reload=False, native=True) 
