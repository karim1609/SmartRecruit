
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
    job_offers_collection,
    companies_collection,
    company_members_collection
)

from app.core.dependencies import (
    get_current_user,
    require_role
)

from app.models.job_offer import (
    JobOfferCreate,
    JobOfferUpdate,
    JobOfferResponse
)


router = APIRouter(
    prefix="/job-offers",
    tags=["Job Offers"]
)


# =====================================
# HELPER 1: GET JOB OFFER
# =====================================

def get_job_offer_or_404(job_offer_id: str):

    try:
        object_id = ObjectId(job_offer_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid job offer ID"
        )

    job_offer = job_offers_collection.find_one({
        "_id": object_id
    })

    if not job_offer:
        raise HTTPException(
            status_code=404,
            detail="Job offer not found"
        )

    return job_offer


# =====================================
# HELPER 2: VERIFY COMPANY MEMBERSHIP
# =====================================

def get_company_membership(
    company_id: str,
    user_id: str
):

    try:
        company_object_id = ObjectId(company_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid company ID"
        )

    company = companies_collection.find_one({
        "_id": company_object_id
    })

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    membership = company_members_collection.find_one({
        "company_id": company_id,
        "recruiter_id": user_id
    })

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this company"
        )

    return membership


# =====================================
# HELPER 3: CHECK OFFER MANAGEMENT
# =====================================

def check_offer_permission(
    job_offer: dict,
    current_user: dict
):

    # Platform administrator
    if current_user["role"] == "admin":
        return

    membership = get_company_membership(
        job_offer["company_id"],
        current_user["id"]
    )

    # Company owner or company admin
    if membership["role"] in ["owner", "admin"]:
        return

    # Regular recruiter can manage their own offers
    if job_offer["created_by"] == current_user["id"]:
        return

    raise HTTPException(
        status_code=403,
        detail="You don't have permission to manage this job offer"
    )


# =====================================
# 1. CREATE JOB OFFER
# =====================================

@router.post(
    "/",
    response_model=JobOfferResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job_offer(
    data: JobOfferCreate,
    current_user: dict = Depends(require_role("recruiter"))
):

    # Verify recruiter belongs to the company
    get_company_membership(
        data.company_id,
        current_user["id"]
    )

    now = datetime.now(timezone.utc)

    job_document = data.model_dump()

    # Add server-controlled fields
    job_document.update({
        "created_by": current_user["id"],
        "created_at": now,
        "updated_at": now
    })

    result = job_offers_collection.insert_one(
        job_document
    )

    job_document["id"] = str(result.inserted_id)

    return job_document


# =====================================
# 2. GET ALL OPEN JOB OFFERS
# =====================================

@router.get(
    "/",
    response_model=list[JobOfferResponse]
)
def get_job_offers(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):

    cursor = (
        job_offers_collection
        .find({"status": "open"})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    job_offers = []

    for job in cursor:

        job["id"] = str(job["_id"])

        job_offers.append(job)

    return job_offers


# =====================================
# 3. GET MY JOB OFFERS
# =====================================

@router.get(
    "/my",
    response_model=list[JobOfferResponse]
)
def get_my_job_offers(
    current_user: dict = Depends(require_role("recruiter"))
):

    cursor = job_offers_collection.find({
        "created_by": current_user["id"]
    }).sort("created_at", -1)

    job_offers = []

    for job in cursor:

        job["id"] = str(job["_id"])

        job_offers.append(job)

    return job_offers


# =====================================
# 4. GET JOB OFFER DETAILS
# =====================================

@router.get(
    "/{job_offer_id}",
    response_model=JobOfferResponse
)
def get_job_offer(job_offer_id: str):

    job = get_job_offer_or_404(job_offer_id)

    # Public users can only see published offers
    if job["status"] != "open":

        raise HTTPException(
            status_code=404,
            detail="Job offer not found"
        )

    job["id"] = str(job["_id"])

    return job


# =====================================
# 5. UPDATE JOB OFFER
# =====================================

@router.patch(
    "/{job_offer_id}",
    response_model=JobOfferResponse
)
def update_job_offer(
    job_offer_id: str,
    data: JobOfferUpdate,
    current_user: dict = Depends(
        require_role("recruiter", "admin")
    )
):

    job = get_job_offer_or_404(job_offer_id)

    # Check permissions
    check_offer_permission(
        job,
        current_user
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:

        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Do not allow moving an offer to another company
    # through this endpoint.
    if "company_id" in update_data:

        raise HTTPException(
            status_code=400,
            detail="Company association cannot be changed here"
        )

    # Prevent required fields from being set to null
    required_fields = [
        "title",
        "description",
        "location",
        "min_experience",
        "status",
        "required_skills"
    ]

    for field in required_fields:

        if field in update_data and update_data[field] is None:

            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    update_data["updated_at"] = datetime.now(timezone.utc)

    job_offers_collection.update_one(
        {"_id": job["_id"]},
        {"$set": update_data}
    )

    updated_job = job_offers_collection.find_one({
        "_id": job["_id"]
    })

    updated_job["id"] = str(updated_job["_id"])

    return updated_job


# =====================================
# 6. DELETE JOB OFFER
# =====================================

@router.delete(
    "/{job_offer_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_job_offer(
    job_offer_id: str,
    current_user: dict = Depends(
        require_role("recruiter", "admin")
    )
):

    job = get_job_offer_or_404(job_offer_id)

    # Check permissions
    check_offer_permission(
        job,
        current_user
    )

    job_offers_collection.delete_one({
        "_id": job["_id"]
    })

    return None
