
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from app.database.connection import candidates_collection
from app.core.dependencies import require_role


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


# -------------------------
# Response / Update schemas
# -------------------------

class CandidateUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    phone: str | None = None
    location: str | None = None

    skills: list[str] | None = None

    education: list[dict] | None = None

    experience: list[dict] | None = None


# -------------------------
# Get candidate profile
# -------------------------

@router.get("/me")
def get_candidate_profile(
    current_user: dict = Depends(require_role("candidate"))
):

    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    return {
        "id": str(candidate["_id"]),
        "user_id": candidate["user_id"],
        "full_name": candidate["full_name"],
        "phone": candidate.get("phone"),
        "location": candidate.get("location"),
        "skills": candidate.get("skills", []),
        "education": candidate.get("education", []),
        "experience": candidate.get("experience", []),
        "created_at": candidate["created_at"],
        "updated_at": candidate["updated_at"]
    }


# -------------------------
# Update candidate profile
# -------------------------

@router.patch("/me")
def update_candidate_profile(
    data: CandidateUpdate,
    current_user: dict = Depends(require_role("candidate"))
):

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = candidates_collection.update_one(
        {"user_id": current_user["id"]},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    updated_candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    return {
        "message": "Candidate profile updated successfully",
        "candidate": {
            "id": str(updated_candidate["_id"]),
            "user_id": updated_candidate["user_id"],
            "full_name": updated_candidate["full_name"],
            "phone": updated_candidate.get("phone"),
            "location": updated_candidate.get("location"),
            "skills": updated_candidate.get("skills", []),
            "education": updated_candidate.get("education", []),
            "experience": updated_candidate.get("experience", []),
            "updated_at": updated_candidate["updated_at"]
        }
    }
