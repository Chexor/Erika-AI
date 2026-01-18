import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from engine.logger import setup_engine_logger
from engine.modules.time_keeper import TimeKeeper

logger = setup_engine_logger("ENGINE.Memory")

class Memory:
    def __init__(self, base_path="chats"):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            
    def create_chat(self) -> Dict[str, Any]:
        """Creates a new chat session metadata (does not save to disk)."""
        chat_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        logger.info(f"Created new chat session: {chat_id}")
        return {
            "id": chat_id,
            "created_at": timestamp,
            "messages": []
        }

    def _find_chat_path(self, chat_id: str) -> Optional[str]:
        """Recursively searches for a chat file."""
        # 1. Check root (legacy/flat)
        root_path = os.path.join(self.base_path, f"{chat_id}.json")
        if os.path.exists(root_path): return root_path
        
        # 2. Check subfolders
        for root, dirs, files in os.walk(self.base_path):
            if f"{chat_id}.json" in files:
                return os.path.join(root, f"{chat_id}.json")
        return None

    def save_chat(self, chat_id: str, data: Dict[str, Any]):
        """Saves chat data to file in date-based subfolder (Circadian)."""
        # Determine folder DD-MM-YYYY
        created_at = data.get('created_at')
        if created_at:
            try:
                dt = datetime.datetime.fromisoformat(created_at)
                # Use TimeKeeper logic on the specific timestamp
                date_obj = TimeKeeper.get_date_from_datetime(dt)
                date_str = date_obj.strftime('%d-%m-%Y')
            except ValueError:
                date_str = TimeKeeper.get_logical_date().strftime('%d-%m-%Y')
        else:
            date_str = TimeKeeper.get_logical_date().strftime('%d-%m-%Y')
            
        folder_path = os.path.join(self.base_path, date_str)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        file_path = os.path.join(folder_path, f"{chat_id}.json")

        # Check for empty conversation
        if not data.get("messages"):
            # Try to find existing file to delete
            existing_path = self._find_chat_path(chat_id)
            if existing_path and os.path.exists(existing_path):
                try:
                    os.remove(existing_path)
                    logger.info(f"Deleted empty chat: {chat_id}")
                except Exception as e:
                    logger.warning(f"Failed to clean up empty chat {chat_id}: {e}")
            return
            
        # Clean up legacy location
        legacy_path = os.path.join(self.base_path, f"{chat_id}.json")
        if os.path.exists(legacy_path) and os.path.abspath(legacy_path) != os.path.abspath(file_path):
             try: os.remove(legacy_path)
             except: pass

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save chat {chat_id}: {e}")

    def delete_chat(self, chat_id: str) -> bool:
        """Deletes a chat file by ID."""
        file_path = self._find_chat_path(chat_id)
        if not file_path:
             logger.warning(f"Attempted to delete non-existent chat: {chat_id}")
             return False
             
        try:
            os.remove(file_path)
            logger.info(f"Deleted chat: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chat {chat_id}: {e}")
            return False

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves chat data."""
        file_path = self._find_chat_path(chat_id)
        if not file_path:
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat {chat_id}: {e}")
            return None

    def list_chats(self) -> List[Dict[str, Any]]:
        """Lists all chats recursively."""
        chats = []
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith(".json"):
                    try:
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        chats.append({
                            "id": data.get("id"),
                            "created_at": data.get("created_at"),
                            "preview": (data.get("messages", []) or [{"content": "Empty"}])[0].get("content")[:50]
                        })
                    except Exception as e:
                        logger.error(f"Failed to list chat {filename}: {e}")
                        
        return sorted(chats, key=lambda x: x.get("created_at", ""), reverse=True)
