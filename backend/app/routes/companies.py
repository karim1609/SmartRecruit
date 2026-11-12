
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.database.connection import (
    companies_collection,
    company_members_collection,
    recruiters_collection
)

from app.core.dependencies import (
    get_current_user,
    require_role
)

from app.models.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


# =====================================
# HELPER: FIND COMPANY
# =====================================

def get_company_or_404(company_id: str):

    try:
        object_id = ObjectId(company_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid company ID"
        )

    company = companies_collection.find_one({
        "_id": object_id
    })

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return company


# =====================================
# HELPER: CHECK COMPANY PERMISSION
# =====================================

def check_company_permission(
    company_id: str,
    current_user: dict,
    required_role: str | None = None
):

    # Admin can access all companies
    if current_user["role"] == "admin":
        return

    membership = company_members_collection.find_one({
        "company_id": company_id,
        "recruiter_id": current_user["id"]
    })

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this company"
        )

    if required_role and membership["role"] != required_role:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to perform this action"
        )


# =====================================
# 1. CREATE COMPANY
# =====================================

@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED
)
def create_company(
    data: CompanyCreate,
    current_user: dict = Depends(require_role("recruiter"))
):

    # Verify recruiter profile exists
    recruiter = recruiters_collection.find_one({
        "user_id": current_user["id"]
    })

    if not recruiter:
        raise HTTPException(
            status_code=404,
            detail="Recruiter profile not found"
        )

    now = datetime.now(timezone.utc)

    company_document = data.model_dump()

    company_document.update({
        "created_by": current_user["id"],
        "created_at": now,
        "updated_at": now
    })

    result = companies_collection.insert_one(company_document)

    company_id = str(result.inserted_id)

    try:

        # The creator automatically becomes the owner
        company_members_collection.insert_one({
            "company_id": company_id,
            "recruiter_id": current_user["id"],
            "role": "owner",
            "joined_at": now
        })

    except Exception:

        # Clean up the company if membership creation fails
        companies_collection.delete_one({
            "_id": result.inserted_id
        })

        raise HTTPException(
            status_code=500,
            detail="Could not complete company creation"
        )

    company_document["id"] = company_id

    return company_document


# =====================================
# 2. GET MY COMPANIES
# =====================================

@router.get(
    "/me",
    response_model=list[CompanyResponse]
)
def get_my_companies(
    current_user: dict = Depends(require_role("recruiter"))
):

    memberships = company_members_collection.find({
        "recruiter_id": current_user["id"]
    })

    companies = []

    for membership in memberships:

        company = companies_collection.find_one({
            "_id": ObjectId(membership["company_id"])
        })

        if company:
            company["id"] = str(company["_id"])
            companies.append(company)

    return companies


# =====================================
# 3. GET COMPANY DETAILS
# =====================================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse
)
def get_company(
    company_id: str,
    current_user: dict = Depends(get_current_user)
):

    company = get_company_or_404(company_id)

    check_company_permission(
        company_id,
        current_user
    )

    company["id"] = str(company["_id"])

    return company


# =====================================
# 4. UPDATE COMPANY
# =====================================

@router.patch(
    "/{company_id}",
    response_model=CompanyResponse
)
def update_company(
    company_id: str,
    data: CompanyUpdate,
    current_user: dict = Depends(get_current_user)
):

    company = get_company_or_404(company_id)

    # Only the owner or platform admin can update
    check_company_permission(
        company_id,
        current_user,
        required_role="owner"
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Prevent explicit null values for required fields
    for field in [
        "name",
        "description",
        "industry",
        "location"
    ]:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    update_data["updated_at"] = datetime.now(timezone.utc)

    companies_collection.update_one(
        {"_id": company["_id"]},
        {"$set": update_data}
    )

    updated_company = companies_collection.find_one({
        "_id": company["_id"]
    })

    updated_company["id"] = str(updated_company["_id"])

    return updated_company
