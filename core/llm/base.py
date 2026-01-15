from abc import ABC, abstractmethod
from typing import Generator

class LLMProvider(ABC):
    """
    Abstract Base Class for all LLM backends.
    """
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        pass
