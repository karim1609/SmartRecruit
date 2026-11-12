
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connection import recruiters_collection
from app.core.dependencies import require_role
from app.models.recruiter import RecruiterUpdate


router = APIRouter(
    prefix="/recruiters",
    tags=["Recruiters"]
)


# -------------------------
# Get recruiter profile
# -------------------------

@router.get("/me")
def get_recruiter_profile(
    current_user: dict = Depends(require_role("recruiter"))
):

    recruiter = recruiters_collection.find_one({
        "user_id": current_user["id"]
    })

    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )

    return {
        "id": str(recruiter["_id"]),
        "user_id": recruiter["user_id"],
        "full_name": recruiter["full_name"],
        "phone": recruiter.get("phone"),
        "job_title": recruiter.get("job_title"),
        "company_id": recruiter.get("company_id"),
        "created_at": recruiter["created_at"],
        "updated_at": recruiter["updated_at"]
    }


# -------------------------
# Update recruiter profile
# -------------------------

@router.patch("/me")
def update_recruiter_profile(
    data: RecruiterUpdate,
    current_user: dict = Depends(require_role("recruiter"))
):

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Do not allow users to assign themselves to arbitrary companies.
    # Company association will be handled by company-management logic.
    if "company_id" in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use the company management endpoints to change company association"
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = recruiters_collection.update_one(
        {"user_id": current_user["id"]},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )

    recruiter = recruiters_collection.find_one({
        "user_id": current_user["id"]
    })

    return {
        "message": "Recruiter profile updated successfully",
        "recruiter": {
            "id": str(recruiter["_id"]),
            "user_id": recruiter["user_id"],
            "full_name": recruiter["full_name"],
            "phone": recruiter.get("phone"),
            "job_title": recruiter.get("job_title"),
            "company_id": recruiter.get("company_id"),
            "updated_at": recruiter["updated_at"]
        }
    }
