import os
import json
import shutil
from typing import Any, Dict, Optional
from core.logger import setup_logger

logger = setup_logger("CORE.Settings")

class SettingsManager:
    """
    Manages application settings with strict separation of file types and atomic writes.
    """
    
    DEFAULTS = {
        "theme": "dark",
        "model": "llama3",
        "username": "User"
    }

    def __init__(self, system_path: str = "config/system.json", user_path: str = "config/user.json"):
        self.paths = {
            "system": system_path,
            "user": user_path
        }
        
        # Ensure config directory exists
        for path in self.paths.values():
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
        self._load_defaults()

    def _load_defaults(self):
        """Helper to ensure files exist or have defaults if missing."""
        # For this phase, we just explicitly handle missing files in _read_file
        pass

    def _validate_type(self, file_type: str):
        if file_type not in ["system", "user"]:
            raise ValueError(f"Invalid file_type '{file_type}'. Must be 'system' or 'user'.")

    def _read_file(self, file_type: str) -> Dict[str, Any]:
        path = self.paths[file_type]
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read {file_type} config at {path}: {e}")
            return {}

    def _atomic_write(self, path: str, data: Dict[str, Any]):
        """Writes data to a temp file then renames it to target path."""
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, 'w') as f:
                json.dump(data, f, indent=4)
            
            # Atomic move
            shutil.move(tmp_path, path)
            logger.info(f"Successfully saved config to {path}")
        except Exception as e:
            logger.error(f"Failed to write config to {path}: {e}")
            # Cleanup temp if it exists
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    def get(self, file_type: str, key: str, default: Any = None) -> Any:
        self._validate_type(file_type)
        data = self._read_file(file_type)
        return data.get(key, default)

    def set(self, file_type: str, key: str, value: Any) -> None:
        self._validate_type(file_type)
        data = self._read_file(file_type)
        data[key] = value
        self._atomic_write(self.paths[file_type], data)
