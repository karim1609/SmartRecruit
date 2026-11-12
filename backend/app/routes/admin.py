
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.connection import (
    users_collection,
    candidates_collection,
    recruiters_collection,
    companies_collection,
    job_offers_collection,
    applications_collection
)

from app.core.dependencies import require_role


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ==========================================
# PLATFORM STATISTICS
# ==========================================

@router.get("/stats")
def get_platform_stats(
    current_user: dict = Depends(require_role("admin"))
):
    return {
        "total_users": users_collection.count_documents({}),

        "active_users": users_collection.count_documents({
            "is_active": True
        }),

        "inactive_users": users_collection.count_documents({
            "is_active": False
        }),

        "total_candidates": candidates_collection.count_documents({}),

        "total_recruiters": recruiters_collection.count_documents({}),

        "total_companies": companies_collection.count_documents({}),

        "total_job_offers": job_offers_collection.count_documents({}),

        "open_job_offers": job_offers_collection.count_documents({
            "status": "open"
        }),

        "closed_job_offers": job_offers_collection.count_documents({
            "status": "closed"
        }),

        "total_applications": applications_collection.count_documents({})
    }


# ==========================================
# GET ALL COMPANIES
# ==========================================

@router.get("/companies")
def get_all_companies(
    current_user: dict = Depends(require_role("admin")),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    companies = companies_collection.find(
        {}
    ).skip(skip).limit(limit)

    return [
        {
            "id": str(company["_id"]),
            "name": company.get("name"),
            "description": company.get("description"),
            "industry": company.get("industry"),
            "website": company.get("website"),
            "location": company.get("location"),
            "size": company.get("size"),
            "created_at": company.get("created_at")
        }
        for company in companies
    ]


# ==========================================
# DELETE COMPANY
# ==========================================

@router.delete("/companies/{company_id}")
def delete_company(
    company_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    try:
        object_id = ObjectId(company_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID"
        )

    company = companies_collection.find_one({
        "_id": object_id
    })

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    company_id_str = str(object_id)

    # Delete related job offers and applications
    job_ids = [
        str(job["_id"])
        for job in job_offers_collection.find(
            {"company_id": company_id_str},
            {"_id": 1}
        )
    ]

    applications_collection.delete_many({
        "job_offer_id": {"$in": job_ids}
    })

    job_offers_collection.delete_many({
        "company_id": company_id_str
    })

    # Delete company memberships
    from app.database.connection import company_members_collection

    company_members_collection.delete_many({
        "company_id": company_id_str
    })

    companies_collection.delete_one({
        "_id": object_id
    })

    return {
        "message": "Company and its related job offers were deleted successfully",
        "company_id": company_id_str,
        "deleted_job_offers": len(job_ids)
    }


# ==========================================
# GET ALL JOB OFFERS
# ==========================================

@router.get("/job-offers")
def get_all_job_offers(
    current_user: dict = Depends(require_role("admin")),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    jobs = job_offers_collection.find(
        {}
    ).skip(skip).limit(limit)

    return [
        {
            "id": str(job["_id"]),
            "title": job.get("title"),
            "company_id": job.get("company_id"),
            "description": job.get("description"),
            "required_skills": job.get("required_skills", []),
            "min_experience": job.get("min_experience", 0),
            "location": job.get("location"),
            "status": job.get("status"),
            "created_by": job.get("created_by"),
            "created_at": job.get("created_at")
        }
        for job in jobs
    ]


# ==========================================
# DELETE JOB OFFER
# ==========================================

@router.delete("/job-offers/{job_id}")
def delete_job_offer(
    job_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    try:
        object_id = ObjectId(job_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job offer ID"
        )

    job = job_offers_collection.find_one({
        "_id": object_id
    })

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job offer not found"
        )

    job_id_str = str(object_id)

    # Delete applications associated with this job
    applications_collection.delete_many({
        "job_offer_id": job_id_str
    })

    job_offers_collection.delete_one({
        "_id": object_id
    })

    return {
        "message": "Job offer and its applications deleted successfully",
        "job_id": job_id_str
    }


# ==========================================
# GET ALL APPLICATIONS
# ==========================================

@router.get("/applications")
def get_all_applications(
    current_user: dict = Depends(require_role("admin")),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    applications = applications_collection.find(
        {}
    ).sort("applied_at", -1).skip(skip).limit(limit)

    return [
        {
            "id": str(application["_id"]),
            "candidate_id": application.get("candidate_id"),
            "job_offer_id": application.get("job_offer_id"),
            "status": application.get("status"),
            "applied_at": application.get("applied_at")
        }
        for application in applications
    ]
