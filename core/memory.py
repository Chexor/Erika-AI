import json
import os
import uuid
from datetime import datetime

CHATS_DIR = os.path.join("erika_home", "chats")

class MemoryManager:
    def __init__(self):
        if not os.path.exists(CHATS_DIR):
            os.makedirs(CHATS_DIR)

    def create_chat(self) -> str:
        """Creates a new chat file and returns the chat_id."""
        chat_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        chat_data = {
            "id": chat_id,
            "title": "New Chat",
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": []
        }
        
        self._save_file(chat_id, chat_data)
        return chat_id

    def save_turn(self, chat_id: str, user_msg: str, ai_msg: str):
        """Saves a user/AI turn to the chat file."""
        chat_data = self.load_chat(chat_id)
        if not chat_data:
            # If chat doesn't exist for some reason, recreate it
            chat_data = {
                "id": chat_id,
                "title": "New Chat",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "messages": []
            }

        timestamp = datetime.now().isoformat()
        
        # Auto-title if first message
        if len(chat_data["messages"]) == 0:
            # Simple truncation for title
            chat_data["title"] = user_msg[:30] + ("..." if len(user_msg) > 30 else "")

        chat_data["messages"].append({
            "role": "user",
            "content": user_msg,
            "timestamp": timestamp
        })
        
        chat_data["messages"].append({
            "role": "assistant",
            "content": ai_msg,
            "timestamp": timestamp
        })
        
        chat_data["updated_at"] = timestamp
        self._save_file(chat_id, chat_data)

    def get_messages(self, chat_id: str) -> list:
        """Returns the message history for a chat, cleaned for the LLM."""
        data = self.load_chat(chat_id)
        if not data:
            return []
        
        # Return only role and content
        return [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in data.get("messages", [])
        ]

    def load_chat(self, chat_id: str) -> dict:
        """Loads a chat object by ID."""
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_chats(self) -> list:
        """Returns a list of chat metadata sorted by updated_at (newest first)."""
        chats = []
        if not os.path.exists(CHATS_DIR):
            return []
            
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(CHATS_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        chats.append({
                            "id": data.get("id"),
                            "title": data.get("title", "Untitled"),
                            "updated_at": data.get("updated_at", "")
                        })
                except Exception:
                    continue
        
        # Sort by updated_at descending
        chats.sort(key=lambda x: x["updated_at"], reverse=True)
        return chats

    def delete_chat(self, chat_id: str):
        """Deletes a chat file."""
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

    def _save_file(self, chat_id: str, data: dict):
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
