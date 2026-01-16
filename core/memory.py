import os
import json
import uuid
import datetime
import shutil
from typing import List, Dict, Optional, Any
from core.settings import SettingsManager
from core.logger import setup_logger

logger = setup_logger("CORE.Memory")

class MemoryManager:
    """
    Manages chat history and context persistence.
    Stores each chat session as a unique JSON file in 'chats/'.
    """

    def __init__(self, settings_manager: SettingsManager, base_path: str = "chats"):
        self.settings = settings_manager
        # Allow base_path override for testing, otherwise default to "chats" 
        # (or whatever settings dictates, but per requirements "Use erika_home/chats/ as storage root")
        self.base_path = base_path
        
        if not os.path.exists(self.base_path):
            try:
                os.makedirs(self.base_path)
            except OSError as e:
                logger.error(f"Failed to create memory directory {self.base_path}: {e}")

    def create_chat(self) -> str:
        """Creates a new chat session and returns its ID."""
        chat_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        chat_data = {
            "id": chat_id,
            "created_at": timestamp,
            "messages": []
        }
        
        self._save_chat_file(chat_id, chat_data)
        logger.info(f"Created new chat session: {chat_id}")
        return chat_id

    def save_message(self, chat_id: str, role: str, content: str) -> None:
        """Appends a message to the specified chat history."""
        chat_data = self.get_chat(chat_id)
        if not chat_data:
            logger.warning(f"Attempted to save message to non-existent chat: {chat_id}")
            return
            
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        chat_data["messages"].append(message)
        self._save_chat_file(chat_id, chat_data)

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full chat history."""
        file_path = os.path.join(self.base_path, f"{chat_id}.json")
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat {chat_id}: {e}")
            return None

    def list_all_chats(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available chats."""
        chats = []
        if not os.path.exists(self.base_path):
            return []
            
        for filename in os.listdir(self.base_path):
            if filename.endswith(".json"):
                chat_id = filename[:-5]
                # Optimization: In a real system we might index this. 
                # Here we read files to get metadata (e.g. title/preview).
                chat_data = self.get_chat(chat_id)
                if chat_data:
                    # Create a preview title if not strictly defined
                    messages = chat_data.get("messages", [])
                    preview = "Empty Chat"
                    if messages:
                         # first user message or system message
                         preview = messages[0].get("content", "")[:50]
                         
                    chats.append({
                        "id": chat_data.get("id"),
                        "created_at": chat_data.get("created_at"),
                        "preview": preview
                    })
        
        # Sort by creation time descending usually
        chats.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return chats

    def _save_chat_file(self, chat_id: str, data: Dict[str, Any]) -> None:
        """Helper to write chat file atomically."""
        file_path = os.path.join(self.base_path, f"{chat_id}.json")
        tmp_path = file_path + ".tmp"
        
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            shutil.move(tmp_path, file_path)
        except Exception as e:
            logger.error(f"Failed to save chat {chat_id}: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
