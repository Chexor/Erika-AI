"""interface/state.py
The Model layer. Holds the reactive state of the Erika AI application.
"""
from typing import List, Dict, Callable
from dataclasses import dataclass, field

@dataclass
class AppState:
    # Chat State
    current_chat_id: str | None = None
    messages: List[Dict] = field(default_factory=list)
    is_generating: bool = False
    
    # UI State
    sidebar_history: Dict[str, List[Dict]] = field(default_factory=dict)
    
    # Notification Queue (Message, Type)
    # UI consumes this to show toasts
    notifications: List[tuple] = field(default_factory=list)
    
    def clear_messages(self):
        self.messages.clear()
    
    def add_message(self, msg: Dict):
        self.messages.append(msg)
        
    def update_last_message(self, content: str):
        if self.messages:
            self.messages[-1]['content'] = content
            
    def set_generating(self, generating: bool):
        self.is_generating = generating
        
    def push_notification(self, msg: str, type: str = 'info'):
        self.notifications.append((msg, type))
