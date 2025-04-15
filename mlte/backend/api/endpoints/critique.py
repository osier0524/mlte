import traceback
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from mlte.backend.dto.critique import CritiqueStats, SetCritiqueRequest, SetCritiqueResponse
from mlte.backend.dto.requirement import GetVersionRequest
from mlte.backend.services.critique_service import CritiqueService

from mlte.backend.services.config import OPENAI_API_KEY

from mlte.backend.db.session import get_db
from mlte.backend.services.llm.llm_service import LLMService
from mlte.backend.services.llm.openai_provider import OpenAIProvider
from mlte.backend.services.requirement_service import RequirementService
from mlte.backend.services.critique_service import CritiqueService
router = APIRouter()

openai_provider = OpenAIProvider(OPENAI_API_KEY)
llm_service = LLMService(openai_provider)

@router.post("", response_model=CritiqueStats)
async def critique_api(artifact_id: int, requirement_id: int, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    critique_service = CritiqueService(db, llm_service, requirement_service)
    try:
        return await critique_service.critique_requirement(artifact_id, requirement_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-critique/version")
def get_filter_requirement_version(request: GetVersionRequest, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)

    version = requirement_service.get_requirements_version(request.artifact_id, request.filter_criteria)
    return {"version": version}

@router.post("/set-critique", response_model=SetCritiqueResponse)
async def critique_requirement_set(
    request: SetCritiqueRequest,
    db: Session = Depends(get_db),
):
    requirement_service = RequirementService(db)
    critique_service = CritiqueService(db, llm_service, requirement_service)
    try:
        stats = await critique_service.critique_requirement_set(
            request.artifact_id, 
            request.filter_criteria
        )
        return SetCritiqueResponse(stats=stats)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)
)