from openai import OpenAI, APIConnectionError
from .base import LLMProvider

class LocalLLMEngine(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434/v1", model_name: str = "llama3"):
        # Using standard OpenAI client for local servers (Ollama/vLLM)
        self.client = OpenAI(
            base_url=base_url,
            api_key="erika-local"
        )
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = self._build_messages(prompt, system_prompt)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except APIConnectionError:
            return "⚠️ Connection Error: Is your local AI engine (Ollama/vLLM) running?"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def stream(self, prompt: str, system_prompt: str = None):
        messages = self._build_messages(prompt, system_prompt)
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except APIConnectionError:
            yield "⚠️ Connection Error: Is your local AI engine running?"
        except Exception as e:
            yield f"⚠️ Error: {str(e)}"

    def _build_messages(self, prompt: str, system_prompt: str):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def check_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
