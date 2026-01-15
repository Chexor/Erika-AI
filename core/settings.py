
import json
import os

CONFIG_DIR = "erika_home/config"
USER_CONF_PATH = os.path.join(CONFIG_DIR, "user.json")
SYS_CONF_PATH = os.path.join(CONFIG_DIR, "system.json")

class SettingsManager:
    def __init__(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
        self._ensure_defaults()
        self.user_config = self._load_file(USER_CONF_PATH)
        self.sys_config = self._load_file(SYS_CONF_PATH)

        # Migration: Ensure model_paths exists
        if "model_paths" not in self.sys_config:
             default_path = os.path.join(os.path.expanduser("~"), ".ollama", "models")
             self.sys_config["model_paths"] = [default_path] if os.path.exists(default_path) else []
             self._save_file(SYS_CONF_PATH, self.sys_config)

    def _ensure_defaults(self):
        if not os.path.exists(USER_CONF_PATH):
            default_user = {
                "username": "User", 
                "theme": "dark",
                "persona": "You are Erika, a helpful and intelligent AI assistant."
            }
            self._save_file(USER_CONF_PATH, default_user)
            
        if not os.path.exists(SYS_CONF_PATH):
            # Detect default Ollama path
            default_path = os.path.join(os.path.expanduser("~"), ".ollama", "models")
            model_paths = []
            if os.path.exists(default_path):
                 model_paths.append(default_path)

            default_sys = {
                "ollama_url": "http://localhost:11434",
                "model": "llama3",
                "context_window": 8192,
                "model_paths": model_paths
            }
            self._save_file(SYS_CONF_PATH, default_sys)

    def _load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_file(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # User Settings
    def get_user_setting(self, key, default=None):
        return self.user_config.get(key, default)

    def set_user_setting(self, key, value):
        self.user_config[key] = value
        self._save_file(USER_CONF_PATH, self.user_config)

    # System Settings
    def get_system_setting(self, key, default=None):
        return self.sys_config.get(key, default)

    def set_system_setting(self, key, value):
        self.sys_config[key] = value
        self._save_file(SYS_CONF_PATH, self.sys_config)

    def save_user_settings(self, new_config):
        self.user_config.update(new_config)
        self._save_file(USER_CONF_PATH, self.user_config)

    def save_system_settings(self, new_config):
        self.sys_config.update(new_config)
        self._save_file(SYS_CONF_PATH, self.sys_config)
