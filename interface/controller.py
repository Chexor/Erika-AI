from engine.brain import Brain
from engine.memory import Memory
from engine.logger import setup_engine_logger
from engine.modules.system_monitor import SystemMonitor
from engine.modules.token_counter import TokenCounter
from tools.speech_engine import SpeechEngine
from engine.network_router import BrainRouter
from engine.modules.time_keeper import TimeKeeper
from domain.subconscious.reflection_service import ReflectionService
from domain.subconscious.growth_service import GrowthService
import asyncio
import uuid
import datetime
import json
import os
import re
from typing import Optional, List, Dict, Any, Callable

logger = setup_engine_logger("INTERFACE.Controller")

# Input validation constants
MAX_INPUT_LENGTH = 50000  # Maximum characters for user input
LLM_GENERATION_TIMEOUT = 300  # 5 minutes timeout for LLM generation
CONTEXT_HEADROOM_TOKENS = 512  # Reserve space for completion

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
        
        # Subconscious Domain Services
        self.reflection_service = ReflectionService(self.brain, self.memory, self.brain_router)
        self.growth_service = GrowthService(self.brain, self.brain_router)
        
        # Speech Engine
        self.speech_engine = SpeechEngine()
        
        # Settings State
        self.settings_path = os.path.join("config", "user.json")
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from disk."""
        defaults = {
            'username': 'User',
            'context_window': 8192,
            'tts_voice': 'azelma',
            'tts_volume': 1.0,
            'tts_autoplay': False,
            'tts_offline_mode': True,
            'tts_update_days': 7
        }
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception as e:
                logger.error(f"Controller: Failed to load settings: {e}")
                 
        return defaults

    def save_settings(self):
        """Saves settings to disk."""
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Controller: Failed to save settings: {e}")
        
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
            status, content = await self.reflection_service.reflect_on_day(yesterday)
            logger.info(f"Controller: Reflection Task Status: {status}")
            
            # If successful, trigger growth
            if status == "Completed" and content:
                 await self.growth_service.evolve(content)
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
    
    def set_username(self, name: str):
        self.settings['username'] = name
        self.save_settings()
        logger.info(f"Controller: Username updated to {name}")
        
        # Instant UI Update
        if self.refresh_ui_callback:
             if asyncio.iscoroutinefunction(self.refresh_ui_callback):
                 asyncio.create_task(self.refresh_ui_callback())
             else:
                 self.refresh_ui_callback()

    def set_persona_prompt(self, text: str):
        """Updates the soul prompt and saves directly to MD file."""
        self.settings['persona_prompt'] = text
        # Save to user.json for redundancy
        self.save_settings()
        
        # Save to Authority File (Soul)
        soul_path = os.path.join("erika_home", "config", "erika_soul.md")
        try:
            os.makedirs(os.path.dirname(soul_path), exist_ok=True)
            with open(soul_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info("Controller: Updated erika_soul.md")
        except Exception as e:
            logger.error(f"Controller: Failed to save erika_soul.md: {e}")

    def set_context_window(self, tokens: int):
        """Updates the context window setting."""
        self.settings['context_window'] = tokens
        self.save_settings()
        logger.info(f"Controller: Context Window updated to {tokens} tokens")

    def set_tts_voice(self, voice: str):
        """Updates the TTS voice."""
        self.settings['tts_voice'] = voice
        self.speech_engine.set_voice(voice)
        self.save_settings()
        logger.info(f"Controller: TTS Voice updated to {voice}")

    def set_tts_volume(self, volume: float):
        """Updates TTS volume."""
        self.settings['tts_volume'] = volume
        self.speech_engine.set_volume(volume)
        self.save_settings()

    def set_tts_autoplay(self, enabled: bool):
        """Updates TTS Autoplay setting."""
        self.settings['tts_autoplay'] = enabled
        self.save_settings()
        logger.info(f"Controller: TTS Autoplay set to {enabled}")

    def _sanitize_for_tts(self, text: str) -> str:
        """Removes emojis and roleplay actions for TTS safety only."""
        if not text: return ""
        # Strip *actions* and (parentheticals)
        clean = re.sub(r'\*.*?\*', '', text)
        clean = re.sub(r'\(.*?\)', '', clean)
        # Remove emojis (Keep alphanumeric + basic punctuation)
        clean = re.sub(r'[^\w\s,.\'?!"-]', '', clean)
        return clean.strip()

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
            
            clean_text = self._sanitize_for_tts(text)
            self.speaking_msg_id = msg_id
            self.speech_engine.speak(clean_text)
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
        
    def bind_view(self, refresh_callback, stream_callback=None):
        """Binds the view refresh callback."""
        self.refresh_ui_callback = refresh_callback
        self.stream_ui_callback = stream_callback

    async def _safe_refresh(self):
        """Safely awaits the refresh callback."""
        if self.refresh_ui_callback:
            if asyncio.iscoroutinefunction(self.refresh_ui_callback):
                await self.refresh_ui_callback()
            else:
                self.refresh_ui_callback()

    async def _safe_stream(self, msg_id, content):
        """Safely calls stream updater."""
        if self.stream_ui_callback:
            if asyncio.iscoroutinefunction(self.stream_ui_callback):
                await self.stream_ui_callback(msg_id, content)
            else:
                self.stream_ui_callback(msg_id, content)

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
        """Constructs the system prompt from Core, Soul, and Growth files."""
        base_path = os.path.join("erika_home", "config")
        core_path = os.path.join(base_path, "system_core.md")
        soul_path = os.path.join(base_path, "erika_soul.md")
        growth_path = os.path.join(base_path, "erika_growth.md")
        
        # Load Core
        if os.path.exists(core_path):
            with open(core_path, 'r', encoding='utf-8') as f:
                core_text = f.read()
        else:
            core_text = "ERROR: SYSTEM CORE MISSING. ACT AS A HELPFUL ASSISTANT."
            
        # Load Soul
        if os.path.exists(soul_path):
            with open(soul_path, 'r', encoding='utf-8') as f:
                soul_text = f.read()
        else:
            soul_text = f"You are chatting with {self.settings.get('username', 'User')}."

        # Load Growth (The Living Personality)
        growth_text = ""
        if os.path.exists(growth_path):
             with open(growth_path, 'r', encoding='utf-8') as f:
                 growth_text = f.read()
            
        # Load Reflection
        reflection = self.reflection_service.get_latest_reflection()
        reflection_block = ""
        if reflection:
            reflection_block = (
                "\n### INTERNAL MEMORY: YESTERDAY'S PERSPECTIVE ###\n"
                f"{reflection}\n"
                "### END MEMORY ###\n"
            )

        return f"{core_text}\n\n{soul_text}\n\n{growth_text}\n\n{reflection_block}"

    def _calc_context_target(self, max_tokens: int) -> int:
        """Returns the target max tokens for the prompt after headroom."""
        if not max_tokens or max_tokens <= 0:
            return 0
        headroom = min(CONTEXT_HEADROOM_TOKENS, max_tokens // 4)
        if max_tokens < 64:
            return max_tokens
        return min(max_tokens, max(64, max_tokens - headroom))

    def _trim_context_messages(self, messages: list, max_tokens: int) -> tuple[list, bool]:
        """Trims oldest messages to fit within max_tokens."""
        if not messages or max_tokens <= 0:
            return messages, False

        trimmed = list(messages)
        while len(trimmed) > 1 and self.token_counter.count_messages(trimmed) > max_tokens:
            if trimmed[0].get("role") == "system" and len(trimmed) > 2:
                trimmed.pop(1)
            else:
                trimmed.pop(0)

        was_trimmed = len(trimmed) != len(messages)
        return trimmed, was_trimmed

    def _ensure_system_prompt_fits(self, messages: list, max_tokens: int) -> tuple[list, bool]:
        """Ensures the system prompt fits by truncating it if needed."""
        if not messages or max_tokens <= 0:
            return messages, False

        if messages[0].get("role") != "system":
            return messages, False

        system_content = messages[0].get("content", "")
        if not system_content:
            return messages, False

        if self.token_counter.count_messages([messages[0]]) <= max_tokens:
            return messages, False

        # Truncate by characters to approximate token reduction.
        approx_limit = max(200, max_tokens * 3)
        truncated = system_content[:approx_limit] + "\n\n[System prompt truncated to fit context window]"
        messages[0]["content"] = truncated
        return messages, True

    async def _generate_with_timeout(self, model: str, messages: list, host: str, options: dict):
        """Async generator wrapper for LLM generation with a per-chunk timeout."""
        gen = self.brain.generate_response(model=model, messages=messages, host=host, options=options)
        while True:
            try:
                chunk = await asyncio.wait_for(gen.__anext__(), timeout=LLM_GENERATION_TIMEOUT)
            except StopAsyncIteration:
                break
            except asyncio.TimeoutError:
                try:
                    await gen.aclose()
                except Exception:
                    pass
                yield {"error": f"Generation timed out after {LLM_GENERATION_TIMEOUT}s"}
                break
            yield chunk

    async def handle_user_input(self, content: str):
        """Processes user input."""
        # Input validation
        if not content or not content.strip():
            logger.warning("Controller: Empty input received, ignoring")
            return

        if len(content) > MAX_INPUT_LENGTH:
            logger.warning(f"Controller: Input too long ({len(content)} chars), truncating to {MAX_INPUT_LENGTH}")
            content = content[:MAX_INPUT_LENGTH]

        # Check for null bytes or control characters (security)
        if '\x00' in content:
            logger.warning("Controller: Null byte in input, sanitizing")
            content = content.replace('\x00', '')

        if not self.current_chat_id:
            self.new_chat()

        # 1. Add User Message
        user_msg = {"role": "user", "content": content, "id": uuid.uuid4().hex}
        self.chat_history.append(user_msg)
        
        # Log Prompt Tokens (raw history before trimming)
        raw_prompt_tokens = self.token_counter.count_messages(self.chat_history)
        logger.info(f"Controller: User Input Received. Raw Context Tokens: {raw_prompt_tokens}")

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
        context_messages = [{"role": "system", "content": system_prompt}] + self.chat_history[:-1]

        # Trim context to fit target window
        max_ctx = self.settings.get('context_window', 8192)
        target_ctx = self._calc_context_target(max_ctx)
        context_messages, trimmed = self._trim_context_messages(context_messages, target_ctx)
        context_messages, system_trimmed = self._ensure_system_prompt_fits(context_messages, target_ctx)
        prompt_tokens = self.token_counter.count_messages(context_messages)
        self.current_token_count = prompt_tokens
        if trimmed or system_trimmed:
            logger.warning("Controller: Context trimmed to fit the context window.")
        
        # Initial Refresh to show the empty bubble
        await self._safe_refresh()
        
        # Stream response
        full_response = ""
        model_to_use = self.brain_router.LOCAL_MODEL
        target_node_alias = 'local'
        if target_node == 'remote':
            model_to_use = self.brain_router.REMOTE_MODEL
            target_node_alias = 'remote'

        # Fetch Hardware-Specific Options
        gen_options = self.brain_router.get_model_options(target_node_alias)
        logger.info(f"Controller: Using Options: {gen_options}")

        try:
            # Direct iteration - asyncio.wait_for cannot wrap an async generator for 'async for'
            async for chunk in self._generate_with_timeout(model_to_use, context_messages, target_url, gen_options):
                
                # Ollama chunk format: {'message': {'role': 'assistant', 'content': '...'}, 'done': False}
                if "message" in chunk:
                    msg_obj = chunk['message']

                    content_bit = ""
                    if isinstance(msg_obj, dict):
                        content_bit = msg_obj.get('content', '')
                    elif hasattr(msg_obj, 'content'):
                        content_bit = msg_obj.content

                    # Accumulate raw output
                    full_response += content_bit

                    assistant_msg['content'] = full_response

                    # Targeted Update (No Flash)
                    await self._safe_stream(assistant_msg['id'], full_response)

                elif "error" in chunk:
                    assistant_msg['content'] = f"Error: {chunk['error']}"
                    await self._safe_refresh()
        except Exception as e:
                logger.error(f"Controller: Generation check failed: {e}")
                # Fallback if needed, but the loop is now safe from the async error
                if not full_response:
                    assistant_msg['content'] = f"Error during generation: {str(e)}"
                    await self._safe_refresh()

        # Append a brief notice if trimming occurred
        if trimmed:
            assistant_msg['content'] = (
                f"{assistant_msg['content']}\n\nNote: earlier messages were trimmed to fit the context window."
            )

        # Final Refresh to ensure complete message consistency
        await self._safe_refresh()
        
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
        
        today = TimeKeeper.get_logical_date()
        yesterday = today - datetime.timedelta(days=1)
        last_week = today - datetime.timedelta(days=7)
        
        for chat in chats:
            created_at_str = chat.get("created_at")
            if not created_at_str:
                groups["Older"].append(chat)
                continue
                
            try:
                dt = datetime.datetime.fromisoformat(created_at_str)
                logical_date = TimeKeeper.get_date_from_datetime(dt)
                
                if logical_date == today:
                    groups["Today"].append(chat)
                elif logical_date == yesterday:
                    groups["Yesterday"].append(chat)
                elif logical_date > last_week:
                    groups["This Week"].append(chat)
                else:
                    groups["Older"].append(chat)
            except ValueError:
                groups["Older"].append(chat)
                
        return groups
