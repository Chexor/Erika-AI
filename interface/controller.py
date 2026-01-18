from engine.brain import Brain
from engine.memory import Memory
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
import logging
from typing import Optional, List, Dict, Any, Callable

logger = logging.getLogger("interface.controller")

# Input validation constants
MAX_INPUT_LENGTH = 50000  # Maximum characters for user input
LLM_GENERATION_TIMEOUT = 300  # 5 minutes timeout for LLM generation
CONTEXT_HEADROOM_TOKENS = 512  # Reserve space for completion

class Controller:
    async def shutdown(self):
        """Graceful shutdown of controller resources."""
        if self.brain:
            await self.brain.cleanup()
        logger.info("Controller: Shutdown complete.")

    def __init__(self, brain: Brain, memory: Memory):
        self.brain = brain
        self.memory = memory
        self.current_chat_id = None
        self.current_chat_created_at = None
        self.chat_history = []  # In-memory messages for UI
        self.refresh_ui_callback = None
        self.theme_update_callback = None # Callback for dynamic theming
        self.speaking_msg_id = None # Tracks active TTS message
        self._is_reflecting = False # Guard for re-entrancy
        
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
        
        # Load User Config for TTS
        self.user_config = {}
        try:
            with open(os.path.join("config", "user.json"), "r") as f:
                self.user_config = json.load(f)
        except Exception:
            pass
            
        # Speech Engine Selection
        if self.user_config.get("tts_backend") == "mcp":
            try:
                from tools.mcp_tts_client import McpTtsClient
                logger.info("Controller: Using MCP TTS Backend.")
                self.speech_engine = McpTtsClient()
            except Exception as e:
                logger.error(f"Controller: Failed to load MCP Client ({e}). Fallback to Local.")
                self.speech_engine = SpeechEngine()
        else:
             logger.info("Controller: Using Local TTS Backend.")
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
            'tts_update_days': 7,
            'accent_color': '#3b82f6'
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
        # Prevent spamming startup checks if called repeatedly
        if hasattr(self, '_startup_done') and self._startup_done:
            return
            
        logger.info("Controller: Running startup network checks...")
        await self.brain_router.update_status()
        
        # Start Speech Engine (Connects if MCP)
        if hasattr(self.speech_engine, 'start'):
             await self.speech_engine.start()
             
        self._startup_done = True
        
        # Run Reflection Check (Background)
        asyncio.create_task(self.check_legacy_reflection())

    async def check_legacy_reflection(self):
        """Checks if we need to generate a reflection for yesterday."""
        if self._is_reflecting:
            logger.debug("Controller: Reflection already in progress. Skipping heartbeat check.")
            return

        try:
            self._is_reflecting = True
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
                 logger.debug("Controller: Reflection for yesterday exists.")
        except Exception as e:
            logger.error(f"Controller: Error during reflection check: {e}")
        finally:
            self._is_reflecting = False

    def get_logical_date_str(self):
        return TimeKeeper.get_logical_date().strftime('%a, %d %b')
        
    def get_system_health(self):
        """Returns the latest system stats."""
        stats = self.system_monitor.get_system_health()
        if stats:
             stats['tokens_curr'] = self.current_token_count
             stats['tokens_max'] = self.settings.get('context_window', 8192)
        return stats

    def get_extended_status(self) -> dict:
        """Aggregates comprehensive status for the dashboard."""
        # 1. Base System Stats
        stats = self.get_system_health() or {}
        
        # 2. Brain Status
        # Check router status. If missing, assume Local is connected (since we are running)
        b_stat = self.brain_router.status
        stats['brain'] = {
            'local': b_stat.get('local', True), 
            'remote': b_stat.get('remote', False)
        }
        
        # 3. MCP Servers
        # Currently we only track TTS explicitly as a managed service
        mcp_list = []
        
        # TTS Service
        tts_mode = self.settings.get('tts_backend', 'edge')
        if tts_mode == 'mcp':
             # We can check the client readiness
             is_ready = False
             detail = "Connecting..."
             if hasattr(self.speech_engine, 'is_ready'):
                 is_ready = self.speech_engine.is_ready()
                 detail = "Ready" if is_ready else "Not Ready"
             
             mcp_list.append({
                 'name': 'TTS Engine (MCP)', 
                 'status': 'ok' if is_ready else 'error',
                 'detail': detail
             })
        else:
             mcp_list.append({
                 'name': 'TTS Engine (Edge)', 
                 'status': 'ok',
                 'detail': 'Internal Service'
             })
             
        stats['mcp'] = mcp_list
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

    
    def set_accent_color(self, color: str):
        """Updates the accent color and triggers theme refresh."""
        self.settings['accent_color'] = color
        self.save_settings()
        logger.info(f"Controller: Accent color updated to {color}")
        
        # Trigger dynamic theme update
        if self.theme_update_callback:
             if asyncio.iscoroutinefunction(self.theme_update_callback):
                 asyncio.create_task(self.theme_update_callback(color))
             else:
                 self.theme_update_callback(color)

    def update_window_geometry(self, geometry: dict):
        """Updates window position and size settings."""
        changed = False
        for key in ['x', 'y', 'width', 'height']:
            if key in geometry:
                setting_key = f"window_{key}"
                self.settings[setting_key] = geometry[key]
                changed = True
        
        if changed:
            self.save_settings()

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
            
            # Create a callback closure for this specific message
            def on_finished():
                # This runs in the speech thread, so we must be thread-safe
                if self.refresh_ui_callback:
                    # NiceGUI Apps run on an asyncio loop. We can schedule the update.
                    # Note: We need to access the main loop. Since we're in a thread, 
                    # we can't just await. We use fire-and-forget logic if possible, 
                    # or rely on ui.timer polling if nicegui loop access is hard.
                    # But better: Controller can expose a method properly.
                    self._handle_tts_finished_threadsafe(msg_id)

            self.speech_engine.speak(clean_text, on_finished)
            logger.info(f"Controller: TTS Started for {msg_id}")
            
        # Refresh to update icons
        await self._safe_refresh()

    def _handle_tts_finished_threadsafe(self, msg_id: str):
        """Thread-safe handler for TTS completion."""
        # We need to bridge from Thread -> Async Loop
        try:
             # Find running loop
             loop = asyncio.get_running_loop() 
        except RuntimeError:
             loop = None
        
        # If we can't find loop (we are in thread), we assume app.loop is available globally 
        # or we rely on the fact that nicegui wraps everything.
        # Actually, best approach is creating a small scheduled task in the global loop if accessible.
        # But since we don't have global app ref here easily, we'll try to just modify state
        # and trigger refresh via a future if possible.
        
        # SAFE APPROACH: Just update state. UI poller or next interaction will pick it up?
        # NO, user wants icon to reset.
        # Let's import app
        from nicegui import app
        if app.loop:
            app.loop.call_soon_threadsafe(self._finalize_tts_stop, msg_id)

    def _finalize_tts_stop(self, msg_id: str):
        """Final clean up on main thread."""
        if self.speaking_msg_id == msg_id:
            self.speaking_msg_id = None
            if self.refresh_ui_callback:
                asyncio.create_task(self._safe_refresh())

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
        
    def bind_view(self, refresh_callback, stream_callback=None, theme_callback=None):
        """Binds the view refresh and theme callbacks."""
        self.refresh_ui_callback = refresh_callback
        self.stream_ui_callback = stream_callback
        self.theme_update_callback = theme_callback

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

    async def regenerate_last_message(self):
        """Removes the last assistant message and regenerates it."""
        if not self.chat_history:
            return

        # Check if last message is from assistant
        last_msg = self.chat_history[-1]
        if last_msg['role'] == 'assistant':
            logger.info("Controller: Regenerating last message...")
            self.chat_history.pop() # Remove bad response
            
            # Find last user message content
            user_content = ""
            for msg in reversed(self.chat_history):
                if msg['role'] == 'user':
                    user_content = msg['content']
                    break
            
            if user_content:
                # Trigger generation again (handle_user_input logic but skipping history add)
                await self._trigger_regeneration(user_content)
            else:
                logger.warning("Controller: No user message found for regeneration.")

    async def _trigger_regeneration(self, content: str):
        """Internal helper to re-run generation flow without adding new user message."""
        # This is a focused subset of handle_user_input
        # 1. Refresh UI (removal of old msg)
        await self._safe_refresh()
        
        # 2. Create placeholder
        assistant_msg = {"role": "assistant", "content": "", "id": uuid.uuid4().hex}
        self.chat_history.append(assistant_msg)
        
        # 3. Router & Generation (Logic duplicated for safety/isolation or we could factor out)
        # Refactoring handle_user_input is better, but for now we'll call a shared core 
        # For simplicity in this step, I will factor out the generation core.
        # But wait, to avoid massive refactor risk right now, I'll direct call handle_user_input?
        # No, handle_user_input appends the user message.
        
        # Let's Extract the generation logic in next step or duplicate it carefully?
        # Duplication for this specific task reduces regression risk on main flow. 
        # Actually, let's Extract `_execute_generation` from `handle_user_input`.
        
        # RE-USE via Refactor is safer long term. 
        # I will refactor handle_user_input below to support this.
        await self._execute_generation(content, assistant_msg)

    async def pin_message(self, msg_id: str):
        """Toggles pinned state of a message."""
        for msg in self.chat_history:
            if msg.get('id') == msg_id:
                msg['pinned'] = not msg.get('pinned', False)
                self._persist()
                await self._safe_refresh()
                logger.info(f"Controller: Toggled pin for {msg_id}")
                break

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
        
        await self._execute_generation(content, assistant_msg)

    async def _execute_generation(self, user_content: str, assistant_msg: dict):
        """Core generation logic used by handle_user_input and regenerate."""
         # Router Decision
        target_node = await self.brain_router.route_query('chat', {'msg': user_content})
        target_url = self.brain_router.get_active_url(target_node)
        logger.info(f"Controller: Routing generation to {target_node} ({target_url})")
        
        # Build Context (System + History)
        system_prompt = self.build_system_prompt()
        # Note: Chat history already contains the assistant_msg placeholder at the end
        # We need context to exclude it for the prompt
        context_history = self.chat_history[:-1] # Exclude empty placeholder
        
        context_messages = [{"role": "system", "content": system_prompt}] + context_history

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
