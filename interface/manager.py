"""interface/manager.py
Controller layer for Erika AI chat UI.
"""
import asyncio
from typing import Dict, List, Coroutine
from datetime import datetime, timedelta
import os

from nicegui import ui
from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager

class ChatController:
    """Handles state and data logic, completely decoupled from UI rendering."""
    
    DEFAULT_AVATAR = '/assets/Erika-AI_logo2_transparant.png'

    def __init__(self):
        # Core components
        self.brain = Brain()
        self.memory_manager = MemoryManager()
        self.settings_manager = SettingsManager()

        # Runtime state
        self.current_chat_id = None
        self.is_generating = False
        self._stop_flag = False

        # The single source of truth for the chat messages displayed in the UI
        self.messages: List[Dict] = []

        # UI Callbacks - to be set by the UI layer
        self.refresh_history_callback: Coroutine = None
        self.refresh_chat_callback: Coroutine = None
        self.stream_update_callback: Coroutine = None
        
    def get_history_sections(self) -> Dict[str, List[dict]]:
        """Return chats grouped by date for the sidebar."""
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
        return sections

    async def load_chat(self, chat_id: str):
        """Loads a chat's message history into the controller's state."""
        self.current_chat_id = chat_id
        chat_data = self.memory_manager.load_chat(chat_id)
        self.messages.clear()
        if chat_data:
            # Recreate the message structure for ui.chat_message
            for msg in chat_data.get('messages', []):
                self.messages.append({
                    'role': msg['role'],
                    'content': msg['content'],
                    'stamp': datetime.fromisoformat(msg['timestamp']).strftime('%I:%M %p'),
                    'name': 'You' if msg['role'] == 'user' else 'Erika',
                    'avatar': None if msg['role'] == 'user' else self.DEFAULT_AVATAR
                })
        
        # Trigger UI refresh
        if self.refresh_history_callback:
            asyncio.create_task(self.refresh_history_callback())
        if self.refresh_chat_callback:
            asyncio.create_task(self.refresh_chat_callback())

    def load_new_chat(self):
        """Resets the state to a new, empty chat."""
        self.current_chat_id = None
        self.messages.clear()
        if self.refresh_history_callback:
            asyncio.create_task(self.refresh_history_callback())
        if self.refresh_chat_callback:
            asyncio.create_task(self.refresh_chat_callback())

    async def send_message(self, user_msg: str):
        """Handles the logic of sending a message and getting a response."""
        if not user_msg or self.is_generating:
            return

        self.is_generating = True
        self._stop_flag = False

        # Add user message to the UI
        self.messages.append({
            'role': 'user', 'content': user_msg,
            'stamp': datetime.now().strftime('%I:%M %p'), 'name': 'You', 'avatar': None
        })

        # Add a placeholder for the assistant's response
        assistant_message_id = len(self.messages)
        self.messages.append({
            'role': 'assistant', 'content': '...', 'stamp': datetime.now().strftime('%I:%M %p'),
            'name': 'Erika', 'avatar': self.DEFAULT_AVATAR
        })
        
        # New: Trigger a chat refresh to show the new messages
        if self.refresh_chat_callback:
            await self.refresh_chat_callback()

        # Get context and stream response
        history = self.memory_manager.get_messages(self.current_chat_id) if self.current_chat_id else []
        if len(history) > 20: history = history[-20:]
        context = history + [{'role': 'user', 'content': user_msg}]

        full_response = ""
        try:
            async for chunk in self.brain.think_stream(context):
                if self._stop_flag:
                    break
                full_response += chunk
                # Update the content of the assistant's message in place
                self.messages[assistant_message_id]['content'] = full_response
                # Trigger stream update
                if self.stream_update_callback:
                    await self.stream_update_callback(full_response)
        except Exception as e:
            self.messages[assistant_message_id]['content'] = f"**Error:** {e}"
        finally:
            self.is_generating = False
            self._stop_flag = False

            # Save the completed conversation turn
            if self.current_chat_id is None:
                self.current_chat_id = self.memory_manager.create_chat(user_msg)
            self.memory_manager.save_turn(self.current_chat_id, user_msg, full_response)

            # Trigger a refresh of the sidebar
            if self.refresh_history_callback:
                await self.refresh_history_callback()

    def stop_generation(self):
        """Sets the flag to stop the current generation stream."""
        self._stop_flag = True
        ui.notify('Stopping generation...')
