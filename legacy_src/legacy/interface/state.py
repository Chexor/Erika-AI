from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class AppState:
    """
    Mutable state container for the application UI.
    No logic allowed here.
    """
    # Chat Data
    messages: List[Dict[str, Any]] = field(default_factory=list)
    sidebar_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # UI Flags
    is_sidebar_open: bool = True
    web_search_active: bool = False
    is_loading: bool = False
    
    # Configuration
    selected_model: str = "llama3"
    
    # Notifications/Status
    status_message: str = "Ready"
