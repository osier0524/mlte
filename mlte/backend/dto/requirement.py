from typing import List
from pydantic import BaseModel
from mlte.backend.dto.critique import FeedbackResponse

class RequirementBase(BaseModel):
    artifact_id: int
    content: str

class RequirementCreate(RequirementBase):
    pass

class RequirementCreateResponse(BaseModel):
    requirement_id: int

class RequirementCategoryAssign(BaseModel):
    requirement_id: int
    category_names: List[str]

class CategoryResponse(BaseModel):
    category_id: int
    name: str

    class Config:
        from_attributes = True

class CategoryWrapper(BaseModel):
    category: CategoryResponse

    class Config:
        from_attributes = True

class RequirementFeedbackCreate(BaseModel):
    requirement_id: int
    level: str # "warning" or "error"
    quality_name: str
    critiques: List[str]

class RequirementResponse(BaseModel):
    requirement_id: int
    content: str
    categories: List[str]
    feedbacks: List[FeedbackResponse]

class RequirementContentResponse(BaseModel):
    requirement_id: int
    content: str

class RequirementListResponse(BaseModel):
    requirements: List[RequirementResponse]

class GetVersionRequest(BaseModel):
    artifact_id: int
    filter_criteria: str