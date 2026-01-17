import asyncio
from typing import Optional, Callable, Awaitable
from interface.state import AppState
from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager
from core.logger import setup_logger

logger = setup_logger("INTERFACE.Controller")

class ErikaController:
    """
    Orchestrates the application logic.
    - Bridges 'interface/state.py' (Model) with 'core/' (Backend).
    - Handles user actions and updates state.
    """

    def __init__(self, state: AppState, settings_manager: Optional[SettingsManager] = None, memory_manager: Optional[MemoryManager] = None):
        self.state = state
        self.settings = settings_manager if settings_manager else SettingsManager()
        self.memory = memory_manager if memory_manager else MemoryManager(self.settings)
        self.brain = Brain(self.settings)
        
        # Callback to trigger UI refresh (dependency injection by Assembler ideally)
        self.refresh_ui: Optional[Callable[[], Awaitable[None]]] = None
        
        # Initialize
        self._load_initial_data()

    def cleanup(self):
        """Clean up resources before shutdown."""
        logger.info("Controller: Cleanup initiated.")
        # Cancel any active generation tasks here if we track them
        # For now, we just log. 
        # Future: self.brain.cancel_generation()
        pass

    def _load_initial_data(self):
        # Load last chat or settings?
        self.state.selected_model = self.settings.get("user", "model", "llama3")

    async def handle_send(self, content: str):
        if not content.strip():
            return
            
        # 0. Core Loop: Prepare context
        # If no chat, create one? For now assume ephemeral or create on fly.
        # Ideally we map state messages to a chat ID.
        # Let's create a chat if empty list (first msg)
        current_chat_id = getattr(self.state, 'current_chat_id', None)
        if not current_chat_id:
            current_chat_id = self.memory.create_chat()
            setattr(self.state, 'current_chat_id', current_chat_id)

        # 1. Update State (Optimistic User Msg)
        self.state.messages.append({'role': 'user', 'content': content})
        self.memory.save_message(current_chat_id, "user", content)
        
        if self.refresh_ui: await self.refresh_ui()

        # 2. Inference
        self.state.is_loading = True
        if self.refresh_ui: await self.refresh_ui()

        try:
            # Prepare messages for Brain
            # We strictly pass list of dicts.
            # Assuming Brain accepts state['messages'] format.
            context_messages = self.state.messages
            
            # Create placeholder for assistant response
            self.state.messages.append({'role': 'assistant', 'content': ''})
            full_response = ""
            
            # Stream response
            # Note: think_stream is a generator. We must iterate it.
            # If it's synchronous generator, we block.
            # If Brain.think_stream is just `yield`, it's sync. 
            # To be non-blocking in NiceGUI, we should run it in executor or iterate with small sleeps if sync.
            # HOWEVER, Phase 1.4 implementation was `yield`. 
            # We wrap iteration in a way that doesn't freeze UI if possible, 
            # generally standard loop is fine if fast, but for LLM, we need async.
            # But Brain is currently sync generator.
            # We will iterate it directly.
            
            for chunk in self.brain.think_stream(context_messages[:-1]): # Exclude the empty assistant msg we just added? No, Brain needs history.
                # Actually we shouldn't pass the empty assistant placeholder.
                # So we pass up to the user message.
                
                full_response += chunk
                self.state.messages[-1]['content'] = full_response
                
                # Signal UI update
                if self.refresh_ui: await self.refresh_ui()
                
                # Yield control to event loop (critical for UI responsiveness)
                await asyncio.sleep(0.01)
                
            # 3. Save Final
            self.memory.save_message(current_chat_id, "assistant", full_response)
            
        except Exception as e:
            logger.error(f"Error in handle_send: {e}")
            self.state.messages.append({'role': 'system', 'content': f"Error: {str(e)}"})
            
        finally:
            self.state.is_loading = False
            if self.refresh_ui: await self.refresh_ui()

    async def handle_new_chat(self):
        self.state.messages = []
        setattr(self.state, 'current_chat_id', None) # Clear ID
        if self.refresh_ui: await self.refresh_ui()

    async def load_all_chats(self):
        """Loads and sorts all chat history for the sidebar."""
        raw_chats = self.memory.list_all_chats()
        # Sort by created_at desc (already done by memory, but good to ensure)
        # We might want to group them here or in the UI. 
        # Components.Sidebar expects a list, so let's just pass the list.
        self.state.sidebar_history = raw_chats
        if self.refresh_ui: await self.refresh_ui()

    async def load_chat(self, chat_id: str):
        """Loads a specific chat into the main view."""
        self.state.is_loading = True
        if self.refresh_ui: await self.refresh_ui()
        
        try:
            chat_data = self.memory.get_chat(chat_id)
            if chat_data:
                self.state.messages = chat_data.get("messages", [])
                setattr(self.state, 'current_chat_id', chat_id)
            else:
                logger.warning(f"Chat {chat_id} not found.")
                
        except Exception as e:
            logger.error(f"Error loading chat {chat_id}: {e}")
            
        finally:
            self.state.is_loading = False
            if self.refresh_ui: await self.refresh_ui()
