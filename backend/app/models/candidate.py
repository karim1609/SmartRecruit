
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


# Education information
class Education(BaseModel):
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None


# Professional experience
class Experience(BaseModel):
    position: str
    company: str
    description: Optional[str] = None
    years: float = Field(default=0, ge=0)


# Candidate creation schema
class CandidateCreate(BaseModel):
    user_id: str

    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None

    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)


# Candidate update schema
class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

    skills: Optional[list[str]] = None
    education: Optional[list[Education]] = None
    experience: Optional[list[Experience]] = None


# Candidate representation stored in MongoDB
class CandidateInDB(CandidateCreate):
    cv_filename: Optional[str] = None
    cv_path: Optional[str] = None
    cv_text: Optional[str] = None

    embedding_id: Optional[str] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# Candidate information returned to frontend
class CandidateResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None

    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)

    cv_filename: Optional[str] = None
    created_at: datetime
