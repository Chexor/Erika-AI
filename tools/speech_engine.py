import logging
import threading
from typing import Optional, Callable
from mcp_tools.erika_voice.service import TTSService, TEMP_FILE_MAX_AGE

logger = logging.getLogger("TOOLS.SpeechEngine")

class SpeechEngine:
    """
    Wrapper around TTSService to maintain backward compatibility.
    """
    def __init__(self):
        self._service = TTSService()

    async def start(self):
        """No-op for local engine, maintained for interface compatibility."""
        pass
    
    @property
    def stop_event(self):
        return self._service.stop_event
        
    @property
    def is_speaking(self):
        return self._service.is_speaking
        
    @is_speaking.setter
    def is_speaking(self, value):
        self._service.is_speaking = value

    @property
    def current_voice(self):
        return self._service.current_voice

    @property
    def volume(self):
        return self._service.volume

    @property
    def tts_model(self):
        return self._service.tts_model

    def set_voice(self, voice_name: str):
        self._service.set_voice(voice_name)

    def set_volume(self, volume: float):
        self._service.set_volume(volume)

    def stop(self):
        self._service.stop()

    def speak(self, text: str, on_finished: Optional[Callable[[], None]] = None) -> bool:
        return self._service.speak(text, on_finished)

