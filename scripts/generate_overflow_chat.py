
import json
import uuid
import os
from datetime import datetime, timedelta

CHATS_DIR = "erika_home/chats"
os.makedirs(CHATS_DIR, exist_ok=True)

def generate_chat():
    chat_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    messages = []
    
    # Message 0 (User) - The Secret (Should be lost)
    messages.append({
        "role": "user",
        "content": "The secret password is 'OBSIDIAN'. Remember it.",
        "timestamp": timestamp
    })
    # Message 1 (AI)
    messages.append({
        "role": "assistant",
        "content": "Okay, I will remember the password 'OBSIDIAN'.",
        "timestamp": timestamp
    })
    
    # Generate 22 filler messages (11 turns)
    # Total messages before new input = 2 + 22 = 24.
    # Sliding window is 20.
    # It will keep the last 20.
    # So messages [0, 1, 2, 3] will be dropped. (Keeping 4 to 23).
    
    for i in range(11):
        messages.append({
            "role": "user",
            "content": f"Filler message number {i+1}",
            "timestamp": timestamp
        })
        messages.append({
            "role": "assistant",
            "content": f"Acknowledged filler {i+1}",
            "timestamp": timestamp
        })
        
    chat_data = {
        "id": chat_id,
        "title": "Sliding Window Test",
        "created_at": timestamp,
        "updated_at": timestamp,
        "messages": messages
    }
    
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2)
        
    print(f"Created chat {chat_id} with {len(messages)} messages.")

if __name__ == "__main__":
    generate_chat()
