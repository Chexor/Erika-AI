from engine.brain import Brain
from engine.memory import Memory
from engine.logger import setup_engine_logger
from engine.modules.system_monitor import SystemMonitor
from engine.modules.token_counter import TokenCounter
import asyncio

logger = setup_engine_logger("INTERFACE.Controller")

class Controller:
    def __init__(self, brain: Brain, memory: Memory):
        self.brain = brain
        self.memory = memory
        self.current_chat_id = None
        self.chat_history = []  # In-memory messages for UI
        self.refresh_ui_callback = None
        
        # System Monitor
        self.system_monitor = SystemMonitor()
        self.system_monitor.start()

        # Token Counter
        self.token_counter = TokenCounter()
        self.current_token_count = 0
        
        # Settings State
        self.settings = {
            'context_window': 8192 # Default 8k
        }
        
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
        self.current_chat_id = self.memory.create_chat()
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
            self.chat_history = data.get("messages", [])
            
            # Recount tokens
            self.current_token_count = self.token_counter.count_messages(self.chat_history)
            logger.info(f"Controller: Loaded chat {chat_id} (Tokens: {self.current_token_count})")
            
            await self._safe_refresh()

    async def handle_user_input(self, content: str):
        """Processes user input."""
        if not self.current_chat_id:
            self.new_chat()
            
        # 1. Add User Message
        user_msg = {"role": "user", "content": content}
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
        assistant_msg = {"role": "assistant", "content": ""}
        self.chat_history.append(assistant_msg)
        
        # Stream response
        full_response = ""
        async for chunk in self.brain.generate_response(model="llama3", messages=self.chat_history[:-1]):
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
                "created_at": "TODO", # Should preserve original
                "messages": self.chat_history
            }
            self.memory.save_chat(self.current_chat_id, data)
