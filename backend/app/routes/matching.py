
from bson import ObjectId
from bson.errors import InvalidId

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.connection import (
    job_offers_collection,
    company_members_collection
)

from app.core.dependencies import require_role
from app.services.matching_service import find_top_candidates_for_job


router = APIRouter(
    prefix="/matching",
    tags=["AI Matching"]
)


# ==========================================
# CHECK RECRUITER ACCESS TO JOB
# ==========================================

def verify_job_access(job: dict, current_user: dict):

    user_id = current_user["id"]

    # Admin can access every job
    if current_user["role"] == "admin":
        return

    # Recruiter who created the job
    if job.get("created_by") == user_id:
        return

    # Check company membership
    company_id = job.get("company_id")

    membership = company_members_collection.find_one({
        "company_id": company_id,
        "recruiter_id": user_id
    })

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this job's candidates"
        )


# ==========================================
# MATCH CANDIDATES WITH A JOB OFFER
# ==========================================

@router.get("/job/{job_id}")
def match_candidates(
    job_id: str,
    top_k: int = Query(default=5, ge=1, le=20),
    current_user: dict = Depends(require_role("recruiter", "admin"))
):

    # 1. Validate job ID
    try:
        job_object_id = ObjectId(job_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job offer ID"
        )

    # 2. Retrieve job offer
    job = job_offers_collection.find_one({
        "_id": job_object_id
    })

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job offer not found"
        )

    # 3. Verify permissions
    verify_job_access(job, current_user)

    # 4. Validate job description
    if not job.get("description"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is missing"
        )

    # 5. Call AI matching service
    try:
        matches = find_top_candidates_for_job(
            job=job,
            top_k=top_k
        )

    except Exception:
        # Log the actual exception internally in production
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI matching service is currently unavailable"
        )

    # 6. Return matching results
    return {
        "job_id": str(job["_id"]),
        "job_title": job.get("title"),
        "total_matches": len(matches),
        "matches": matches
    }


# ==========================================
# CHECK MATCHING SERVICE STATUS
# ==========================================

@router.get("/health")
def matching_health(
    current_user: dict = Depends(require_role("recruiter", "admin"))
):
    return {
        "service": "AI Matching",
        "status": "available"
    }
