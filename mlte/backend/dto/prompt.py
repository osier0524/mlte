from pydantic import BaseModel
from typing import List


class PromptChainRequest(BaseModel):
    prompts: List[str]
    model: str = "gpt-4"

class PromptChainResponse(BaseModel):
    response: str