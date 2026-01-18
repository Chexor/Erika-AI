
import httpx
import logging
import asyncio

logger = logging.getLogger("ENGINE.BrainRouter")

class BrainRouter:
    def __init__(self):
        # Configuration
        self.LOCAL_BRAIN = "http://localhost:11434"
        self.REMOTE_BRAIN = "http://192.168.0.69:11434"
        
        self.LOCAL_MODEL = "qwen3:14b"
        self.REMOTE_MODEL = "gemma2:9b"
        
        self.nodes = {
            'local': self.LOCAL_BRAIN,
            'remote': self.REMOTE_BRAIN
        }
        
        # State
        self.status = {
            'local': False, 
            'remote': False
        }
        
    async def check_availability(self, url: str) -> bool:
        """Pings an Ollama instance."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{url}/api/tags")
                return resp.status_code == 200
        except Exception:
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
        
    # Legacy / Controller Support
    async def route_query(self, task_type: str, payload: dict) -> str:
        host = self.get_primary_host(task_type)
        return 'remote' if host == self.REMOTE_BRAIN else 'local'

    def get_active_url(self, node_name: str) -> str:
        return self.nodes.get(node_name, self.LOCAL_BRAIN)
