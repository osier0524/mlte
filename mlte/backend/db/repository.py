from sqlalchemy.orm import Session
from mlte.backend.db.models import Artifact, Requirement

class ArtifactRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Artifact).all()

    @staticmethod
    def get_by_id(db: Session, artifact_id: int):
        return db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()

    @staticmethod
    def create(db: Session, name: str):
        new_artifact = Artifact(name=name)
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)
        return new_artifact
    

class RequirementRepository:
    @staticmethod
    def get_all(db: Session, artifact_id: int):
        return db.query(Requirement).filter(Requirement.artifact_id == artifact_id).all()

    @staticmethod
    def create(db: Session, artifact_id: int, content: str):
        new_requirement = Requirement(artifact_id=artifact_id, content=content)
        db.add(new_requirement)
        db.commit()
        db.refresh(new_requirement)
        return new_requirement
