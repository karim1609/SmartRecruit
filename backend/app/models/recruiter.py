
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict


class RecruiterCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = None
    job_title: str | None = None
    company_id: str | None = None


class RecruiterUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    phone: str | None = None
    job_title: str | None = None
    company_id: str | None = None


class RecruiterInDB(RecruiterCreate):
    user_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class RecruiterResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str | None = None
    job_title: str | None = None
    company_id: str | None = None
    created_at: datetime
    updated_at: datetime
