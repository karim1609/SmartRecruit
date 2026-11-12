
from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connection import (
    users_collection,
    candidates_collection,
    recruiters_collection,
    companies_collection,
    company_members_collection,
    job_offers_collection,
    applications_collection
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# CANDIDATE DASHBOARD
# ==========================================

def get_candidate_dashboard(user_id: str):

    candidate = candidates_collection.find_one({
        "user_id": user_id
    })

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    candidate_id = str(candidate["_id"])

    total_applications = applications_collection.count_documents({
        "candidate_id": candidate_id
    })

    pending_applications = applications_collection.count_documents({
        "candidate_id": candidate_id,
        "status": "pending"
    })

    reviewing_applications = applications_collection.count_documents({
        "candidate_id": candidate_id,
        "status": "reviewing"
    })

    accepted_applications = applications_collection.count_documents({
        "candidate_id": candidate_id,
        "status": "accepted"
    })

    rejected_applications = applications_collection.count_documents({
        "candidate_id": candidate_id,
        "status": "rejected"
    })

    recent_applications = list(
        applications_collection.find({
            "candidate_id": candidate_id
        }).sort("applied_at", -1).limit(5)
    )

    return {
        "role": "candidate",
        "profile": {
            "full_name": candidate.get("full_name"),
            "location": candidate.get("location"),
            "skills": candidate.get("skills", [])
        },
        "statistics": {
            "total_applications": total_applications,
            "pending": pending_applications,
            "reviewing": reviewing_applications,
            "accepted": accepted_applications,
            "rejected": rejected_applications
        },
        "recent_applications": [
            {
                "id": str(app["_id"]),
                "job_offer_id": app.get("job_offer_id"),
                "status": app.get("status"),
                "applied_at": app.get("applied_at")
            }
            for app in recent_applications
        ]
    }


# ==========================================
# RECRUITER DASHBOARD
# ==========================================

def get_recruiter_dashboard(user_id: str):

    recruiter = recruiters_collection.find_one({
        "user_id": user_id
    })

    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )

    # Find companies where this recruiter is a member
    memberships = list(
        company_members_collection.find({
            "recruiter_id": user_id
        })
    )

    company_ids = [
        membership["company_id"]
        for membership in memberships
    ]

    # Find jobs created by this recruiter OR belonging to their companies
    jobs_query = {
        "$or": [
            {"created_by": user_id},
            {"company_id": {"$in": company_ids}}
        ]
    }

    total_jobs = job_offers_collection.count_documents(
        jobs_query
    )

    open_jobs = job_offers_collection.count_documents({
        **jobs_query,
        "status": "open"
    })

    closed_jobs = job_offers_collection.count_documents({
        **jobs_query,
        "status": "closed"
    })

    job_ids = [
        str(job["_id"])
        for job in job_offers_collection.find(
            jobs_query,
            {"_id": 1}
        )
    ]

    total_applications = applications_collection.count_documents({
        "job_offer_id": {"$in": job_ids}
    })

    pending_applications = applications_collection.count_documents({
        "job_offer_id": {"$in": job_ids},
        "status": "pending"
    })

    accepted_applications = applications_collection.count_documents({
        "job_offer_id": {"$in": job_ids},
        "status": "accepted"
    })

    recent_jobs = list(
        job_offers_collection.find(
            jobs_query
        ).sort("created_at", -1).limit(5)
    )

    return {
        "role": "recruiter",
        "profile": {
            "full_name": recruiter.get("full_name"),
            "job_title": recruiter.get("job_title")
        },
        "statistics": {
            "total_jobs": total_jobs,
            "open_jobs": open_jobs,
            "closed_jobs": closed_jobs,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "accepted_applications": accepted_applications
        },
        "recent_jobs": [
            {
                "id": str(job["_id"]),
                "title": job.get("title"),
                "status": job.get("status"),
                "location": job.get("location"),
                "created_at": job.get("created_at")
            }
            for job in recent_jobs
        ]
    }


# ==========================================
# ADMIN DASHBOARD
# ==========================================

def get_admin_dashboard():

    total_users = users_collection.count_documents({})
    active_users = users_collection.count_documents({
        "is_active": True
    })

    total_candidates = candidates_collection.count_documents({})
    total_recruiters = recruiters_collection.count_documents({})

    total_companies = companies_collection.count_documents({})
    total_jobs = job_offers_collection.count_documents({})

    open_jobs = job_offers_collection.count_documents({
        "status": "open"
    })

    total_applications = applications_collection.count_documents({})

    pending_applications = applications_collection.count_documents({
        "status": "pending"
    })

    accepted_applications = applications_collection.count_documents({
        "status": "accepted"
    })

    rejected_applications = applications_collection.count_documents({
        "status": "rejected"
    })

    recent_users = list(
        users_collection.find(
            {},
            {"hashed_password": 0}
        ).sort("created_at", -1).limit(5)
    )

    return {
        "role": "admin",
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "total_candidates": total_candidates,
            "total_recruiters": total_recruiters,
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "open_jobs": open_jobs,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "accepted_applications": accepted_applications,
            "rejected_applications": rejected_applications
        },
        "recent_users": [
            {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "role": user.get("role"),
                "created_at": user.get("created_at")
            }
            for user in recent_users
        ]
    }


# ==========================================
# MAIN DASHBOARD ENDPOINT
# ==========================================

@router.get("/")
def get_dashboard(
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["id"]
    role = current_user["role"]

    if role == "candidate":
        return get_candidate_dashboard(user_id)

    elif role == "recruiter":
        return get_recruiter_dashboard(user_id)

    elif role == "admin":
        return get_admin_dashboard()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unsupported user role"
    )
