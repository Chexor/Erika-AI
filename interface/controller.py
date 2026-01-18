from engine.brain import Brain
from engine.memory import Memory
from engine.logger import setup_engine_logger
from engine.modules.system_monitor import SystemMonitor
from engine.modules.token_counter import TokenCounter
from tools.speech_engine import SpeechEngine
from engine.network_router import BrainRouter
from engine.modules.time_keeper import TimeKeeper
from engine.modules.reflector import Reflector
import asyncio
import uuid
import datetime

logger = setup_engine_logger("INTERFACE.Controller")

class Controller:
    def __init__(self, brain: Brain, memory: Memory):
        self.brain = brain
        self.memory = memory
        self.current_chat_id = None
        self.current_chat_created_at = None
        self.chat_history = []  # In-memory messages for UI
        self.refresh_ui_callback = None
        self.speaking_msg_id = None # Tracks active TTS message
        
        # System Monitor
        self.system_monitor = SystemMonitor()
        self.system_monitor.start()

        # Token Counter
        self.token_counter = TokenCounter()
        self.current_token_count = 0
        
        # Brain Router (Distributed)
        self.brain_router = BrainRouter()
        
        # Reflector (Dreaming Engine)
        self.reflector = Reflector(self.brain, self.memory, self.brain_router)
        
        # Speech Engine
        self.speech_engine = SpeechEngine()
        
        # Settings State
        self.settings = {
            'context_window': 8192,
            'tts_voice': 'azelma',
            'tts_volume': 1.0,
            'tts_autoplay': False
        }
        
    async def startup(self):
        """Runs startup checks."""
        logger.info("Controller: Running startup network checks...")
        await self.brain_router.update_status()
        
        # Run Reflection Check (Background)
        asyncio.create_task(self.check_legacy_reflection())

    async def check_legacy_reflection(self):
        """Checks if we need to generate a reflection for yesterday."""
        # Current logical date
        today = TimeKeeper.get_logical_date()
        yesterday = today - datetime.timedelta(days=1)
        
        # Check if file exists
        fname = f"day_{yesterday.strftime('%d-%m-%Y')}.md"
        fpath = os.path.join("erika_home", "reflections", fname)
        
        if not os.path.exists(fpath):
            logger.info("Controller: Yesterday's reflection missing. Attempting generation...")
            # We can't block startup, but this is an async task so it's fine
            status = await self.reflector.reflect_on_day(yesterday)
            logger.info(f"Controller: Reflection Task Status: {status}")
        else:
             logger.info("Controller: Reflection for yesterday exists.")

    def get_logical_date_str(self):
        return TimeKeeper.get_logical_date().strftime('%a, %d %b')
        
    def get_system_health(self):
        """Returns the latest system stats."""
        stats = self.system_monitor.get_system_health()
        if stats:
             stats['tokens_curr'] = self.current_token_count
             stats['tokens_max'] = self.settings.get('context_window', 8192)
        return stats
    
    def set_context_window(self, tokens: int):
        """Updates the context window setting."""
        self.settings['context_window'] = tokens
        logger.info(f"Controller: Context Window updated to {tokens} tokens")

    def set_tts_voice(self, voice: str):
        """Updates the TTS voice."""
        self.settings['tts_voice'] = voice
        self.speech_engine.set_voice(voice)
        logger.info(f"Controller: TTS Voice updated to {voice}")

    def set_tts_volume(self, volume: float):
        """Updates TTS volume."""
        self.settings['tts_volume'] = volume
        self.speech_engine.set_volume(volume)

    def set_tts_autoplay(self, enabled: bool):
        """Updates TTS Autoplay setting."""
        self.settings['tts_autoplay'] = enabled
        logger.info(f"Controller: TTS Autoplay set to {enabled}")

    async def toggle_tts(self, msg_id: str, text: str):
        """Toggles TTS for a specific message."""
        # 1. If currently speaking THIS message -> STOP
        if self.speaking_msg_id == msg_id:
            self.speech_engine.stop()
            self.speaking_msg_id = None
            logger.info("Controller: TTS Stopped.")
        
        # 2. If speaking output -> STOP old, START new
        else:
            if self.speaking_msg_id:
                self.speech_engine.stop()
            
            self.speaking_msg_id = msg_id
            self.speech_engine.speak(text)
            logger.info(f"Controller: TTS Started for {msg_id}")
            
        # Refresh to update icons
        await self._safe_refresh()

    def stop_tts(self):
        """Stops any active TTS."""
        if self.speaking_msg_id:
            self.speech_engine.stop()
            self.speaking_msg_id = None
            if self.refresh_ui_callback:
                if asyncio.iscoroutinefunction(self.refresh_ui_callback):
                    asyncio.create_task(self.refresh_ui_callback())
                else:
                    self.refresh_ui_callback()
        
    def bind_view(self, refresh_callback):
        """Binds the view refresh callback."""
        self.refresh_ui_callback = refresh_callback

    async def _safe_refresh(self):
        """Safely awaits the refresh callback."""
        if self.refresh_ui_callback:
            if asyncio.iscoroutinefunction(self.refresh_ui_callback):
                await self.refresh_ui_callback()
            else:
                self.refresh_ui_callback()

    def new_chat(self):
        """Starts a new chat."""
        chat_data = self.memory.create_chat()
        self.current_chat_id = chat_data['id']
        self.current_chat_created_at = chat_data['created_at']
        self.chat_history = []
        if self.refresh_ui_callback:
             # Schedule it since new_chat is sync
             if asyncio.iscoroutinefunction(self.refresh_ui_callback):
                 asyncio.create_task(self.refresh_ui_callback())
             else:
                 self.refresh_ui_callback()
        logger.info(f"Controller: New chat started {self.current_chat_id}")

    async def load_history(self):
        """Loads list of chats for sidebar."""
        return self.memory.list_chats()

    async def load_chat_session(self, chat_id: str):
        """Loads a specific chat session."""
        data = self.memory.get_chat(chat_id)
        if data:
            self.current_chat_id = chat_id
            self.current_chat_created_at = data.get("created_at")
            self.chat_history = data.get("messages", [])
            
            # Ensure IDs exist (backward compatibility)
            for msg in self.chat_history:
                if 'id' not in msg:
                    msg['id'] = uuid.uuid4().hex
            
            # Recount tokens
            self.current_token_count = self.token_counter.count_messages(self.chat_history)
            logger.info(f"Controller: Loaded chat {chat_id} (Tokens: {self.current_token_count})")
            
            await self._safe_refresh()

    async def request_delete_chat(self, chat_id: str):
        """Deletes a chat and updates state."""
        success = self.memory.delete_chat(chat_id)
        if success:
            logger.info(f"Controller: Chat {chat_id} deleted successfully.")
            if self.current_chat_id == chat_id:
                self.new_chat()
            # Triggers full UI rebuild including sidebar
            await self._safe_refresh()
        else:
            logger.warning(f"Controller: Failed to delete chat {chat_id}")

    def build_system_prompt(self) -> str:
        """Constructs the system prompt with internal memory."""
        base_persona = (
            "You are Erika, an intelligent and empathetic AI assistant. "
            "You are chatting with Tim. "
            "Your responses should be natural, concise, and engaging."
        )
        
        reflection = self.reflector.get_latest_reflection()
        
        memory_block = ""
        if reflection:
            memory_block = (
                "\n### INTERNAL MEMORY (DO NOT REPEAT VERBATIM) ###\n"
                f"LIBRARIAN REFLECTION:\n{reflection}\n"
                "### END MEMORY ###\n"
                "Use the Internal Memory to inform your tone and first greeting, "
                "but act naturally, as if you just woke up with these thoughts."
            )
            
        return base_persona + memory_block

    async def handle_user_input(self, content: str):
        """Processes user input."""
        if not self.current_chat_id:
            self.new_chat()
            
        # 1. Add User Message
        user_msg = {"role": "user", "content": content, "id": uuid.uuid4().hex}
        self.chat_history.append(user_msg)
        
        # Log Prompt Tokens
        prompt_tokens = self.token_counter.count_messages(self.chat_history)
        self.current_token_count = prompt_tokens
        logger.info(f"Controller: User Input Received. Current Context Tokens: {prompt_tokens}")

        await self._safe_refresh()
            
        # 2. Persist
        self._persist()
        
        # 3. Generate Response
        # Create a placeholder for assistant
        assistant_msg = {"role": "assistant", "content": "", "id": uuid.uuid4().hex}
        self.chat_history.append(assistant_msg)
        
        # Router Decision
        target_node = await self.brain_router.route_query('chat', {'msg': content})
        target_url = self.brain_router.get_active_url(target_node)
        logger.info(f"Controller: Routing generation to {target_node} ({target_url})")
        
        # Build Context (System + History)
        system_prompt = self.build_system_prompt()
        # Note: chat_history contains the empty assistant msg at the end, so we slice it off
        # AND we prepend system prompt
        context_messages = [{"role": "system", "content": system_prompt}] + self.chat_history[:-1]
        
        # Stream response
        full_response = ""
        model_to_use = self.brain_router.LOCAL_MODEL
        
        async for chunk in self.brain.generate_response(model=model_to_use, messages=context_messages, host=target_url):
            # Ollama chunk format: {'message': {'role': 'assistant', 'content': '...'}, 'done': False}
            if "message" in chunk:
                content_bit = chunk['message'].get('content', '')
                full_response += content_bit
                assistant_msg['content'] = full_response
                
                if self.refresh_ui_callback:
                     await self._safe_refresh()
            
            elif "error" in chunk:
                 assistant_msg['content'] = f"Error: {chunk['error']}"
        
        # 4. Persist Final
        self._persist()
        
        # Auto-read
        if self.settings.get('tts_autoplay'):
             await self.toggle_tts(assistant_msg['id'], assistant_msg['content'])
        
        # Log Completion Tokens
        final_tokens = self.token_counter.count_messages(self.chat_history)
        completion_tokens = final_tokens - prompt_tokens
        self.current_token_count = final_tokens
        
        logger.info(f"Controller: Response complete. Completion: {completion_tokens} toks. Total: {final_tokens} toks.")

    def _persist(self):
        """Saves current state to memory."""
        if self.current_chat_id:
            data = {
                "id": self.current_chat_id,
                "created_at": self.current_chat_created_at,
                "messages": self.chat_history
            }
            self.memory.save_chat(self.current_chat_id, data)

    async def get_grouped_history(self):
        """Retrieves and groups chat history."""
        chats = self.memory.list_chats()
        groups = {
            "Today": [],
            "Yesterday": [],
            "This Week": [],
            "Older": []
        }
        
        now = datetime.datetime.now()
        today = now.date()
        yesterday = today - datetime.timedelta(days=1)
        last_week = today - datetime.timedelta(days=7)
        
        for chat in chats:
            created_at_str = chat.get("created_at")
            if not created_at_str:
                groups["Older"].append(chat)
                continue
                
            try:
                dt = datetime.datetime.fromisoformat(created_at_str)
                date = dt.date()
                
                if date == today:
                    groups["Today"].append(chat)
                elif date == yesterday:
                    groups["Yesterday"].append(chat)
                elif date > last_week:
                    groups["This Week"].append(chat)
                else:
                    groups["Older"].append(chat)
            except ValueError:
                groups["Older"].append(chat)
                
        return groups
