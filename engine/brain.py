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

    async def generate_response(self, model: str, messages: list, host: str = None, options: dict = None):
        """Generates a streamed response."""
        
        # Determine client to use
        target_client = self.client
        if host and host != self.host:
             # Create temp client for this request
             target_client = AsyncClient(host=host)

        try:
            async for chunk in await target_client.chat(model=model, messages=messages, stream=True, options=options):
                # Ensure we yield a dict, not a Pydantic object
                if hasattr(chunk, 'model_dump'):
                    yield chunk.model_dump()
                elif hasattr(chunk, 'dict'):
                    yield chunk.dict()
                else:
                    yield dict(chunk)
        except Exception as e:
            logger.error(f"Generation error (Host: {host or self.host}): {e}")
            yield {"error": str(e)}
