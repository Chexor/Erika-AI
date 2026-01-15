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
        
        # State Management (Copies for binding)
        self.pending_user = self.settings.user_config.copy()
        self.pending_sys = self.settings.sys_config.copy()
        
        self.dialog = ui.dialog()
        with self.dialog, ui.card().classes('w-full max-w-[850px] h-[700px] max-h-[90vh] p-0 flex flex-col bg-[#212121] border border-white/10 no-wrap'):
            # --- Header ---
            with ui.row().classes('w-full justify-between items-center p-4 border-b border-white/10 bg-[#212121]'):
                ui.label('Settings').classes('text-xl font-bold text-white')
                ui.button(icon='close', on_click=self.dialog.close).props('flat round color=white')

            # --- Body ---
            with ui.row().classes('w-full flex-grow overflow-hidden gap-0 no-wrap'):
                # Left Sidebar (Navigation)
                with ui.column().classes('w-64 h-full bg-[#171717] p-3 gap-1 border-r border-white/10'):
                    self.nav_btns = {}
                    
                    def nav_button(label, icon, tab):
                        btn = ui.button(label, icon=icon, on_click=lambda: self.show_tab(tab)) \
                            .props('flat align=left') \
                            .classes('w-full rounded-md text-sm font-medium px-3 py-2 transition-colors duration-200 text-gray-400 hover:bg-[#2f2f2f]/50')
                        self.nav_btns[tab] = btn
                        return btn

                    nav_button('Interface', 'palette', 'interface')
                    nav_button('Personalization', 'person', 'personalization')
                    nav_button('Memory', 'history', 'memory')
                    nav_button('System', 'dns', 'system')
                    nav_button('Tools', 'extension', 'tools')
                    ui.separator().classes('bg-white/10 my-2')
                    nav_button('About', 'info', 'about')
                    
                    ui.space()
                    ui.button('Save', icon='save', on_click=self.save_changes) \
                        .classes('w-full bg-blue-600 hover:bg-blue-700 text-white rounded-md mb-2')

                # Right Content (Dynamic)
                with ui.column().classes('flex-grow min-w-0 h-full p-8 overflow-y-auto bg-[#212121] text-white scroll-smooth') as self.content_area:
                    self.current_tab = 'interface'
                    self.render_interface_tab() # Default

    def save_changes(self):
        # 1. Save System Settings
        self.settings.save_system_settings(self.pending_sys)
        
        # 2. Save User Settings and Check Theme
        old_theme = self.settings.get_user_setting('theme')
        self.settings.save_user_settings(self.pending_user)
        
        # Toggle theme if changed
        if self.pending_user['theme'] != old_theme and self.on_theme_toggle:
            self.on_theme_toggle()
            
        ui.notify('Settings Saved', type='positive')
        self.dialog.close()

    def open(self):
        self.dialog.open()

    def show_tab(self, tab_name):
        self.current_tab = tab_name
        
        # Update styling
        for t, btn in self.nav_btns.items():
            if t == tab_name:
                btn.classes(remove='text-gray-400 hover:bg-[#2f2f2f]/50', add='bg-[#2f2f2f] text-white')
            else:
                btn.classes(add='text-gray-400 hover:bg-[#2f2f2f]/50', remove='bg-[#2f2f2f] text-white')
        
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
                # Add to pending settings
                current_paths = self.pending_sys.get('model_paths', [])
                if path not in current_paths:
                    current_paths.append(path)
                    self.pending_sys['model_paths'] = current_paths
                    path_input.set_value(", ".join(current_paths))
                    ui.notify(f"Added model path (Pending Save): {path}")
        except Exception as e:
            ui.notify(f"Error browsing: {e}", type='negative')

    def render_interface_tab(self):
        ui.label('Interface Settings').classes('text-2xl font-semibold mb-6')
        
        u_theme = self.pending_user.get('theme', 'dark')

        ui.label('Appearance').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        with ui.row().classes('items-center justify-between w-full mb-4'):
             ui.label('Dark Mode').classes('text-base')
             def toggle(e):
                 self.pending_user['theme'] = 'dark' if e.value else 'light'
             ui.switch(value=True if u_theme == 'dark' else False, on_change=toggle)

    def render_personalization_tab(self):
        ui.label('Personalization').classes('text-2xl font-semibold mb-6')
        
        u_name = self.pending_user.get('username', 'User')
        u_persona = self.pending_user.get('persona', '')

        ui.label('Profile').classes('text-sm font-bold text-gray-500 uppercase mb-2')
        ui.input('Nickname', value=u_name, on_change=lambda e: self.pending_user.update({'username': e.value})).classes('w-full mb-4').props('dark outlined')
        
        ui.label('System Persona').classes('text-sm font-bold text-gray-500 uppercase mb-2 mt-4')
        ui.textarea('Custom Instructions', value=u_persona, placeholder='You are a helpful assistant...', on_change=lambda e: self.pending_user.update({'persona': e.value})).classes('w-full h-32').props('dark outlined')

    def render_memory_tab(self):
        ui.label('Memory Settings').classes('text-2xl font-semibold mb-6')
        ui.label('Memory management features coming soon.').classes('text-gray-400 italic')
        
    def render_system_tab(self):
        ui.label('System Settings').classes('text-2xl font-semibold mb-6')
        
        # Load Pending Settings
        sys_model = self.pending_sys.get('model', 'llama3')
        sys_url = self.pending_sys.get('ollama_url', 'http://localhost:11434')
        sys_ctx = self.pending_sys.get('context_window', 8192)
        sys_paths = self.pending_sys.get('model_paths', [])

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
                  on_change=lambda e: self.pending_sys.update({'model': e.value})) \
            .classes('w-full mb-4').props('dark outlined behavior=menu')
            
        # Ollama URL
        ui.input('Ollama API URL', value=sys_url, on_change=lambda e: self.pending_sys.update({'ollama_url': e.value})).classes('w-full mb-4').props('dark outlined')
        
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
             with ui.row().classes('w-full justify-between text-[10px] text-gray-500 mt-1'):
                 for val in ctx_options:
                     ui.label(ctx_labels.get(val, str(val)))

        # Link slider change to setting
        def on_slider_change(e):
            val = ctx_options[int(e.value)]
            self.pending_sys['context_window'] = val
            
        slider.on_value_change(on_slider_change)

    def render_tools_tab(self):
        ui.label('Tools').classes('text-2xl font-semibold mb-6')
        ui.label('External tools configuration coming soon.').classes('text-gray-400 italic')

    def render_about_tab(self):
        ui.label('About Erika AI').classes('text-2xl font-semibold mb-6')
        ui.label('Version 1.0.0').classes('text-gray-400 mb-4')
        ui.markdown('Powered by **Ollama** and **NiceGUI**.').classes('text-gray-300 mb-4')
        ui.link('View on GitHub', '#').classes('text-blue-400 hover:text-blue-300')
