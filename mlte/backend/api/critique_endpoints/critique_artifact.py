from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from mlte.backend.db.session import get_db
from mlte.backend.db.repository import ArtifactRepository
from mlte.schema.artifact import ArtifactCreate, ArtifactResponse

router = APIRouter()

@router.get("/", response_model=list[ArtifactResponse])
def list_artifacts(db: Session = Depends(get_db)):
    return ArtifactRepository.get_all(db)

@router.post("/", response_model=ArtifactResponse)
def create_artifact(artifact: ArtifactCreate, db: Session = Depends(get_db)):
    return ArtifactRepository.create(db, artifact.name)
