from pydantic import BaseModel, field_serializer
from typing import List, Optional

class ProjectContext(BaseModel):
    project_description: str
    ml_task: Optional[str] = None
    usage_context: Optional[str] = None
    target_audience: Optional[str] = None
    dataset_description: Optional[str] = None

class RequirementCritiqueRequest(BaseModel):
    requirement: str
    req_category: str
    project_context: ProjectContext
    quality: str  # e.g., "unambiguous"

class Rating(BaseModel):
    rating: str
    explanation: Optional[str]

class Critique(BaseModel):
    rating: str
    critiques: List[str]

class RequirementCritiqueResponse(BaseModel):
    requirement_id: int
    quality: str
    critique: Critique

class CritiqueStats(BaseModel):
    warnings: List[str]
    errors: List[str]

class CritiqueStatsRequest(BaseModel):
    artifact_id: int
    requirement_id: int

# Used in requirement_service.py
class QualityWithCritiquesResponse(BaseModel):
    name: str
    critiques: List[str]

class FeedbackResponse(BaseModel):
    level: str
    qualities: List[QualityWithCritiquesResponse]

class SetCritiqueStats(BaseModel):
    issues: List[str]

class SetCritiqueRequest(BaseModel):
    artifact_id: int
    filter_criteria: str

class SetCritiqueResponse(BaseModel):
    stats: SetCritiqueStats