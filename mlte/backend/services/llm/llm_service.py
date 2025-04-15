from typing import List, Dict
from .base import BaseLLMProvider

class LLMService:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def send_message(self, system_prompt: str, user_prompt: str) -> str:
        return self.provider.chat(system_prompt=system_prompt, user_prompt=user_prompt)

