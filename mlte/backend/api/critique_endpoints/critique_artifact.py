from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from mlte.backend.db.session import get_db
from mlte.backend.db.repository import ArtifactRepository
from mlte.backend.dto.artifact import ArtifactCreate, ArtifactResponse, ArtifactCreateResponse
from mlte.backend.services.set_evaluation_service import SetEvaluationService

router = APIRouter()

@router.get("/", response_model=list[ArtifactResponse])
def list_artifacts(db: Session = Depends(get_db)):
    return ArtifactRepository.get_all(db)

@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(artifact_id: int, db: Session = Depends(get_db)):
    artifact = ArtifactRepository.get_by_id(db, artifact_id)
    return artifact

@router.post("/", response_model=ArtifactCreateResponse)
def create_artifact(artifact: ArtifactCreate, db: Session = Depends(get_db)):
    if artifact.artifact_id is None:
        new_artifact = ArtifactRepository.create(db, artifact)
    else:
        new_artifact = ArtifactRepository.update(db, artifact.artifact_id, artifact)
    return ArtifactCreateResponse(artifact_id=new_artifact.artifact_id)

@router.post("/{artifact_id}", response_model=ArtifactCreateResponse)
def update_artifact(artifact: ArtifactCreate, db: Session = Depends(get_db)):
    updated_artifact = ArtifactRepository.update(db, artifact.artifact_id, artifact)
    return ArtifactCreateResponse(artifact_id=updated_artifact.artifact_id)

@router.get("/{artifact_id}/set-critique")
async def get_set_critique(
    artifact_id: int,
    filter_criteria: str,
    db: Session = Depends(get_db),
):
    try:
        evaluation_service = SetEvaluationService(db)
        result = evaluation_service.get_evaluation(artifact_id, filter_criteria)

        if not result:
            return {"message": "No evaluation found for the given artifact and filter criteria."}
        return result
    except Exception as e:
        return {"error": str(e)}