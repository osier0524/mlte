


from fastapi import APIRouter, HTTPException
from mlte.backend.dto.prompt import PromptChainRequest

import openai


router = APIRouter()

@router.post("/prompt-chain")
def prompt_chain(request: PromptChainRequest):
    try:
        response = ""
        for prompt in request.prompts:
            response += prompt + " "
            completion = openai.Completion.create(
                model = request.model,
                messages = [
                    {"role": "user", "content": response}
                ]
            )
            result = completion.choices[0].message["content"]
            response = result
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    