from nicegui import ui
import asyncio

class StatusDashboard:
    def __init__(self, controller):
        self.controller = controller
        self.dialog = ui.dialog()
        with self.dialog, ui.card().classes('bg-[#1a1c23] border border-white/10 w-full max-w-4xl p-0 overflow-hidden'):
             # Header
             with ui.row().classes('w-full bg-white/5 p-4 items-center justify-between border-b border-white/5'):
                 with ui.row().classes('items-center gap-3'):
                     ui.icon('monitor_heart', size='sm').classes('text-blue-400')
                     ui.label('System Status Dashboard').classes('text-lg font-medium text-white')
                 ui.button(icon='close', on_click=self.dialog.close).props('flat round dense text-color=grey')
             
             # Content
             self.content_area = ui.column().classes('w-full p-6 gap-6')
             
             # Footer
             with ui.row().classes('w-full bg-black/20 p-3 items-center justify-end border-t border-white/5'):
                 ui.label('Updates automatically every 1s').classes('text-xs text-gray-600')

    def open(self):
        self.dialog.open()
        self.render()
        self.timer = ui.timer(1.0, self.update, active=True)
        # Stop timer when dialog closes
        self.dialog.on('close', lambda: self.timer.deactivate())

    def render(self):
        with self.content_area:
            self.content_area.clear()
            
            # Grid Layout
            with ui.grid(columns=3).classes('w-full gap-4'):
                # 1. Local System
                with ui.card().classes('bg-white/5 border border-white/5 p-4 gap-2'):
                    ui.label('Local System').classes('text-xs font-bold text-gray-400 uppercase tracking-wider')
                    self.cpu_label = ui.label('CPU: --%').classes('text-sm text-gray-300 font-mono')
                    self.ram_label = ui.label('RAM: --%').classes('text-sm text-gray-300 font-mono')
                    self.gpu_label = ui.label('GPU: --%').classes('text-sm text-gray-300 font-mono')
                    self.vram_label = ui.label('VRAM: --%').classes('text-sm text-gray-300 font-mono')

                # 2. Conversation
                with ui.card().classes('bg-white/5 border border-white/5 p-4 gap-2'):
                    ui.label('Active Conversation').classes('text-xs font-bold text-gray-400 uppercase tracking-wider')
                    self.ctx_label = ui.label('Context: -- / --').classes('text-sm text-gray-300 font-mono')
                    self.ctx_bar = ui.linear_progress(0).props('color=blue track-color=grey-8').classes('h-2 rounded-full mt-2')
                
                # 3. Brain Status
                with ui.card().classes('bg-white/5 border border-white/5 p-4 gap-2'):
                    ui.label('Brain Link').classes('text-xs font-bold text-gray-400 uppercase tracking-wider')
                    self.local_status = ui.label('Consciousness (Local): --').classes('text-sm text-gray-300')
                    self.remote_status = ui.label('Subconscious (Remote): --').classes('text-sm text-gray-300')

            # MCP Servers (Full Width)
            with ui.card().classes('bg-white/5 border border-white/5 p-4 w-full gap-2'):
                 ui.label('MCP Capabilities').classes('text-xs font-bold text-gray-400 uppercase tracking-wider mb-2')
                 self.mcp_container = ui.column().classes('w-full gap-2')

            self.update() # Initial data fetch

    def update(self):
        if not self.dialog.value: return # Don't update if closed
        
        try:
            stats = self.controller.get_extended_status()
            
            # 1. Local System
            self.cpu_label.set_text(f"CPU:  {stats['cpu']:>5.1f}%")
            self.ram_label.set_text(f"RAM:  {stats['ram']:>5.1f}%")
            
            gpu = stats.get('gpu')
            vram = stats.get('vram')
            self.gpu_label.set_text(f"GPU:  {gpu:>5.1f}%" if gpu is not None else "GPU:  N/A")
            self.vram_label.set_text(f"VRAM: {vram:>5.1f}%" if vram is not None else "VRAM: N/A")
            
            # 2. Context
            curr = stats.get('tokens_curr', 0)
            maxx = stats.get('tokens_max', 8192)
            pct = curr / maxx if maxx > 0 else 0
            self.ctx_label.set_text(f"Context: {curr} / {maxx} ({pct*100:.1f}%)")
            self.ctx_bar.set_value(pct)
            
            # 3. Brain
            l_stat = "Online" if stats['brain']['local'] else "Offline"
            r_stat = "Online" if stats['brain']['remote'] else "Offline"
            
            self.local_status.set_text(f"Consciousness (Local): {l_stat}")
            self.local_status.classes(remove='text-green-400 text-red-400', add='text-green-400' if stats['brain']['local'] else 'text-red-400')
            
            self.remote_status.set_text(f"Subconscious (Remote): {r_stat}")
            self.remote_status.classes(remove='text-green-400 text-red-400', add='text-green-400' if stats['brain']['remote'] else 'text-red-400')
            
            # 4. MCP
            self.mcp_container.clear()
            with self.mcp_container:
                for srv in stats['mcp']:
                     with ui.row().classes('w-full items-center justify-between bg-black/20 p-2 rounded'):
                         with ui.row().classes('items-center gap-2'):
                             color = 'green' if srv['status'] == 'ok' else 'red'
                             ui.icon('circle', size='xs').classes(f'text-{color}-500 text-[8px]')
                             ui.label(srv['name']).classes('text-sm font-medium text-gray-200')
                         
                         ui.label(srv.get('detail', '')).classes('text-xs text-gray-500 font-mono')

        except Exception as e:
            print(f"Dashboard Update Error: {e}")

def open_dashboard(controller):
    dash = StatusDashboard(controller)
    dash.open()
