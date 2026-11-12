
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from app.database.connection import (
    applications_collection,
    candidates_collection,
    job_offers_collection,
    company_members_collection
)

from app.core.dependencies import (
    get_current_user,
    require_role
)

from app.models.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


# =====================================
# HELPER 1: GET APPLICATION
# =====================================

def get_application_or_404(application_id: str):

    try:
        object_id = ObjectId(application_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid application ID"
        )

    application = applications_collection.find_one({
        "_id": object_id
    })

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application


# =====================================
# HELPER 2: GET JOB OFFER
# =====================================

def get_job_offer(job_offer_id: str):

    try:
        object_id = ObjectId(job_offer_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid job offer ID"
        )

    job = job_offers_collection.find_one({
        "_id": object_id
    })

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job offer not found"
        )

    return job


# =====================================
# HELPER 3: CHECK RECRUITER PERMISSION
# =====================================

def check_recruiter_permission(
    job: dict,
    current_user: dict
):

    if current_user["role"] == "admin":
        return

    membership = company_members_collection.find_one({
        "company_id": job["company_id"],
        "recruiter_id": current_user["id"]
    })

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this company"
        )

    # Company owner or company admin
    if membership["role"] in ["owner", "admin"]:
        return

    # Regular recruiter can manage applications
    # for offers they created
    if job["created_by"] == current_user["id"]:
        return

    raise HTTPException(
        status_code=403,
        detail="You cannot manage applications for this job offer"
    )


# =====================================
# 1. CREATE APPLICATION
# =====================================

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_application(
    data: ApplicationCreate,
    current_user: dict = Depends(require_role("candidate"))
):

    # Find candidate profile
    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    # Find job offer
    job = get_job_offer(data.job_offer_id)

    # Only open offers accept applications
    if job["status"] != "open":
        raise HTTPException(
            status_code=400,
            detail="This job offer is not accepting applications"
        )

    candidate_id = str(candidate["_id"])

    # Check for an existing application
    existing_application = applications_collection.find_one({
        "candidate_id": candidate_id,
        "job_offer_id": data.job_offer_id
    })

    if existing_application:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job"
        )

    now = datetime.now(timezone.utc)

    application_document = {
        "candidate_id": candidate_id,
        "job_offer_id": data.job_offer_id,
        "cover_letter": data.cover_letter,
        "status": "pending",
        "applied_at": now,
        "updated_at": now
    }

    try:

        result = applications_collection.insert_one(
            application_document
        )

    except Exception as error:

        # Protect against duplicate submissions
        from pymongo.errors import DuplicateKeyError

        if isinstance(error, DuplicateKeyError):
            raise HTTPException(
                status_code=409,
                detail="You have already applied for this job"
            )

        raise

    application_document["id"] = str(result.inserted_id)

    return application_document


# =====================================
# 2. GET MY APPLICATIONS (CANDIDATE)
# =====================================

@router.get(
    "/my",
    response_model=list[ApplicationResponse]
)
def get_my_applications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_role("candidate"))
):

    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    candidate_id = str(candidate["_id"])

    cursor = (
        applications_collection
        .find({"candidate_id": candidate_id})
        .sort("applied_at", -1)
        .skip(skip)
        .limit(limit)
    )

    applications = []

    for application in cursor:

        application["id"] = str(application["_id"])

        applications.append(application)

    return applications


# =====================================
# 3. GET APPLICATIONS RECEIVED (RECRUITER)
# =====================================

@router.get(
    "/received",
    response_model=list[ApplicationResponse]
)
def get_received_applications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(
        require_role("recruiter", "admin")
    )
):

    if current_user["role"] == "admin":

        jobs = job_offers_collection.find(
            {},
            {"_id": 1}
        )

    else:

        # Recruiter can see applications for:
        # 1. Offers they created
        # 2. Offers belonging to companies they own/administer

        memberships = company_members_collection.find({
            "recruiter_id": current_user["id"],
            "role": {"$in": ["owner", "admin"]}
        })

        company_ids = [
            membership["company_id"]
            for membership in memberships
        ]

        jobs = job_offers_collection.find(
            {
                "$or": [
                    {"created_by": current_user["id"]},
                    {"company_id": {"$in": company_ids}}
                ]
            },
            {"_id": 1}
        )

    job_ids = [
        str(job["_id"])
        for job in jobs
    ]

    cursor = (
        applications_collection
        .find({"job_offer_id": {"$in": job_ids}})
        .sort("applied_at", -1)
        .skip(skip)
        .limit(limit)
    )

    applications = []

    for application in cursor:

        application["id"] = str(application["_id"])

        applications.append(application)

    return applications


# =====================================
# 4. GET APPLICATION DETAILS
# =====================================

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse
)
def get_application_details(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):

    application = get_application_or_404(application_id)

    # Candidate can view only their own application
    if current_user["role"] == "candidate":

        candidate = candidates_collection.find_one({
            "user_id": current_user["id"]
        })

        if not candidate or application["candidate_id"] != str(candidate["_id"]):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this application"
            )

    # Recruiter must have permission for the associated job
    elif current_user["role"] == "recruiter":

        job = get_job_offer(application["job_offer_id"])

        check_recruiter_permission(
            job,
            current_user
        )

    elif current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    application["id"] = str(application["_id"])

    return application


# =====================================
# 5. UPDATE APPLICATION
# =====================================

@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse
)
def update_application(
    application_id: str,
    data: ApplicationUpdate,
    current_user: dict = Depends(get_current_user)
):

    application = get_application_or_404(application_id)

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Candidate can update their cover letter
    # only while the application is pending
    if current_user["role"] == "candidate":

        candidate = candidates_collection.find_one({
            "user_id": current_user["id"]
        })

        if not candidate or application["candidate_id"] != str(candidate["_id"]):
            raise HTTPException(
                status_code=403,
                detail="You cannot update this application"
            )

        if application["status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail="You can only edit a pending application"
            )

        if set(update_data.keys()) != {"cover_letter"}:
            raise HTTPException(
                status_code=403,
                detail="Candidates can only update their cover letter"
            )

    # Recruiters and admins can update application status
    elif current_user["role"] in ["recruiter", "admin"]:

        if set(update_data.keys()) != {"status"}:
            raise HTTPException(
                status_code=400,
                detail="Recruiters can only update application status"
            )

        if current_user["role"] == "recruiter":

            job = get_job_offer(application["job_offer_id"])

            check_recruiter_permission(
                job,
                current_user
            )

    else:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    update_data["updated_at"] = datetime.now(timezone.utc)

    applications_collection.update_one(
        {"_id": application["_id"]},
        {"$set": update_data}
    )

    updated_application = applications_collection.find_one({
        "_id": application["_id"]
    })

    updated_application["id"] = str(
        updated_application["_id"]
    )

    return updated_application


# =====================================
# 6. DELETE / WITHDRAW APPLICATION
# =====================================

@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def withdraw_application(
    application_id: str,
    current_user: dict = Depends(require_role("candidate"))
):

    application = get_application_or_404(application_id)

    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if not candidate or application["candidate_id"] != str(candidate["_id"]):
        raise HTTPException(
            status_code=403,
            detail="You cannot withdraw this application"
        )

    applications_collection.delete_one({
        "_id": application["_id"]
    })

    return None
