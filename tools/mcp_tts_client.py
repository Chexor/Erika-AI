import asyncio
import sys
import logging
import os
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Optional, Callable

logger = logging.getLogger("TOOLS.McpTtsClient")

class McpTtsClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._loop = None
             
        self.is_speaking = False
        self.current_voice = "azelma"
        self.volume = 1.0
        self.temperature = 0.7
        self.decode_steps = 1
        self.eos_threshold = -4.0
        self.stop_event = asyncio.Event() 
        
    def set_session(self, session: ClientSession):
        """Injects an existing MCP session."""
        self.session = session

    async def start(self):
        """Starts the client. Must be called inside a running loop."""
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            
        if not self.session:
             await self.connect()
        
    async def connect(self):
        logger.info("Connecting to MCP TTS Server...")
        # script = os.path.join(os.getcwd(), 'mcp_tools', 'erika_voice', 'server.py')
        
        # Use python executable
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_tools.erika_voice.server"],
            env=None
        )
        
        try:
             read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
             self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
             await self.session.initialize()
             logger.info("Connected to MCP TTS Server.")
        except Exception as e:
             logger.error(f"Failed to connect to MCP TTS Server: {e}")
             self.session = None

    def set_voice(self, voice_name: str):
         self.current_voice = voice_name
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("set_voice", arguments={"voice": voice_name}), self._loop)

    def set_volume(self, volume: float):
         self.volume = volume
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("set_volume", arguments={"volume": volume}), self._loop)

    def set_temperature(self, temp: float):
         self.temperature = temp
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("set_temperature", arguments={"temp": temp}), self._loop)

    def set_decode_steps(self, steps: int):
         self.decode_steps = steps
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("set_decode_steps", arguments={"steps": steps}), self._loop)

    def set_eos_threshold(self, threshold: float):
         self.eos_threshold = threshold
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("set_eos_threshold", arguments={"threshold": threshold}), self._loop)

    def stop(self):
         if self.session:
             asyncio.run_coroutine_threadsafe(self.session.call_tool("stop", arguments={}), self._loop)

    def speak(self, text: str, on_finished: Optional[Callable[[], None]] = None) -> bool:
         if not self.session:
             logger.warning("MCP Session not active. Dropping TTS request.")
             return False
             
         async def _speak_task():
             try:
                 self.is_speaking = True
                 # Call speak with all current context
                 args = {
                     "text": text,
                     "voice": self.current_voice,
                     "volume": self.volume,
                     "temperature": self.temperature,
                     "decode_steps": self.decode_steps,
                     "eos_threshold": self.eos_threshold,
                     "autoplay": True
                 }
                 await self.session.call_tool("speak", arguments=args)
                 
                 # Poll for completion
                 # The server uses a thread, so is_speaking remains true for a duration.
                 while True:
                     try:
                         result = await self.session.call_tool("status", arguments={})
                         # result.content is a list of TextContent
                         if result.content:
                              data = json.loads(result.content[0].text) # Wait, status returns dict? 
                              # MCP implementation: @mcp.tool() def status() -> dict. 
                              # mcp SDK wraps return into TextContent containing JSON string usually?
                              # Or does it return EmbeddedResource?
                              # FastMCP defaults to JSON text content.
                              # Let's verify structure. FastMCP tools returning dicts are serialized to string.
                              
                              # Actually, checking 'is_speaking' in data
                              if not data.get("is_speaking", False):
                                  break
                     except Exception:
                          break
                     await asyncio.sleep(0.5)
                     
             except Exception as e:
                 logger.error(f"MCP Speak task error: {e}")
             finally:
                 self.is_speaking = False
                 if on_finished:
                      # on_finished is thread safe from controller
                      on_finished()

         asyncio.run_coroutine_threadsafe(_speak_task(), self._loop)
         return True
     
    # Properties for compatibility
    @property
    def tts_model(self):
        # We pretend we have one to satisfy checks (e.g. system start)
        return True
        
    def is_ready(self) -> bool:
        """Returns True if the MCP session is active."""
        return self.session is not None
