from typing import Optional
from pydantic import BaseModel

class ArtifactBase(BaseModel):
    name: str
    project_description: Optional[str] = None
    ml_task: Optional[str] = None
    usage_context: Optional[str] = None
    target_audience: Optional[str] = None
    dataset_description: Optional[str] = None

class ArtifactCreate(ArtifactBase):
    artifact_id: Optional[int] = None
    pass

class ArtifactResponse(ArtifactBase):
    artifact_id: int
    pass

class ArtifactCreateResponse(BaseModel):
    artifact_id: int

    class Config:
        from_attributes = True
