from ollama import AsyncClient
from engine.logger import setup_engine_logger

# Setup Logger
logger = setup_engine_logger("ENGINE.Brain")

class Brain:
    def __init__(self, host='http://localhost:11434'):
        self.host = host
        self.client = AsyncClient(host=self.host)
        
    async def check_connection(self) -> bool:
        """Verifies connection to Ollama."""
        try:
            await self.client.list()
            logger.info(f"Ollama connection verified at {self.host}")
            return True
        except Exception as e:
            logger.warning(f"Ollama unavailable at {self.host}: {e}")
            return False

    async def generate_response(self, model: str, messages: list):
        """Generates a streamed response."""
        try:
            async for chunk in await self.client.chat(model=model, messages=messages, stream=True):
                yield chunk
        except Exception as e:
            logger.error(f"Generation error: {e}")
            yield {"error": str(e)}
