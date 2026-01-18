import httpx
import logging
import json
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("ENGINE.BrainRouter")

# Default configuration - can be overridden via environment variables or config files
DEFAULT_LOCAL_BRAIN = "http://localhost:11434"
DEFAULT_REMOTE_BRAIN = "http://192.168.0.69:11434"
DEFAULT_LOCAL_MODEL = "qwen3:14b"
DEFAULT_REMOTE_MODEL = "gemma2:9b"


class BrainRouter:
    def __init__(self):
        # Configuration from environment variables or defaults
        self.LOCAL_BRAIN = os.environ.get("ERIKA_LOCAL_BRAIN", DEFAULT_LOCAL_BRAIN)
        self.REMOTE_BRAIN = os.environ.get("ERIKA_REMOTE_BRAIN", DEFAULT_REMOTE_BRAIN)

        self.LOCAL_MODEL = os.environ.get("ERIKA_LOCAL_MODEL", DEFAULT_LOCAL_MODEL)
        self.REMOTE_MODEL = os.environ.get("ERIKA_REMOTE_MODEL", DEFAULT_REMOTE_MODEL)

        self.nodes = {
            'local': self.LOCAL_BRAIN,
            'remote': self.REMOTE_BRAIN
        }

        # Load Shared Config
        self.llm_config: Dict[str, Any] = {
            "consciousness_5070ti": {},
            "subconscious_3060": {}
        }

        # Absolute source of truth for LLM parameters
        possible_paths = [
            os.path.join("config", "llm_config.json")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.llm_config = json.load(f)
                    self.config_path = path
                    logger.info(f"BrainRouter: Loaded LLM Config from {path}")
                    break
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"BrainRouter: Failed to load config from {path}: {e}")

        # State
        self.status = {
            'local': False,
            'remote': False
        }

        logger.info(f"BrainRouter initialized: Local={self.LOCAL_BRAIN}, Remote={self.REMOTE_BRAIN}")

    def get_model_options(self, node_type: str) -> dict:
        """Returns model parameters (temp, ctx, etc) from config."""
        if node_type == 'remote':
             return self.llm_config.get("subconscious_3060", {}).get("options", {})
        else:
             return self.llm_config.get("consciousness_5070ti", {}).get("options", {})
        
    async def check_availability(self, url: str) -> bool:
        """Pings an Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{url}/api/tags")
                return resp.status_code == 200
        except httpx.TimeoutException:
            logger.debug(f"BrainRouter: Timeout checking availability of {url}")
            return False
        except httpx.ConnectError:
            logger.debug(f"BrainRouter: Connection refused for {url}")
            return False
        except httpx.HTTPError as e:
            logger.warning(f"BrainRouter: HTTP error checking {url}: {e}")
            return False

    async def ping_remote(self) -> str:
        """Returns 'Online' or 'Offline' for remote."""
        available = await self.check_availability(self.REMOTE_BRAIN)
        return 'Online' if available else 'Offline'

    async def update_status(self):
        """Updates status of all nodes."""
        self.status['local'] = await self.check_availability(self.LOCAL_BRAIN)
        self.status['remote'] = await self.check_availability(self.REMOTE_BRAIN)
        
        if self.status['remote']:
            logger.info(f"Erika's Subconscious Online: {self.REMOTE_BRAIN}")
        else:
            logger.info("Erika's Subconscious Offline. Running in Local Mode.")

    def get_primary_host(self, task_type: str = 'chat') -> str:
        """Determines the best host for the task."""
        # 1. Force Local for strict latency (Chat)
        if task_type == 'chat':
            return self.LOCAL_BRAIN
            
        # 2. Logic/Reflection -> Prefer Remote
        if task_type == 'reflection':
            if self.status['remote']:
                return self.REMOTE_BRAIN
            else:
                return self.LOCAL_BRAIN
                
        # Default
        return self.LOCAL_BRAIN
        
    def set_model_option(self, node_group: str, key: str, value: Any):
        """Updates a model option in the config."""
        if node_group not in self.llm_config:
            self.llm_config[node_group] = {"options": {}}
        if "options" not in self.llm_config[node_group]:
            self.llm_config[node_group]["options"] = {}
        
        self.llm_config[node_group]["options"][key] = value

    def save_config(self):
        """Saves current llm_config back to disk."""
        path = getattr(self, 'config_path', os.path.join("config", "llm_config.json"))
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.llm_config, f, indent=4)
            logger.info(f"BrainRouter: Saved LLM Config to {path}")
        except Exception as e:
            logger.error(f"BrainRouter: Failed to save config: {e}")

    # Legacy / Controller Support
    async def route_query(self, task_type: str, payload: dict) -> str:
        host = self.get_primary_host(task_type)
        return 'remote' if host == self.REMOTE_BRAIN else 'local'

    def get_active_url(self, node_name: str) -> str:
        return self.nodes.get(node_name, self.LOCAL_BRAIN)

    @property
    def current_route(self) -> str:
        """Returns the current routing destination for chat."""
        host = self.get_primary_host('chat')
        return 'remote' if host == self.REMOTE_BRAIN else 'local'
