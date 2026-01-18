from nicegui import ui

# Whitelist of allowed handler methods for security (prevents arbitrary method execution)
ALLOWED_HANDLERS = frozenset({
    'set_username',
    'set_persona_prompt',
    'set_tts_voice',
    'set_tts_volume',
    'set_tts_autoplay',
    'set_context_window',
    'set_accent_color',
})

def _safe_get_handler(controller, handler_name: str):
    """Safely retrieves a handler method if it's in the whitelist."""
    if handler_name not in ALLOWED_HANDLERS:
        return None
    return getattr(controller, handler_name, None)

# --- CONFIGURATION SCHEMA ---
# Modify this dictionary to add/remove/change settings.
SETTINGS_CONFIG = [
    {
        "id": "General",
        "icon": "tune",
        "label": "General",
        "sections": [
            {
                "title": "Window Preferences",
                "items": [
                    {
                        "type": "toggle",
                        "label": "Run on Startup",
                        "sub": "Launch Erika automatically when system starts",
                        "default": True
                    },
                    {
                        "type": "toggle",
                        "label": "Always on Top",
                        "sub": "Keep the interaction window above other apps",
                        "default": False
                    }
                ]
            },
            {
                "title": "Appearance",
                "items": [
                    {
                        "type": "color_picker",
                        "label": "Accent Color",
                        "key": "accent_color",
                        "change_handler": "set_accent_color",
                        "options": ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444', '#f97316']
                    },
                    {
                        "type": "slider",
                        "label": "Font Size",
                        "min": 12,
                        "max": 20,
                        "default": 14
                    }
                ]
            }
        ]
    },
    {
        "id": "Personalization",
        "icon": "palette",
        "label": "Personalization",
        "sections": [
            {
                "title": "User Profile",
                "items": [
                    {
                        "type": "input",
                        "label": "Username",
                        "key": "username",
                        "placeholder": "Enter your name...",
                        "default": "User",
                        "change_handler": "set_username"
                    }
                ]
            },
            {
                "title": "Erika's Persona",
                "items": [
                    {
                        "type": "textarea",
                        "label": "Personality Prompt",
                        "key": "persona_prompt",
                        "placeholder": "You are Erika, a helpful AI assistant...",
                        "default": "You are Erika, a sentient AI assistant.",
                        "change_handler": "set_persona_prompt"
                    }
                ]
            }
        ]
    },
    {
        "id": "System",
        "icon": "memory",
        "label": "System",
        "sections": [
            {
                "title": "Engine Settings",
                "items": [
                    {
                        "type": "model_info",
                        "model_name": "Erika-beta-14b (Qwen)"
                    },
                    {
                        "type": "step_slider",
                        "label": "Context Length",
                        "sub": "Determines how much conversation history the AI can remember.",
                        "steps": ["4k", "8k", "16k", "32k", "64k", "128k", "256k"],
                        "default_index": 1
                    },
                    {
                        "type": "metrics",
                        "label": "Real-time Metrics"
                    }
                ]
            }
        ]
    },
    {
        "type": "separator"
    },
    {
        "type": "header",
        "label": "Tools"
    },
    {
        "id": "Voice",
        "icon": "record_voice_over",
        "label": "Voice",
        "sections": [
             {
                 "title": "Speech Synthesis",
                 "items": [
                     {
                        "type": "select",
                        "label": "Voice Model",
                        "change_handler": "set_tts_voice",
                        "key": "tts_voice",
                        "options": ['alba', 'marius', 'javert', 'jean', 'fantine', 'cosette', 'eponine', 'azelma'],
                        "default": "azelma"
                    },
                    {
                        "type": "slider", 
                        "label": "Volume", 
                        "change_handler": "set_tts_volume",
                        "key": "tts_volume",
                        "min": 0.0, 
                        "max": 1.0, 
                        "step": 0.1, 
                        "default": 1.0,
                    },
                    {
                        "type": "toggle",
                        "label": "Auto-Read Responses",
                        "sub": "Automatically speak responses when generated",
                        "default": False,
                        "change_handler": "set_tts_autoplay"
                    }
                 ]
             }
        ]
    }
]

# --- RENDERERS ---

def render_toggle(item):
    with ui.row().classes('w-full justify-between items-center bg-white/5 p-4 rounded-xl border border-white/5'):
        with ui.column().classes('gap-0'):
            ui.label(item['label']).classes('text-base font-medium text-gray-200')
            if 'sub' in item:
                ui.label(item['sub']).classes('text-xs text-gray-500')
        ui.switch(value=item.get('default', False)).props('ignore-theme')\
            .on('update:model-value', lambda: ui.notify('Setting saved', position='bottom', type='positive', color='black'))

def render_color_picker(item, controller=None):
    ui.label(item['label']).classes('text-sm text-gray-400')
    with ui.row().classes('gap-3'):
        # Get current value
        current_val = item['options'][0]
        if controller and 'key' in item:
            current_val = controller.settings.get(item['key'], current_val)

        for col in item['options']:
            # Highlight active
            is_active = (col == current_val)
            border_cls = 'border-white' if is_active else 'border-white/20'
            scale_cls = 'scale-110' if is_active else 'hover:scale-105'
            
            def make_color_handler(c):
                def _click():
                    if controller and 'change_handler' in item:
                        method = _safe_get_handler(controller, item['change_handler'])
                        if method:
                            method(c)
                            ui.notify(f'Theme updated', color=c)
                            # Apply theme immediately to current client
                            ui.colors(primary=c)
                            ui.run_javascript(f"document.documentElement.style.setProperty('--accent-primary', '{c}')")
                return _click

            ui.button().classes(f'w-8 h-8 rounded-full border-2 {border_cls} {scale_cls} transition-all')\
                .style(f'background-color: {col} !important')\
                .on('click', make_color_handler(col))

def render_slider(item, controller=None):
    ui.label(item['label']).classes('text-sm text-gray-400')
    
    val = item['default']
    if controller and 'key' in item:
         val = controller.settings.get(item['key'], val)
         
    def on_change(e):
        if controller and 'change_handler' in item:
            method = _safe_get_handler(controller, item['change_handler'])
            if method:
                method(e.value)
                ui.notify('Setting saved', position='bottom', type='positive', color='black')
                
    ui.slider(min=item['min'], max=item['max'], value=val, step=item.get('step', 1), on_change=on_change).props('label-always color=blue').classes('w-full max-w-xs')

def render_input(item, controller=None):
    ui.label(item['label']).classes('text-sm text-gray-400')

    # Resolve initial value
    val = item.get('default', '')
    if controller and 'key' in item:
        val = controller.settings.get(item['key'], val)

    def on_change(e):
        if controller and 'change_handler' in item:
            method = _safe_get_handler(controller, item['change_handler'])
            if method:
                method(e.value)

    ui.input(placeholder=item.get('placeholder', ''), value=val, on_change=on_change)\
        .classes('w-full input-field bg-white/5 rounded-xl px-2 py-1 border border-white/10')\
        .props('input-class="text-white" borderless debounce="500"')

def render_textarea(item, controller=None):
    ui.label(item['label']).classes('text-sm text-gray-400')

    val = item.get('default', '')
    if controller and 'key' in item:
        val = controller.settings.get(item['key'], val)

    def on_change(e):
        if controller and 'change_handler' in item:
            method = _safe_get_handler(controller, item['change_handler'])
            if method:
                method(e.value)

    ui.textarea(placeholder=item.get('placeholder', ''), value=val, on_change=on_change)\
        .classes('w-full input-field bg-white/5 rounded-xl p-2 border border-white/10')\
        .props('input-class="text-white" borderless rows=4 debounce="500"')

def render_buttons(item):
    ui.label(item['label']).classes('text-sm text-gray-400')
    with ui.row().classes('gap-2'):
        for opt in item['options']:
            ui.button(opt).classes('px-4 py-1 text-xs bg-white/5 hover:bg-white/10 rounded-full border border-white/10 transition-colors')

def render_model_info(item):
    with ui.item_label().classes('bg-white/5 p-4 rounded-xl border border-white/5 w-full'):
        ui.label('Active Model').classes('text-xs text-gray-500 uppercase tracking-wider mb-1')
        ui.row().classes('items-center justify-between w-full')
        with ui.row().classes('items-center gap-2'):
            ui.icon('smart_toy', size='sm').classes('text-blue-400')
            ui.label(item['model_name']).classes('text-lg font-medium')
        ui.button('Change', on_click=lambda: ui.notify('Model switching coming soon!')).classes('text-xs bg-white/10')

def render_metrics(item):
    ui.label(item['label']).classes('text-sm text-gray-400')
    
    def stat_bar(label, val, col):
        with ui.row().classes('w-full items-center gap-4'):
            ui.label(label).classes('w-16 text-xs font-mono text-gray-500')
            ui.linear_progress(val, show_value=False).props(f'color={col} track-color=grey-9').classes('flex-1 rounded-full h-2')
            ui.label(f'{int(val*100)}%').classes('w-8 text-xs text-right text-gray-400')
            
    stat_bar('CPU', 0.12, 'green')
    stat_bar('RAM', 0.45, 'orange')
    stat_bar('VRAM', 0.82, 'red')

def render_select(item, controller=None):
    with ui.column().classes('w-full gap-1'):
        ui.label(item['label']).classes('text-sm text-gray-400')

        val = item['default']
        if controller and 'key' in item:
             val = controller.settings.get(item['key'], val)

        def on_change(e):
            if controller and 'change_handler' in item:
                method = _safe_get_handler(controller, item['change_handler'])
                if method:
                    method(e.value)

        ui.select(options=item['options'], value=val, on_change=on_change).props('outlined dense options-dense behavior=menu input-class=text-white input-style="color: white !important" label-color="gray-4" color="blue-4" popup-content-class="bg-slate-900 text-white"').classes('w-full bg-slate-800/50 rounded-lg text-white')

def render_step_slider(item, controller=None):
    with ui.column().classes('w-full gap-1'):
        ui.label(item['label']).classes('text-sm text-gray-400')
        if 'sub' in item:
            ui.label(item['sub']).classes('text-xs text-gray-600 mb-2')

        steps = item['steps']
        steps = item['steps']
        default_idx = item.get('default_index', 0)
        
        # Sync with actual settings
        if controller:
             current_tokens = controller.settings.get('context_window', 8192)
             # Find closest index
             for idx, step in enumerate(steps):
                 try:
                     kb = int(step.lower().replace('k', ''))
                     if (kb * 1024) == current_tokens:
                         default_idx = idx
                         break
                 except: pass

        # Current value label
        val_label = ui.label(steps[default_idx]).classes('text-xs font-bold text-blue-400 self-end')

        def on_change(e):
            idx = int(e.value)
            if 0 <= idx < len(steps):
                val_str = steps[idx]
                val_label.set_text(val_str)
                # Update Controller - Parse "8k" -> 8192
                try:
                    kb = int(val_str.lower().replace('k', ''))
                    tokens = kb * 1024
                    if controller:
                        method = _safe_get_handler(controller, 'set_context_window')
                        if method:
                            method(tokens)
                except ValueError:
                    pass  # Invalid format, ignore

        with ui.row().classes('w-full items-center gap-4'):
            ui.slider(min=0, max=len(steps)-1, step=1, value=default_idx, on_change=on_change).props('color=blue track-color=grey-8 selection-color=blue').classes('w-full')

        # Step labels below
        with ui.row().classes('w-full justify-between px-1'):
            for step in steps:
                ui.label(step).classes('text-[10px] text-gray-600')

ITEM_RENDERERS = {
    'toggle': render_toggle,
    'color_picker': render_color_picker,
    'slider': render_slider,
    'input': render_input,
    'textarea': render_textarea,
    'buttons': render_buttons,
    'model_info': render_model_info,
    'metrics': render_metrics,
    'step_slider': render_step_slider,
    'select': render_select,
}

# --- BUILDER ---

def build_settings_modal(controller):
    """
    Builds and returns the Settings Modal dialog using the configuration dictionary.
    """
    with ui.dialog() as settings_dialog:
        with ui.card().classes('glass-panel w-full max-w-6xl h-[90vh] p-0 flex flex-row overflow-hidden border border-white/10 rounded-xl relative'):
            
            # Close Button
            ui.button(icon='close', on_click=settings_dialog.close).props('flat round dense').classes('absolute top-4 right-4 z-50 text-gray-500 hover:text-white transition-colors')

            # --- LEFT NAV ---
            with ui.column().classes('w-64 h-full bg-black/20 p-6 flex-shrink-0 border-r border-white/5 gap-2'):
                ui.label('Settings').classes('text-xl font-bold text-gray-100 mb-6 tracking-tight')
                
                tabs = ui.tabs().classes('w-full flex-col items-stretch h-full gap-2').props('vertical')
                with tabs:
                    for tab_cfg in SETTINGS_CONFIG:
                        # Handle Separator
                        if tab_cfg.get('type') == 'separator':
                            ui.separator().classes('bg-white/10 my-2')
                            continue
                        
                        # Handle Header
                        if tab_cfg.get('type') == 'header':
                             ui.label(tab_cfg['label']).classes('text-xs font-bold text-gray-500 uppercase tracking-wider px-2 mt-4 mb-2')
                             continue
                        
                        # Handle Tab
                        if 'id' in tab_cfg:
                            with ui.tab(tab_cfg['id'], label="").classes('justify-start px-4 py-3 rounded-lg text-gray-400 data-[state=active]:bg-white/10 data-[state=active]:text-white transition-all w-full h-auto min-h-0').props("no-caps flat content-class=w-full"):
                                with ui.row().classes('w-full items-center gap-3 justify-start'):
                                    ui.icon(tab_cfg['icon'], size='xs')
                                    ui.label(tab_cfg['label']).classes('text-sm font-medium')

            # --- RIGHT CONTENT ---
            with ui.column().classes('flex-1 h-full p-8 bg-transparent'):
                # Ensure the value matches the first tab id
                with ui.tab_panels(tabs, value=SETTINGS_CONFIG[0]['id']).classes('w-full h-full bg-transparent text-gray-200 animated fade-in'):
                    
                    for tab_cfg in SETTINGS_CONFIG:
                        # Skip if not a tab
                        if 'id' not in tab_cfg:
                            continue
                            
                        with ui.tab_panel(tab_cfg['id']).classes('p-0 flex flex-col gap-6'):
                            
                            for i, section in enumerate(tab_cfg['sections']):
                                ui.label(section['title']).classes('text-lg font-semibold mb-2 text-white')
                                
                                if 'items' in section:
                                    with ui.column().classes('w-full gap-4'):
                                        for item in section['items']:
                                            renderer = ITEM_RENDERERS.get(item['type'])
                                            if renderer:
                                                if item['type'] in ['step_slider', 'select', 'input', 'textarea', 'slider', 'color_picker']:
                                                    renderer(item, controller)
                                                else:
                                                    renderer(item)
                                            else:
                                                ui.label(f"Unknown type: {item['type']}").classes('text-red-500')
                                
                                # Add separator only if it's not the last section
                                if i < len(tab_cfg['sections']) - 1:
                                    ui.separator().classes('bg-white/10 my-2')

    return settings_dialog
