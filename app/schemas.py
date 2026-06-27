# ============================================================
# schemas.py
# Pydantic schemas control what data comes IN (request body)
# and what goes OUT (JSON response).  They are separate from
# the SQLAlchemy model so validation and serialisation stay clean.
# ============================================================

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
VALID_STATUSES = {"Pending", "Completed"}


# ---------------------------------------------------------------------------
# Request schemas (what the client sends)
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    """Body for POST /tasks — creates a brand-new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field("", max_length=1000, description="Optional details")
    status: Optional[str] = Field("Pending", description="Pending or Completed")

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class TaskUpdate(BaseModel):
    """Body for PUT /tasks/{id} — replaces all mutable fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=1000)
    status: str = Field(..., description="Pending or Completed")

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class TaskPatch(BaseModel):
    """Body for PATCH /tasks/{id} — only updates the status field."""
    status: str = Field(..., description="Pending or Completed")

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


# ---------------------------------------------------------------------------
# Response schemas (what the server returns)
# ---------------------------------------------------------------------------

class TaskOut(BaseModel):
    """Single task as returned in API responses."""
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}   # enables ORM mode


class APIResponse(BaseModel):
    """
    Uniform JSON wrapper for every endpoint.

    {
        "success": true,
        "message": "...",
        "data": <task | list of tasks | null>
    }
    """
    success: bool
    message: str
    data: Optional[Any] = None
