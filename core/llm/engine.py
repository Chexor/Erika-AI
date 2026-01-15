from openai import AsyncOpenAI, APIConnectionError
from .base import LLMProvider

class LocalLLMEngine(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1", model_name: str = "llama3"):
        # Using Async OpenAI client for non-blocking UI
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="erika-local"
        )
        self.model_name = model_name

    async def generate(self, prompt, system_prompt: str = None) -> str:
        messages = self._build_messages(prompt, system_prompt)
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except APIConnectionError:
            return "⚠️ Connection Error: Is your local AI engine (Ollama/vLLM) running?"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def stream(self, prompt, system_prompt: str = None):
        messages = self._build_messages(prompt, system_prompt)
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except APIConnectionError:
            yield "⚠️ Connection Error: Is your local AI engine running?"
        except Exception as e:
            yield f"⚠️ Error: {str(e)}"

    def _build_messages(self, prompt_or_messages, system_prompt: str):
        # Case 1: Input is already a list of messages
        if isinstance(prompt_or_messages, list):
            # If system prompt is provided, prepend it if not present
            messages = prompt_or_messages.copy()
            if system_prompt:
                # Check if first message is system; if not, insert
                if not messages or messages[0].get('role') != 'system':
                    messages.insert(0, {"role": "system", "content": system_prompt})
            return messages
            
        # Case 2: Input is a string (Legacy)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt_or_messages})
        return messages

    # Note: check_connection usually requires a sync call or we can make it async
    # For now, we will try a simple async list, but Brain expects sync status_check?
    # Actually Brain.status_check is called via asyncio.to_thread in UI, so it expects sync.
    # We can use a separate sync client for status checks or run async loop.
    # To keep it simple, let's keep a sync client just for status check or use a requests call.
    # Or just instantiate a temporary sync client.
    def check_connection(self) -> bool:
        from openai import OpenAI
        try:
            sync_client = OpenAI(base_url=self.client.base_url, api_key="erika-local")
            sync_client.models.list()
            return True
        except Exception:
            return False
