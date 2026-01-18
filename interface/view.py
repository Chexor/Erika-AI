from nicegui import ui
import asyncio
import logging
from interface.controller import Controller
from interface.settings_ui import build_settings_modal
from interface.status_ui import open_dashboard

logger = logging.getLogger(__name__)

def build_ui(controller: Controller):
    """
    Builds the main UI layout with a Premium Glassmorphism Aesthetic.
    "Make it a masterpiece."
    """
    
    # --- STYLING (THEME) ---
    # Colors: Deep charcoal/black backgrounds, subtle borders, backdrop blurs.
    # Accent: #3B82F6 (Blue) or #8B5CF6 (Purple) for user interactions.
    
    accent_color = controller.settings.get('accent_color', '#3b82f6')
    ui.colors(primary=accent_color)
    
    ui.add_head_html("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-deep: #0f1115;       /* Very dark background */
                --bg-surface: #181a20;    /* Sidebar / Panels */
                --glass-border: rgba(255, 255, 255, 0.08);
                --glass-bg: rgba(25, 27, 32, 0.6);
                --glass-bg: rgba(25, 27, 32, 0.6);
                --accent-primary: """ + accent_color + """;
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
                background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-primary) 100%);
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
            
            /* Accessibility Focus Rings */
            :focus-visible {
                outline: 2px solid var(--accent-primary);
                outline-offset: 2px;
            }
            .input-field:focus-within {
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
            }
        </style>
    """)

    # --- SCRIPT INJECTION (Code Copy & Theming) ---
    ui.add_body_html("""
        <script>
            // Theme Updater
            window.updateThemeColor = (color) => {
                document.documentElement.style.setProperty('--accent-primary', color);
            }

            // Code Block Copy Button Observer
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {
                            // Check for PRE blocks inside the node or if node is PRE
                            const pres = node.tagName === 'PRE' ? [node] : node.querySelectorAll('pre');
                            pres.forEach(pre => {
                                if (pre.querySelector('.copy-btn')) return;
                                
                                // Relative positioning for button placement
                                pre.style.position = 'relative';
                                
                                const btn = document.createElement('button');
                                btn.className = 'copy-btn absolute top-2 right-2 p-1 rounded bg-white/10 text-xs text-white/50 hover:bg-white/20 hover:text-white transition-colors';
                                btn.innerHTML = '<span class="material-icons" style="font-size: 14px">content_copy</span>';
                                btn.title = 'Copy code';
                                btn.onclick = () => {
                                    const code = pre.querySelector('code');
                                    const text = code ? code.innerText : pre.innerText;
                                    navigator.clipboard.writeText(text);
                                    btn.innerHTML = '<span class="material-icons" style="font-size: 14px">check</span>';
                                    setTimeout(() => btn.innerHTML = '<span class="material-icons" style="font-size: 14px">content_copy</span>', 2000);
                                };
                                pre.appendChild(btn);
                            });
                        }
                    });
                });
            });
            
            observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """)

    # --- COMPONENTS ---
    
    # Track UI elements for direct updates
    message_elements = {}

    @ui.refreshable
    def render_chat_history():
        """Renders the chat stream with high-fidelity avatars and bubbles."""
        message_elements.clear()
        
        # 1. Empty State - Hero
        if not controller.chat_history:
            with ui.column().classes('w-full h-full items-center justify-center pb-24 fade-in'):
                # Big Logo
                ui.image('/assets/ErikaLogo_v3.png').classes('w-32 h-32 object-contain opacity-90 mb-6 drop-shadow-2xl')
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
                         ui.image('/assets/ErikaLogo_v3.png').classes('w-10 h-10 rounded-full object-contain bg-black/20 p-1 border border-white/5')

                # --- MESSAGE COLUMN (Bubble + Actions) ---
                width_cls = 'max-w-[75%]' # Limit width
                bubble_cls = 'msg-bubble-user p-4' if is_user else 'msg-bubble-ai p-5'
                
                # Dynamic Accent Override for User Bubble
                style_override = f"background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-primary) 100%);" if is_user else ""

                with ui.column().classes(f'{width_cls} gap-1'):
                    # Pinned Indicator
                    if msg.get('pinned'):
                        with ui.row().classes('items-center gap-1 opacity-70 mb-1'):
                            ui.icon('push_pin', size='xs').classes('text-yellow-400 rotate-45')
                            ui.label('Pinned').classes('text-[10px] uppercase font-bold text-yellow-500')

                    with ui.column().classes(f'w-full {bubble_cls}').style(f'contain: layout; {style_override}'):
                        if is_user:
                            ui.label(msg['content']).classes('text-base leading-relaxed whitespace-pre-wrap')
                        else:
                            md_el = ui.markdown(msg['content']).classes('text-base leading-relaxed w-full prose text-slate-300 prose-invert prose-p:my-1 prose-headings:text-slate-100 prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10')
                            if 'id' in msg:
                                message_elements[msg['id']] = md_el
                    
                    # Footer Actions (Row)
                    if not is_user:
                        with ui.row().classes('ml-2 opacity-60 hover:opacity-100 transition-opacity gap-2 items-center'):
                             msg_id = msg.get('id')
                             content = msg.get('content')
                             is_playing = controller.speaking_msg_id == msg_id
                             
                             # TTS
                             icon_name = 'stop_circle' if is_playing else 'volume_up'
                             icon_color = 'text-red-400' if is_playing else 'text-gray-500 hover:text-blue-400'
                             ui.button(icon=icon_name, on_click=lambda mid=msg_id, txt=content: controller.toggle_tts(mid, txt)).props('flat round dense size=xs aria-label="Toggle Text to Speech"').classes(f'{icon_color} transition-colors')

                             # Copy
                             async def _copy(txt):
                                 ui.clipboard.write(txt)
                                 ui.notify('Message copied', type='info', position='top')
                             ui.button(icon='content_copy', on_click=lambda txt=content: _copy(txt)).props('flat round dense size=xs aria-label="Copy Message"').classes('text-gray-500 hover:text-white transition-colors')

                             # Pin
                             is_pinned = msg.get('pinned', False)
                             pin_icon = 'push_pin'
                             pin_color = 'text-yellow-400' if is_pinned else 'text-gray-500 hover:text-yellow-400'
                             ui.button(icon=pin_icon, on_click=lambda mid=msg_id: controller.pin_message(mid)).props('flat round dense size=xs aria-label="Pin Message"').classes(f'{pin_color} transition-colors')
                             
                             # Regenerate (Only if it's the LAST message)
                             if msg == controller.chat_history[-1]:
                                 ui.button(icon='refresh', on_click=lambda: controller.regenerate_last_message()).props('flat round dense size=xs aria-label="Regenerate Response"').classes('text-gray-500 hover:text-green-400 transition-colors')

                # --- USER AVATAR (Right) ---
                if is_user:
                     with ui.column().classes('items-end justify-start'):
                         ui.icon('person', size='sm').classes('w-9 h-9 text-gray-400 bg-white/5 rounded-full p-2')


    # --- SETTINGS MODAL ---
    # Refactored to interface/settings_ui.py
    settings_dialog = build_settings_modal(controller)


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
                user_avatar_ui = ui.avatar('U', color='grey-800', text_color='white').classes('w-8 h-8 text-xs font-bold')
                with ui.column().classes('gap-0 flex-1'):
                    user_label = ui.label('User').classes('text-sm font-medium text-gray-200')

                with ui.row().classes('items-center gap-3 ml-auto'):
                     ui.label(controller.get_logical_date_str()).classes('text-[9px] text-gray-600 font-mono tracking-tighter')
                            
                ui.icon('settings', size='xs').classes('text-gray-500')


        # 2. Main Content Area
        with ui.column().classes('flex-1 h-full relative flex flex-col items-center bg-gradient-to-b from-[#0f1115] to-[#13161c]'):
            
            # Top Bar (Model Branding)
            with ui.row().classes('w-full p-4 flex justify-between items-center z-10'):
                ui.label('Erika AI').classes('text-lg font-semibold text-gray-200 tracking-tight opacity-50 hover:opacity-100 transition-opacity cursor-default')
                
                # System Status Badge (Local vs Remote)
                is_connected = controller.brain_router.status.get('remote', False)
                mode_label = "Dream Agent (Remote)" if is_connected else "Local Engine"
                mode_color = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" if is_connected else "bg-blue-500/20 text-blue-300 border-blue-500/30"
                
                # Make Interactive
                with ui.row().classes(f'rounded-full px-3 py-1 text-[10px] font-mono font-bold uppercase tracking-wider border {mode_color} items-center gap-2 cursor-pointer transition-transform hover:scale-105').on('click', lambda: open_dashboard(controller)):
                    ui.label(mode_label)
                    # ui.icon('cloud_done' if is_connected else 'computer', size='xs')
                    with ui.tooltip():
                        ui.label(f"Routing to: {controller.brain_router.current_route or 'Auto'}")

                # Optional: Model Selector
                # with ui.button().classes('rounded-full bg-white/5 px-4 py-1.5 text-xs text-gray-400 hover:text-white transition-colors unstyled flex items-center gap-2'):
                #     ui.label('Erika-beta')
                #     ui.icon('expand_more', size='xs')

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
    
    # Persistent Delete Dialog (Robust Pattern)
    delete_target = {'id': None}
    
    with ui.dialog() as delete_dialog, ui.card().classes('bg-slate-900 border border-white/10'):
        ui.label('Delete this conversation?').classes('text-white font-bold')
        ui.label('This action cannot be undone.').classes('text-gray-400 text-sm')
        with ui.row().classes('w-full justify-end mt-4'):
             ui.button('Cancel', on_click=delete_dialog.close).props('flat text-color=white')
             
             async def perform_delete():
                 cid = delete_target['id']
                 if cid:
                     logger.info(f"UI: Deleting chat {cid}")
                     delete_dialog.close()
                     await controller.request_delete_chat(cid)
                     
             ui.button('Delete', color='red', on_click=perform_delete).props('flat')
             
    def open_delete_confirm(chat_id):
        logger.info(f"UI: Request delete for {chat_id}")
        delete_target['id'] = chat_id
        delete_dialog.open()

    async def refresh_view():
        """Refreshes the UI state."""
        render_chat_history.refresh()
        chat_scroll.scroll_to(percent=1.0)

        
        # Update User Profile
        uname = controller.settings.get('username', 'User')
        user_label.set_text(uname)
        user_avatar_ui.clear()
        with user_avatar_ui:
             ui.label(uname[0].upper() if uname else 'U')

        # Refresh Sidebar
        grouped_chats = await controller.get_grouped_history()
        scroll_list.clear()
        
        with scroll_list:
            has_history = False
            for group_name, chats in grouped_chats.items():
                if not chats: continue
                has_history = True
                
                # Group Header
                ui.label(group_name).classes('text-[10px] font-bold text-gray-600 uppercase tracking-widest mt-4 mb-2 pl-2')
                
                for chat in chats:
                     # Calculate time hint
                     preview = chat.get('preview', 'New Chat')
                     chat_id = chat['id']
                     
                     # Async Handler Factories (Closures) to preserve Context
                     def make_load_handler(cid):
                         async def _load():
                             await controller.load_chat_session(cid)
                         return _load

                     def make_delete_handler(cid):
                         def _del():
                             open_delete_confirm(cid)
                         return _del
                     
                     with ui.row().classes('sidebar-btn w-full p-2 mb-1 cursor-pointer items-center gap-3').on('click', make_load_handler(chat_id)):
                        
                        # Active Indicator
                        is_active = controller.current_chat_id == chat_id
                        icon = 'chat_bubble' if is_active else 'chat_bubble_outline'
                        icon_color = 'text-blue-400' if is_active else 'text-gray-600'
                        
                        ui.icon(icon, size='xs').classes(f'{icon_color}')
                        ui.label(preview).classes(f'text-sm truncate flex-1 { "text-white" if is_active else "text-gray-400" }')
                        
                        with ui.context_menu():
                            ui.menu_item('Delete', on_click=make_delete_handler(chat_id)).classes('text-red-400')
            
            if not has_history:
                 ui.label('No history yet').classes('text-xs text-gray-600 p-2 italic')


    async def update_stream(msg_id: str, content: str):
        """Directly updates a bubble without full re-render."""
        if msg_id in message_elements:
             try:
                 message_elements[msg_id].set_content(content)
                 chat_scroll.scroll_to(percent=1.0)
             except Exception:
                 pass # Element might be dead

    
    async def update_theme(color: str):
        """Updates the CSS variable dynamically."""
        ui.colors(primary=color)
        await ui.run_javascript(f"document.documentElement.style.setProperty('--accent-primary', '{color}')")

    controller.bind_view(refresh_view, update_stream, update_theme)
    ui.timer(0.1, refresh_view, once=True)
    ui.timer(0.1, controller.startup, once=True)
    ui.timer(60.0, controller.startup) # Heartbeat

