from pydantic import BaseModel
from datetime import datetime

class ArtifactBase(BaseModel):
    name: str

class ArtifactCreate(ArtifactBase):
    pass

class ArtifactResponse(ArtifactBase):
    artifact_id: int
    created_at: datetime

    class Config:
        from_attributes = True
