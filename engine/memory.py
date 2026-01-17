import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from engine.logger import setup_engine_logger

logger = setup_engine_logger("ENGINE.Memory")

class Memory:
    def __init__(self, base_path="chats"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
    def create_chat(self) -> str:
        """Creates a new chat session and returns ID."""
        chat_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        data = {
            "id": chat_id,
            "created_at": timestamp,
            "messages": []
        }
        
        self.save_chat(chat_id, data)
        logger.info(f"Created new chat: {chat_id}")
        return chat_id

    def save_chat(self, chat_id: str, data: Dict[str, Any]):
        """Saves chat data to file."""
        file_path = os.path.join(self.base_path, f"{chat_id}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save chat {chat_id}: {e}")

    def delete_chat(self, chat_id: str) -> bool:
        """Deletes a chat file by ID."""
        file_path = os.path.join(self.base_path, f"{chat_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted chat: {chat_id}")
                return True
            else:
                logger.warning(f"Attempted to delete non-existent chat: {chat_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete chat {chat_id}: {e}")
            return False

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves chat data."""
        file_path = os.path.join(self.base_path, f"{chat_id}.json")
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat {chat_id}: {e}")
            return None

    def list_chats(self) -> List[Dict[str, Any]]:
        """Lists all chats (metadata only)."""
        chats = []
        for filename in os.listdir(self.base_path):
            if filename.endswith(".json"):
                chat_id = filename[:-5]
                data = self.get_chat(chat_id)
                if data:
                    chats.append({
                        "id": data.get("id"),
                        "created_at": data.get("created_at"),
                        "preview": (data.get("messages", []) or [{"content": "Empty"}])[0].get("content")[:50]
                    })
        return sorted(chats, key=lambda x: x.get("created_at", ""), reverse=True)
