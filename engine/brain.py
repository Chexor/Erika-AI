from ollama import AsyncClient
import logging

# Setup Logger
logger = logging.getLogger("engine.brain")

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

    async def cleanup(self):
        """Closes the main Ollama client."""
        try:
            await self.client.aclose()
            logger.info("Brain: Main Ollama client closed.")
        except Exception as e:
            logger.warning(f"Brain: Error closing client: {e}")

    async def generate_response(self, model: str, messages: list, host: str = None, options: dict = None):
        """Generates a streamed response."""
        
        # Determine client to use
        should_close = False
        if host and host != self.host:
             # Create temp client for this request
             target_client = AsyncClient(host=host)
             should_close = True
        else:
             target_client = self.client

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
        finally:
            if should_close:
                await target_client.aclose()
