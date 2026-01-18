import asyncio
import json
import os
import sys
import logging
from contextlib import AsyncExitStack
from typing import Dict, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger("ENGINE.McpManager")

class McpManager:
    def __init__(self, config_path: str = "config/mcp_config.json"):
        self.config_path = config_path
        self.config = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self._loop = None
        
    def load_config(self):
        """Loads server configuration from JSON."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"McpManager: Loaded config from {self.config_path}")
            except Exception as e:
                logger.error(f"McpManager: Failed to load config: {e}")
        else:
            logger.warning(f"McpManager: Config not found at {self.config_path}")

    async def start_all(self):
        """Starts all enabled servers defined in config."""
        self.load_config()
        self._loop = asyncio.get_running_loop()
        
        servers = self.config.get('servers', {})
        for name, cfg in servers.items():
            if cfg.get('enabled', False) and cfg.get('auto_start', False):
                await self.start_server(name, cfg)

    async def start_server(self, name: str, cfg: dict):
        """Starts a single MCP server."""
        logger.info(f"McpManager: Starting server '{name}'...")
        
        command = cfg.get('command')
        args = cfg.get('args', [])
        env = cfg.get('env', {}).copy()
        
        # Merge current environment
        full_env = os.environ.copy()
        full_env.update(env)
        
        # Handle python executable alias
        if command == "python":
            command = sys.executable

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=full_env
        )
        
        try:
            read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            self.sessions[name] = session
            logger.info(f"McpManager: Server '{name}' connected.")
            
        except Exception as e:
            logger.error(f"McpManager: Failed to start server '{name}': {e}")

    async def stop_all(self):
        """Stops all servers and cleans up resources."""
        logger.info("McpManager: Stopping all servers...")
        try:
            await self.exit_stack.aclose()
            self.sessions.clear()
            logger.info("McpManager: All servers stopped.")
        except Exception as e:
            logger.error(f"McpManager: Error during shutdown: {e}")

    def get_session(self, name: str) -> Optional[ClientSession]:
        """Returns the active session for a named server."""
        return self.sessions.get(name)

    def get_status(self) -> list:
        """Returns a list of server statuses for the dashboard."""
        status_list = []
        servers = self.config.get('servers', {})
        
        # Iterate over configured servers to show even stopped ones
        for name, cfg in servers.items():
            if not cfg.get('enabled', False):
                continue
                
            is_connected = name in self.sessions
            status_list.append({
                'name': name.capitalize(),
                'status': 'ok' if is_connected else 'error',
                'detail': 'Connected' if is_connected else 'Disconnected'
            })
            
        return status_list
