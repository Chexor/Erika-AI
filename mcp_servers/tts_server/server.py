import logging
import asyncio
import sys
import os

# Ensure project root is in path so we can import tools
# This script is at mcp_servers/tts_server/server.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from tools.tts_service import TTSService

# Initialize Service
# Note: In a real server, we might want this to be lazy or persistent. 
# FastMCP keeps the process alive, so this is persistent.
service = TTSService()

logger = logging.getLogger("mcp_server.tts")
logging.basicConfig(level=logging.INFO)

# Initialize MCP Server
mcp = FastMCP("Erika TTS")

@mcp.tool()
def speak(text: str, voice: str = "azelma", volume: float = 1.0, autoplay: bool = True) -> str:
    """
    Synthesizes speech from text.
    
    Args:
        text: The text to speak.
        voice: Voice ID (default: 'azelma').
        volume: Volume multiplier (0.0 to 1.0).
        autoplay: If True, plays audio immediately. If False, just prepares it (not fully supported by service yet, so autoplay is enforced).
    """
    # Service handles state
    if voice:
        service.set_voice(voice)
    if volume is not None:
        service.set_volume(volume)
        
    # We don't support non-autoplay in current service, so we just speak.
    # We wrap in a way that returns status
    success = service.speak(text)
    if success:
        return f"Speaking: {text[:50]}..."
    else:
        return "Failed to start speech."

@mcp.tool()
def stop() -> str:
    """Stops current playback."""
    service.stop()
    return "Playback stopped."

@mcp.tool()
def status() -> dict:
    """Returns current TTS status."""
    return {
        "is_speaking": service.is_speaking,
        "voice": service.current_voice,
        "volume": service.volume,
        "stop_event": service.stop_event.is_set()
    }

@mcp.tool()
def set_voice(voice: str) -> str:
    """Sets the voice model."""
    service.set_voice(voice)
    return f"Voice set to {service.current_voice}"

@mcp.tool()
def set_volume(volume: float) -> str:
    """Sets the volume (0.0-1.0)."""
    service.set_volume(volume)
    return f"Volume set to {service.volume}"

@mcp.tool()
def health() -> dict:
    """Returns health and configuration status."""
    return {
        "model_loaded": bool(service.tts_model),
        "offline_mode": service._offline_mode,
        "update_days": service._update_days,
        "active": True
    }

if __name__ == "__main__":
    # Run the server
    logger.info("Starting TTS MCP Server...")
    mcp.run()
