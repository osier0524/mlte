import traceback
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from mlte.backend.db.session import get_db
from mlte.backend.db.repository import RequirementRepository
from mlte.backend.dto.requirement import *
from mlte.backend.dto.critique import CritiqueStats, CritiqueStatsRequest
from mlte.backend.services.requirement_service import RequirementService

router = APIRouter()

@router.get("/{artifact_id}/requirements", response_model=list[RequirementBase])
def list_requirements(artifact_id: int, db: Session = Depends(get_db)):
    return RequirementRepository.get_all(db, artifact_id)

# get a requirement
@router.get("/{requirement_id}", response_model=RequirementContentResponse)
def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    requirement = RequirementRepository.get_by_id(db, requirement_id)
    response = RequirementContentResponse(
        requirement_id = requirement.requirement_id,
        content = requirement.content,
    )
    return response

# add a new requirement
@router.post("/", response_model=RequirementCreateResponse)
def create_requirement(req: RequirementCreate, db: Session = Depends(get_db)):
    service = RequirementService(db)
    return service.create_requirement(req.artifact_id, req.card_index, req.content)

# update a requirement
@router.post("/{requirement_id}", response_model=RequirementCreateResponse)
def update_requirement(
    requirement_id: int, 
    req: RequirementCreate, 
    db: Session = Depends(get_db)
):
    service = RequirementService(db)
    return service.update_requirement(req.artifact_id, req.card_index, req.content)

# add requirement category
@router.post("/{requirement_id}/assign-categories")
def assign_categories(
    requirement_id: int,
    payload: RequirementCategoryAssign, 
    db: Session = Depends(get_db)
):
    service = RequirementService(db)
    try:
        service.add_categories_to_requirement(
            payload.artifact_id,
            payload.card_index,
            payload.category_names
        )
    except Exception as e:
        # print error stack trace
        traceback.print_exc()

# add feedback to a requirement
@router.post("/feedback")
def add_feedback(payload: RequirementFeedbackCreate, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    return requirement_service.add_feedback_with_quality_and_critiques(
        requirement_id=payload.requirement_id,
        level=payload.level,
        quality_name=payload.quality_name,
        critique_contents=payload.critiques
    )

# get a requirement's categories
@router.get("/{requirement_id}/categories", response_model=list[CategoryWrapper])
def get_requirement_categories(requirement_id: int, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    return requirement_service.get_categories_for_requirement(requirement_id)

# get all requirements details for a given artifact
@router.get("/artifact/{artifact_id}/details", response_model=RequirementListResponse)
def get_all_requirements_details(artifact_id: int, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    requirements = requirement_service.get_requirements_by_artifact_id(artifact_id)
    return {"requirements": requirements}

# get a requirement's details
@router.get("/artifact/{artifact_id}/req/{requirement_id}", response_model=RequirementResponse)
def get_requirement_details(artifact_id: int, requirement_id: int, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    requirement = requirement_service.get_requirement_by_id(artifact_id, requirement_id)
    return requirement

# get a requirement's critique statistics
@router.get("/{requirement_id}/critique-stats", response_model=CritiqueStats)
def get_requirement_critique_stats(requirement_id: int, db: Session = Depends(get_db)):
    requirement_service = RequirementService(db)
    stats = requirement_service.get_critique_stats(requirement_id)
    return stats
