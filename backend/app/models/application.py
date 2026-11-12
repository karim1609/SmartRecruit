
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


ApplicationStatus = Literal[
    "pending",
    "reviewing",
    "accepted",
    "rejected"
]


class ApplicationBase(BaseModel):
    candidate_id: str
    job_offer_id: str
    cover_letter: str | None = None


class ApplicationCreate(BaseModel):
    """Fields the client sends when applying for a job.
    candidate_id is derived server-side from the JWT token.
    """
    job_offer_id: str
    cover_letter: str | None = None


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ApplicationStatus | None = None
    cover_letter: str | None = None


class ApplicationInDB(ApplicationBase):
    status: ApplicationStatus = "pending"

    applied_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ApplicationResponse(ApplicationBase):
    id: str
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime
