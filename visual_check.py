from nicegui import ui
from interface.components import Sidebar, HeroSection, ChatArea, InputPill

# Mock Data
mock_history = [
    {"id": "1", "preview": "Physics Simulation Help"},
    {"id": "2", "preview": "Code Refactoring"},
]

mock_messages = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I am fine, **thank you**! How can I help?"},
]

def main():
    # Setup dark mode theme
    ui.colors(primary='#5898d4', secondary='#262626', accent='#111b21', dark='#1d1d1d')
    ui.query('body').classes('bg-gray-900 text-white')

    # Layout
    Sidebar(
        history=mock_history, 
        on_select=lambda x: ui.notify(f"Selected {x}"), 
        on_new=lambda: ui.notify("New Chat"),
        on_settings=lambda: ui.notify("Settings")
    )
    
    with ui.column().classes('w-full h-screen'):
        HeroSection() # Should be hidden if messages exist, but for check we show it or ChatArea
        # ChatArea(mock_messages)
        
        InputPill(
            models=["llama3", "mistral"], 
            on_send=lambda msg: ui.notify(f"Sent: {msg}"), 
            on_tool_toggle=lambda: ui.notify("Tools")
        )

ui.run(title="Erika UI Visual Check", dark=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
