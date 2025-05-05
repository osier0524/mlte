from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        system_prompt: The prompt to be used for the system.
        user_prompt: The prompt to be used for the user.
        return str: The response from the model.
        """
        pass
