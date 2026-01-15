from nicegui import ui, app
from core.settings import SettingsManager
import requests
import asyncio
import tkinter as tk
from tkinter import filedialog

class SettingsModal:
    def __init__(self, settings_manager: SettingsManager, on_theme_toggle=None):
        self.settings = settings_manager
        self.on_theme_toggle = on_theme_toggle
        self.dialog = ui.dialog()
        with self.dialog, ui.card().classes('w-[90vw] max-w-[800px] h-[80vh] max-h-[600px] p-0 flex flex-col bg-gray-900 border border-gray-700 no-wrap'):
            # --- Header ---
            with ui.row().classes('w-full justify-between items-center p-4 border-b border-gray-700 bg-gray-800'):
                ui.label('Settings').classes('text-xl font-bold text-white')
                ui.button(icon='close', on_click=self.dialog.close).props('flat round color=white')

            # --- Body ---
            with ui.row().classes('w-full flex-grow overflow-hidden gap-0 no-wrap'):
                # Left Sidebar (Navigation)
                with ui.column().classes('w-64 h-full bg-gray-800/50 p-4 gap-2 border-r border-gray-700'):
                    self.nav_interface = ui.button('Interface', on_click=lambda: self.show_tab('interface')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')
                    self.nav_personalization = ui.button('Personalization', on_click=lambda: self.show_tab('personalization')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')
                    self.nav_memory = ui.button('Memory', on_click=lambda: self.show_tab('memory')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')
                    self.nav_system = ui.button('System', on_click=lambda: self.show_tab('system')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')
                    self.nav_tools = ui.button('Tools', on_click=lambda: self.show_tab('tools')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')
                    self.nav_about = ui.button('About', on_click=lambda: self.show_tab('about')).props('flat align=left').classes('w-full text-gray-300 hover:bg-gray-700 hover:text-white rounded-md')

                # Right Content (Dynamic)
                with ui.column().classes('flex-grow min-w-0 h-full p-8 overflow-y-auto bg-gray-900 text-white') as self.content_area:
                    self.render_interface_tab() # Default

    def open(self):
        self.dialog.open()

    def show_tab(self, tab_name):
        self.content_area.clear()
        with self.content_area:
            if tab_name == 'interface':
                self.render_interface_tab()
            elif tab_name == 'personalization':
                self.render_personalization_tab()
            elif tab_name == 'memory':
                self.render_memory_tab()
            elif tab_name == 'system':
                self.render_system_tab()
            elif tab_name == 'tools':
                self.render_tools_tab()
            elif tab_name == 'about':
                self.render_about_tab()

    def _fetch_ollama_models(self):
        url = self.settings.get_system_setting('ollama_url', 'http://localhost:11434')
        try:
            resp = requests.get(f"{url}/api/tags", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'] for m in data.get('models', [])]
        except Exception:
            return []
        return []

    async def _browse_directory(self, path_input):
        try:
            # Run tkinter dialog in thread to avoid blocking main loop
            root = tk.Tk()
            root.withdraw() # Hide main window
            root.attributes('-topmost', True) # Bring to front
            
            # Use asyncio to run the blocking call
            path = await asyncio.to_thread(filedialog.askdirectory)
            
            root.destroy()
            
            if path:
                # Add to settings
                current_paths = self.settings.get_system_setting('model_paths', [])
                if path not in current_paths:
                    current_paths.append(path)
                    self.settings.set_system_setting('model_paths', current_paths)
                    path_input.set_value(", ".join(current_paths))
                    ui.notify(f"Added model path: {path}")
        except Exception as e:
            ui.notify(f"Error browsing: {e}", type='negative')

    def render_interface_tab(self):
        ui.label('Interface Settings').classes('text-2xl font-semibold mb-6')
        
        u_theme = self.settings.get_user_setting('theme', 'dark')

        ui.label('Appearance').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        with ui.row().classes('items-center justify-between w-full mb-4'):
             ui.label('Dark Mode').classes('text-base')
             def toggle(e):
                 if self.on_theme_toggle:
                     self.on_theme_toggle()
             ui.switch(value=True if u_theme == 'dark' else False, on_change=toggle)

    def render_personalization_tab(self):
        ui.label('Personalization').classes('text-2xl font-semibold mb-6')
        
        u_name = self.settings.get_user_setting('username', 'User')
        u_persona = self.settings.get_user_setting('persona', '')

        ui.label('Profile').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        ui.input('Nickname', value=u_name, on_change=lambda e: self.settings.set_user_setting('username', e.value)).classes('w-full mb-4').props('dark outlined')
        
        ui.label('System Persona').classes('text-sm font-bold text-gray-500 uppercase mb-2 mt-4')
        ui.textarea('Custom Instructions', value=u_persona, placeholder='You are a helpful assistant...', on_change=lambda e: self.settings.set_user_setting('persona', e.value)).classes('w-full h-32').props('dark outlined')

    def render_memory_tab(self):
        ui.label('Memory Settings').classes('text-2xl font-semibold mb-6')
        ui.label('Memory management features coming soon.').classes('text-gray-400 italic')
        
    def render_system_tab(self):
        ui.label('System Settings').classes('text-2xl font-semibold mb-6')
        
        # Load Settings
        sys_model = self.settings.get_system_setting('model', 'llama3')
        sys_url = self.settings.get_system_setting('ollama_url', 'http://localhost:11434')
        sys_ctx = self.settings.get_system_setting('context_window', 8192)
        sys_paths = self.settings.get_system_setting('model_paths', [])

        # Fetch Available Models
        available_models = self._fetch_ollama_models()
        if not available_models:
             available_models = [sys_model, 'llama3', 'mistral', 'gemma'] # Fallbacks
        
        # Ensure current model is valid
        if sys_model not in available_models:
            available_models.append(sys_model)

        # --- MODEL LOCATION ---
        ui.label('Model Location').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        ui.label('Location where models are stored.').classes('text-xs text-gray-400 mb-2')
        
        with ui.row().classes('w-full items-center gap-2 mb-6'):
            # Just display them as a comma separated string for now
            path_str = ", ".join(sys_paths)
            path_input = ui.input(value=path_str).classes('flex-grow').props('dark outlined readonly')
            ui.button('Browse', icon='folder_open', on_click=lambda: asyncio.create_task(self._browse_directory(path_input))) \
                .classes('bg-gray-700 text-white hover:bg-gray-600')

        # --- MODEL CONFIG ---
        ui.label('LLM Configuration').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        
        # Model Name (Dropdown)
        ui.select(available_models, value=sys_model, label='Model Name', 
                  on_change=lambda e: self.settings.set_system_setting('model', e.value)) \
            .classes('w-full mb-4').props('dark outlined behavior=menu')
            
        # Ollama URL
        ui.input('Ollama API URL', value=sys_url, on_change=lambda e: self.settings.set_system_setting('ollama_url', e.value)).classes('w-full mb-4').props('dark outlined')
        
        # Context Window (Slider)
        ui.label('Context Length').classes('text-sm font-bold text-gray-500 uppercase mb-1 mt-2')
        ui.label('Context length determines how much of your conversation local LLMs can remember.').classes('text-xs text-gray-400 mb-4')
        
        # Slider Scale: 4k to 128k
        # We use a logarithmic-like mapping or just fixed steps
        ctx_options = [4096, 8192, 16384, 32768, 65536, 131072]
        ctx_labels = {4096: '4k', 8192: '8k', 16384: '16k', 32768: '32k', 65536: '64k', 131072: '128k'}
        
        # Find closed index
        current_idx = 1 # Default 8k
        if sys_ctx in ctx_options:
            current_idx = ctx_options.index(sys_ctx)
            
        with ui.row().classes('w-full items-center px-2'):
             slider = ui.slider(min=0, max=len(ctx_options)-1, step=1, value=current_idx) \
                .classes('w-full') \
                .props('markers snap label')
             
             # Labels row
             with ui.row().classes('w-full justify-between text-xs text-gray-500 mt-1'):
                 for val in ctx_options:
                     ui.label(ctx_labels.get(val, str(val)))

        # Link slider change to setting
        def on_slider_change(e):
            val = ctx_options[int(e.value)]
            self.settings.set_system_setting('context_window', val)
            ui.notify(f"Context Window set to {val}", type='info')
            
        slider.on_change(on_slider_change)

    def render_tools_tab(self):
        ui.label('Tools').classes('text-2xl font-semibold mb-6')
        ui.label('External tools configuration coming soon.').classes('text-gray-400 italic')

    def render_about_tab(self):
        ui.label('About Erika AI').classes('text-2xl font-semibold mb-6')
        ui.label('Version 1.0.0').classes('text-gray-400 mb-4')
        ui.markdown('Powered by **Ollama** and **NiceGUI**.').classes('text-gray-300 mb-4')
        ui.link('View on GitHub', '#').classes('text-blue-400 hover:text-blue-300')
