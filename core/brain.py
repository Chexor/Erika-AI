try:
    import ollama
except ImportError:
    ollama = None

from typing import List, Dict, Generator, Any
from core.settings import SettingsManager
from core.logger import setup_logger

logger = setup_logger("CORE.Brain")

class Brain:
    """
    Interface for LLM interactions via Ollama.
    """

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        if ollama is None:
            logger.critical("Ollama library not installed. Brain module invalid.")

    def check_connection(self) -> bool:
        """Verifies connection to the Ollama server."""
        if ollama is None:
            return False
        try:
            ollama.list()
            return True
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Returns a list of available model names."""
        if ollama is None:
            return []
        try:
            response = ollama.list()
            # Handle different versions of ollama lib structure if needed,
            # but assuming standard: {'models': [{'name': ...}]}
            return [m['name'] for m in response.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def think_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Streams response from the LLM.
        
        Args:
            messages: List of dicts with 'role' and 'content'.
            
        Yields:
            str: chunks of generated text.
        """
        if ollama is None:
            raise ImportError("Ollama library missing")

        model = self.settings.get("user", "model", "llama3")
        system_prompt = self.settings.get("user", "system_prompt", "")
        
        # Inject system prompt if present and not already there
        # (Naive check: if first msg is not system)
        final_messages = messages.copy()
        if system_prompt:
            if not final_messages or final_messages[0].get('role') != 'system':
                final_messages.insert(0, {'role': 'system', 'content': system_prompt})

        try:
            stream = ollama.chat(model=model, messages=final_messages, stream=True)
            for chunk in stream:
                content = chunk.get('message', {}).get('content', '')
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Inference error: {e}")
            yield f"[Error: {str(e)}]"
