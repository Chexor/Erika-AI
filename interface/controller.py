"""interface/controller.py
The Controller layer. Orchestrates logic and updates the State.
"""
import asyncio
from typing import Coroutine
from datetime import datetime, timedelta

from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager
from core.logger import setup_logger, handle_async_exception
from interface.state import AppState

logger = setup_logger("Controller")

class ErikaController:
    DEFAULT_AVATAR = '/assets/Erika-AI_logo2_transparant.png'

    def __init__(self, state: AppState):
        self.state = state
        
        # Core Components
        self.brain = Brain()
        self.memory_manager = MemoryManager()
        self.settings_manager = SettingsManager()
        
        self._stop_flag = False
        
        # Callback hooks for the Assembler to attach to
        # e.g. when state update isn't enough (like scrolling)
        self.on_scroll_request: Coroutine = None 
        self.on_notification_request: Coroutine = None

    def startup(self):
        """Initializes the application hooks."""
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(handle_async_exception)
        logger.info("🛡️ Robust Error Handling Active (MVC Controller)")

    def shutdown(self):
        """Gracefully shuts down."""
        logger.info("🛑 Shutting down...")
        self._stop_flag = True
        # core resources cleanup if needed
        logger.info("✅ Shutdown clean.")

    def get_history_sections(self):
        """Logic to group chats."""
        chats = self.memory_manager.list_chats()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        sections = {'Today': [], 'Yesterday': [], 'Older': []}
        
        for chat in sorted(chats, key=lambda x: x.get('updated_at'), reverse=True):
            try:
                chat_date = datetime.fromisoformat(chat['updated_at']).date()
            except (ValueError, TypeError):
                chat_date = datetime.min.date()

            if chat_date == today:
                 sections['Today'].append(chat)
            elif chat_date == yesterday:
                 sections['Yesterday'].append(chat)
            else:
                 sections['Older'].append(chat)
        
        self.state.sidebar_history = sections

    async def load_chat(self, chat_id: str):
        """Loads chat history into state."""
        self.state.current_chat_id = chat_id
        chat_data = self.memory_manager.load_chat(chat_id)
        
        self.state.clear_messages()
        if chat_data:
            for msg in chat_data.get('messages', []):
                self.state.add_message({
                    'role': msg['role'],
                    'content': msg['content'],
                    'stamp': datetime.fromisoformat(msg['timestamp']).strftime('%I:%M %p'),
                    'name': 'You' if msg['role'] == 'user' else 'Erika',
                    'avatar': None if msg['role'] == 'user' else self.DEFAULT_AVATAR
                })
        
        if self.on_scroll_request:
            await self.on_scroll_request()

    def load_new_chat(self):
        self.state.current_chat_id = None
        self.state.clear_messages()

    async def handle_send(self, user_msg: str):
        if not user_msg or self.state.is_generating:
            return

        self.state.set_generating(True)
        self._stop_flag = False

        # 1. Optimistic Update (User)
        self.state.add_message({
            'role': 'user', 'content': user_msg,
            'stamp': datetime.now().strftime('%I:%M %p'), 'name': 'You', 'avatar': None
        })

        # 2. Optimistic Update (Assistant Placeholder)
        assistant_idx = len(self.state.messages)
        self.state.add_message({
            'role': 'assistant', 'content': '...', 'stamp': datetime.now().strftime('%I:%M %p'), 
            'name': 'Erika', 'avatar': self.DEFAULT_AVATAR
        })
        
        # Scroll after adding
        if self.on_scroll_request:
            await self.on_scroll_request()

        # 3. Stream
        history = self.memory_manager.get_messages(self.state.current_chat_id) if self.state.current_chat_id else []
        if len(history) > 20: history = history[-20:]
        context = history + [{'role': 'user', 'content': user_msg}]

        full_response = ""
        try:
            async for chunk in self.brain.think_stream(context):
                if self._stop_flag:
                    break
                full_response += chunk
                self.state.update_last_message(full_response)
                # Note: NiceGUI reactivity might need help for deep nested updates inside lists
                # But we will handle that in main.py binding or refresh
                
        except Exception as e:
            self.state.update_last_message(f"**Error:** {e}")
        finally:
            self.state.set_generating(False)
            self._stop_flag = False
            
            # Save
            if self.state.current_chat_id is None:
                self.state.current_chat_id = self.memory_manager.create_chat(user_msg)
            self.memory_manager.save_turn(self.state.current_chat_id, user_msg, full_response)
            
            # Update History List
            self.get_history_sections()

    def handle_stop(self):
        self._stop_flag = True
        self.notify("Stopping generation...", "warning")

    async def regenerate_last(self):
        if not self.state.messages or self.state.messages[-1]['role'] != 'assistant':
            return
        
        self.state.messages.pop() # Remove assistant msg
        
        last_user_msg = None
        for msg in reversed(self.state.messages):
            if msg['role'] == 'user':
                last_user_msg = msg['content']
                break
        
        if last_user_msg:
             # State update implies UI refresh in Main
            await self.handle_send(last_user_msg)

    def read_aloud(self, text):
        self.notify("TTS not implemented", "info")

    def notify(self, msg, type='info'):
        self.state.push_notification(msg, type)
        # Also trigger immediate callback if available
        if self.on_notification_request:
             # Fire and forget callback? Ideally async. Assuming unsafe sync call for notify
             # Wrapper in main will handle it.
             pass
