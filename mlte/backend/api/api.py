"""
mlte/backend/api/api.py

Top-level API functionality.
"""

from fastapi import APIRouter

from fastapi.routing import APIRoute
from mlte.backend.api.endpoints import artifact, health, metadata, token, user, prompt, critique, requirement
from mlte.backend.api.critique_endpoints import critique_artifact

# The common URL prefix for all artifact routes
_ARTIFACT_PREFIX = "/model/{model_id}/version/{version_id}"

# The base API router across all endpoints
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(metadata.router, tags=["metadata"])
api_router.include_router(token.router, tags=["token"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(
    artifact.router,
    prefix=f"{_ARTIFACT_PREFIX}/artifact",
    tags=["artifact"],
)
api_router.include_router(prompt.router, prefix="/prompt", tags=["prompt"])
api_router.include_router(critique.router, prefix="/critiques", tags=["critiques"])
api_router.include_router(critique_artifact.router, prefix="/artifacts", tags=["critique_artifacts"])
api_router.include_router(requirement.router, prefix="/requirements", tags=["requirements"])