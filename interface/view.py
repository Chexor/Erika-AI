from nicegui import ui
import asyncio
from interface.controller import Controller

def build_ui(controller: Controller):
    """
    Builds the main UI layout with a Premium Glassmorphism Aesthetic.
    "Make it a masterpiece."
    """
    
    # --- STYLING (THEME) ---
    # Colors: Deep charcoal/black backgrounds, subtle borders, backdrop blurs.
    # Accent: #3B82F6 (Blue) or #8B5CF6 (Purple) for user interactions.
    
    ui.add_head_html("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-deep: #0f1115;       /* Very dark background */
                --bg-surface: #181a20;    /* Sidebar / Panels */
                --glass-border: rgba(255, 255, 255, 0.08);
                --glass-bg: rgba(25, 27, 32, 0.6);
                --accent-primary: #3b82f6;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
            }

            body {
                background-color: var(--bg-deep);
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
                overflow: hidden;
                margin: 0;
            }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

            /* Utility Classes */
            .glass-panel {
                background: var(--glass-bg);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-right: 1px solid var(--glass-border);
            }
            
            .glass-pill {
                background: rgba(30, 32, 38, 0.7);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }
            
            .fade-in { animation: fadeIn 0.3s ease-in-out; }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Message Bubbles */
            .msg-bubble-user {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                border-radius: 18px 4px 18px 18px;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
            }
            .msg-bubble-ai {
                background: rgba(40, 44, 52, 0.8);
                border: 1px solid var(--glass-border);
                color: #e2e8f0;
                border-radius: 4px 18px 18px 18px;
            }

            /* Buttons & Inputs */
            .sidebar-btn {
                transition: all 0.2s ease;
                border-radius: 8px;
                color: var(--text-secondary);
            }
            .sidebar-btn:hover {
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-primary);
            }
            
            .input-field {
                background: transparent;
                border: none;
                outline: none;
                font-size: 0.95rem;
            }
            .input-field .q-field__native {
                color: var(--text-primary);
            }
            .input-field .q-field__native::placeholder { 
                color: var(--text-secondary); 
                opacity: 1; /* Ensure firefox matches */
            }
            
            .send-btn {
                transition: transform 0.1s;
                background: white;
                color: black;
            }
            .send-btn:hover { transform: scale(1.05); }
            .send-btn:active { transform: scale(0.95); }
        </style>
    """)

    # --- COMPONENTS ---
    
    @ui.refreshable
    def render_chat_history():
        """Renders the chat stream with high-fidelity avatars and bubbles."""
        
        # 1. Empty State - Hero
        if not controller.chat_history:
            with ui.column().classes('w-full h-full items-center justify-center pb-24 fade-in'):
                # Big Logo
                ui.image('/assets/Erika-AI_logo2_transparent.png').classes('w-32 h-32 object-contain opacity-90 mb-6 drop-shadow-2xl')
                ui.label('How can I help you today?').classes('text-2xl font-light text-gray-400')
            return

        # 2. Chat List
        for msg in controller.chat_history:
            is_user = msg['role'] == 'user'
            
            # Row Layout
            # User: Right Aligned | AI: Left Aligned
            align = 'justify-end' if is_user else 'justify-start'
            
            with ui.row().classes(f'w-full max-w-4xl mx-auto mb-8 gap-4 px-4 {align} fade-in'):
                
                # --- AI AVATAR (Left) ---
                if not is_user:
                    with ui.column().classes('items-end justify-start'):
                         ui.image('/assets/Erika-AI_logo2_transparent.png').classes('w-10 h-10 rounded-full object-contain bg-black/20 p-1 border border-white/5')

                # --- MESSAGE BUBBLE ---
                width_cls = 'max-w-[75%]' # Limit width
                bubble_cls = 'msg-bubble-user p-4' if is_user else 'msg-bubble-ai p-5'
                
                with ui.column().classes(f'{width_cls} {bubble_cls}'):
                    # AI Name Label (Optional, maybe inside bubble or above?)
                    # For now, cleaner to just have content.
                    
                    if is_user:
                         ui.label(msg['content']).classes('text-base leading-relaxed whitespace-pre-wrap')
                    else:
                        # Markdown for AI
                        # We use typography class to style headings/code blocks efficiently
                        ui.markdown(msg['content']).classes('text-base leading-relaxed w-full prose text-slate-300 prose-invert prose-p:my-1 prose-headings:text-slate-100 prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10')
                
                # --- USER AVATAR (Right) ---
                if is_user:
                     with ui.column().classes('items-end justify-start'):
                         ui.icon('person', size='sm').classes('w-9 h-9 text-gray-400 bg-white/5 rounded-full p-2')


    # --- SETTINGS MODAL ---
    with ui.dialog() as settings_dialog:
        with ui.card().classes('glass-panel w-[800px] h-[600px] p-0 flex flex-row overflow-hidden border border-white/10 rounded-xl'):
            
            # Left Nav
            with ui.column().classes('w-64 h-full bg-black/20 p-6 flex-shrink-0 border-r border-white/5 gap-2'):
                ui.label('Settings').classes('text-xl font-bold text-gray-100 mb-6 tracking-tight')
                
                tabs = ui.tabs().classes('w-full flex-col items-stretch h-full gap-2').props('vertical')
                with tabs:
                    def tab_style(name, icon):
                        t = ui.tab(name, label=name, icon=icon).classes('justify-start px-4 py-3 rounded-lg text-gray-400 data-[state=active]:bg-white/10 data-[state=active]:text-white transition-all')
                        # NiceGUI tabs styling is a bit tricky, relying on standard props
                        t.props("no-caps flat")
                        return t
                        
                    t_gen = tab_style('General', 'tune')
                    t_pers = tab_style('Personalization', 'palette')
                    t_sys = tab_style('System', 'memory')

            # Right Content
            with ui.column().classes('flex-1 h-full p-8 bg-transparent'):
                with ui.tab_panels(tabs, value='General').classes('w-full h-full bg-transparent text-gray-200 animated fade-in'):
                    
                    # --- GENERAL (UI & Window) ---
                    with ui.tab_panel('General').classes('p-0 flex flex-col gap-6'):
                        ui.label('Window Preferences').classes('text-lg font-semibold mb-2 text-white')
                        
                        def toggle_row(label, sub, val=True):
                            with ui.row().classes('w-full justify-between items-center bg-white/5 p-4 rounded-xl border border-white/5'):
                                with ui.column().classes('gap-0'):
                                    ui.label(label).classes('text-base font-medium text-gray-200')
                                    ui.label(sub).classes('text-xs text-gray-500')
                                ui.switch(value=val).props('color=blue ignore-theme')

                        toggle_row('Run on Startup', 'Launch Erika automatically when system starts')
                        toggle_row('Always on Top', 'Keep the interaction window above other apps', False)
                        
                        ui.separator().classes('bg-white/10 my-2')
                        
                        ui.label('Appearance').classes('text-lg font-semibold mb-2 text-white')
                        
                        with ui.column().classes('gap-4'):
                            ui.label('Accent Color').classes('text-sm text-gray-400')
                            with ui.row().classes('gap-3'):
                                for col in ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']:
                                    ui.button().classes('w-8 h-8 rounded-full border border-white/20').style(f'background-color: {col}')
                        
                        ui.label('Font Size').classes('text-sm text-gray-400')
                        ui.slider(min=12, max=20, value=14).props('label-always color=blue').classes('w-full max-w-xs')


                    # --- PERSONALIZATION (Erika) ---
                    with ui.tab_panel('Personalization').classes('p-0 flex flex-col gap-6'):
                        ui.label('Erika\'s Persona').classes('text-lg font-semibold mb-2 text-white')
                        
                        with ui.column().classes('w-full gap-2'):
                            ui.label('System Prompt').classes('text-sm text-gray-400')
                            ui.textarea(placeholder="You are Erika, a helpful AI assistant...", value="You are Erika, a sentient AI assistant.").classes('w-full input-field bg-white/5 rounded-xl p-2 border border-white/10').props('input-class="text-white" borderless rows=4')

                        with ui.column().classes('w-full gap-2'):
                             ui.label('Tone / Vibe').classes('text-sm text-gray-400')
                             with ui.row().classes('gap-2'):
                                 for vibe in ['Professional', 'Friendly', 'Sassy', 'Minimal']:
                                     ui.button(vibe).classes('px-4 py-1 text-xs bg-white/5 hover:bg-white/10 rounded-full border border-white/10 transition-colors')


                    # --- SYSTEM (Engine) ---
                    with ui.tab_panel('System').classes('p-0 flex flex-col gap-6'):
                        ui.label('Engine Settings').classes('text-lg font-semibold mb-2 text-white')
                        
                        # Model Info
                        with ui.item_label().classes('bg-white/5 p-4 rounded-xl border border-white/5 w-full'):
                            ui.label('Active Model').classes('text-xs text-gray-500 uppercase tracking-wider mb-1')
                            ui.row().classes('items-center justify-between w-full')
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('smart_toy', size='sm').classes('text-blue-400')
                                ui.label('Erika-beta-14b (Qwen)').classes('text-lg font-medium')
                            ui.button('Change', on_click=lambda: ui.notify('Model switching coming soon!')).classes('text-xs bg-white/10')
                        
                        # Resources Mock
                        with ui.column().classes('w-full gap-2 mt-4'):
                             ui.label('Real-time Metrics').classes('text-sm text-gray-400')
                             
                             def stat_bar(label, val, col):
                                 with ui.row().classes('w-full items-center gap-4'):
                                     ui.label(label).classes('w-16 text-xs font-mono text-gray-500')
                                     ui.linear_progress(val, show_value=False).props(f'color={col} track-color=grey-9').classes('flex-1 rounded-full h-2')
                                     ui.label(f'{int(val*100)}%').classes('w-8 text-xs text-right text-gray-400')
                                     
                             stat_bar('CPU', 0.12, 'green')
                             stat_bar('RAM', 0.45, 'orange')
                             stat_bar('VRAM', 0.82, 'red')


    # --- LAYOUT ---
    
    with ui.row().classes('w-full h-screen no-wrap gap-0'):
        
        # 1. Sidebar (Glassy)
        with ui.column().classes('w-[280px] h-full glass-panel flex flex-col p-4 flex-shrink-0 z-20'):
            
            # Header / New Chat
            with ui.button(on_click=controller.new_chat).classes('sidebar-btn w-full flex items-center justify-start px-3 py-3 mb-6 unstyled'):
                ui.icon('add', size='xs').classes('mr-3')
                ui.label('New Chat').classes('font-medium text-sm')
                
            ui.label('History').classes('text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2')
            
            # Scrollable History
            scroll_list = ui.scroll_area().classes('flex-1 w-full -mx-2 px-2')
            
            # User Account / Settings Footnote
            with ui.row().classes('w-full border-t border-white/5 pt-4 mt-auto items-center gap-3 cursor-pointer sidebar-btn p-2 rounded-lg').on('click', settings_dialog.open):
                ui.avatar('U', color='grey-800', text_color='white').classes('w-8 h-8 text-xs font-bold')
                with ui.column().classes('gap-0'):
                    ui.label('User').classes('text-sm font-medium text-gray-200')
                    ui.label('Pro Plan').classes('text-[10px] text-gray-500')
                ui.icon('settings', size='xs').classes('ml-auto text-gray-500')


        # 2. Main Content Area
        with ui.column().classes('flex-1 h-full relative flex flex-col items-center bg-gradient-to-b from-[#0f1115] to-[#13161c]'):
            
            # Top Bar (Model Branding)
            with ui.row().classes('w-full p-4 flex justify-between items-center z-10'):
                ui.label('Erika AI').classes('text-lg font-semibold text-gray-200 tracking-tight opacity-50 hover:opacity-100 transition-opacity cursor-default')
                # Optional: Model Selector
                with ui.button().classes('rounded-full bg-white/5 px-4 py-1.5 text-xs text-gray-400 hover:text-white transition-colors unstyled flex items-center gap-2'):
                    ui.label('Erika-beta')
                    ui.icon('expand_more', size='xs')

            # Chat Stream (Scroll Area)
            with ui.scroll_area().classes('w-full flex-1 p-0 pb-40') as chat_scroll:
                 # Container for messages
                 with ui.column().classes('w-full h-full pt-4'):
                    render_chat_history()
            
            # 3. Input Region (Floating Glass Pill)
            # Positioned absolute at bottom center
            with ui.row().classes('absolute bottom-10 w-full max-w-3xl px-6 justify-center z-30'):
                with ui.row().classes('glass-pill w-full rounded-[2rem] p-2 pl-6 items-center flex-nowrap gap-4'):
                    
                    # Tool Accessories (Plus Button)
                    with ui.button().classes('rounded-full text-gray-400 hover:text-white hover:bg-white/10 w-8 h-8 flex items-center justify-center transition-colors unstyled'):
                        ui.icon('add', size='sm')

                    # Text Input
                    text_input = ui.input(placeholder='Message Erika...').classes('flex-grow input-field').props('borderless autocomplete=off')
                    
                    # Right Actions
                    with ui.row().classes('items-center gap-2 pr-1'):
                        # Voice/Mic (Visual only for now)
                        # ui.icon('mic', size='xs').classes('text-gray-500 hover:text-white cursor-pointer transition-colors p-2')
                        
                        # Send Button
                        async def send():
                            val = text_input.value
                            if not val: return
                            text_input.value = ''
                            await controller.handle_user_input(val)
                            
                        with ui.button(on_click=send).classes('send-btn rounded-full w-10 h-10 flex items-center justify-center shadow-lg unstyled'):
                             ui.icon('arrow_upward', size='xs')
                        
                        text_input.on('keydown.enter', send)

    # --- LOGIC & BINDINGS ---
    
    async def refresh_view():
        """Refreshes the UI state."""
        render_chat_history.refresh()
        chat_scroll.scroll_to(percent=1.0)
        
        # Refresh Sidebar
        chats = await controller.load_history()
        scroll_list.clear()
        with scroll_list:
            if not chats:
                ui.label('No history yet').classes('text-xs text-gray-600 p-2 italic')
            else:
                for chat in chats:
                     with ui.row().classes('sidebar-btn w-full p-2 mb-1 cursor-pointer items-center gap-3').on('click', lambda c=chat['id']: controller.load_chat_session(c)):
                        ui.icon('chat_bubble_outline', size='xs').classes('text-gray-600')
                        ui.label(chat.get('preview', 'New Chat')).classes('text-sm truncate flex-1 text-gray-400')


    controller.bind_view(refresh_view)
    ui.timer(0.1, refresh_view, once=True)

