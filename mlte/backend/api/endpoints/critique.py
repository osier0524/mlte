from fastapi import APIRouter, HTTPException
from app.models.critique import RequirementCritiqueRequest, RequirementCritiqueResponse
from app.services.critique_service import critique_requirement

router = APIRouter()

@router.post("/critique", response_model=RequirementCritiqueResponse)
async def critique_api(req: RequirementCritiqueRequest):
    try:
        return await critique_requirement(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
