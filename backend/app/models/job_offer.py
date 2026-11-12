
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


JobStatus = Literal["open", "closed", "draft"]


class JobOfferBase(BaseModel):
    title: str = Field(min_length=2, max_length=150)

    company_id: str

    description: str

    required_skills: list[str] = Field(default_factory=list)

    min_experience: int = Field(default=0, ge=0)

    location: str

    status: JobStatus = "open"


class JobOfferCreate(JobOfferBase):
    pass


class JobOfferUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=150)
    company_id: str | None = None
    description: str | None = None
    required_skills: list[str] | None = None
    min_experience: int | None = Field(default=None, ge=0)
    location: str | None = None
    status: JobStatus | None = None


class JobOfferInDB(JobOfferBase):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class JobOfferResponse(JobOfferBase):
    id: str
    created_at: datetime
    updated_at: datetime
