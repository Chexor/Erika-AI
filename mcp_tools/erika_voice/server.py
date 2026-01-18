import logging
import asyncio
import sys
import os
from mcp.server.fastmcp import FastMCP
from .service import TTSService

# Initialize Service
# Note: In a real server, we might want this to be lazy or persistent. 
# FastMCP keeps the process alive, so this is persistent.
service = TTSService()

logger = logging.getLogger("mcp_server.tts")
logging.basicConfig(level=logging.INFO)

# Initialize MCP Server
mcp = FastMCP("Erika TTS")

@mcp.tool()
def speak(text: str, voice: str = "azelma", volume: float = 1.0, 
          temperature: float = 0.7, decode_steps: int = 1, 
          eos_threshold: float = -4.0, autoplay: bool = True) -> str:
    """
    Synthesizes speech from text.
    
    Args:
        text: The text to speak.
        voice: Voice ID.
        volume: Volume multiplier.
        temperature: Voice personality.
        decode_steps: Speech clarity.
        eos_threshold: Ending sensitivity.
        autoplay: If True, plays audio immediately.
    """
    # Service handles state
    if voice:
        service.set_voice(voice)
    if volume is not None:
        service.set_volume(volume)
    if temperature is not None:
        service.set_temperature(temperature)
    if decode_steps is not None:
        service.set_decode_steps(decode_steps)
    if eos_threshold is not None:
        service.set_eos_threshold(eos_threshold)
        
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
def set_temperature(temp: float) -> str:
    """Sets the voice personality (0.0-2.0)."""
    service.set_temperature(temp)
    return f"Temperature set to {service.temperature}"

@mcp.tool()
def set_decode_steps(steps: int) -> str:
    """Sets the clarity/decode steps (1-10)."""
    service.set_decode_steps(steps)
    return f"Decode steps set to {service.lsd_decode_steps}"

@mcp.tool()
def set_eos_threshold(threshold: float) -> str:
    """Sets the ending sensitivity (-10.0-0.0)."""
    service.set_eos_threshold(threshold)
    return f"EOS Threshold set to {service.eos_threshold}"

@mcp.tool()
def health() -> dict:
    """Returns health and configuration status."""
    return {
        "model_loaded": bool(service.tts_model),
        "offline_mode": service._offline_mode,
        "update_days": service._update_days,
        "temperature": service.temperature,
        "decode_steps": service.lsd_decode_steps,
        "eos_threshold": service.eos_threshold,
        "active": True
    }

if __name__ == "__main__":
    # Run the server
    logger.info("Starting TTS MCP Server...")
    mcp.run()
