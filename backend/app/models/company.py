
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str
    industry: str
    website: str | None = None
    location: str
    size: int | None = Field(default=None, ge=1)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    industry: str | None = None
    website: str | None = None
    location: str | None = None
    size: int | None = Field(default=None, ge=1)


class CompanyInDB(CompanyBase):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
