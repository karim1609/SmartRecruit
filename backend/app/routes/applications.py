
import os
import shutil
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    UploadFile,
    File,
    status
)
from fastapi.responses import FileResponse

from app.database.connection import (
    applications_collection,
    candidates_collection,
    job_offers_collection,
    company_members_collection,
    companies_collection,
    users_collection,
)

from app.core.dependencies import (
    get_current_user,
    require_role
)
from app.services.email_service import email_service

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


APP_CV_UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "cvs")


# =====================================
# 1. CREATE APPLICATION
# =====================================

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_application(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role("candidate"))
):

    content_type = request.headers.get("content-type", "")
    job_offer_id: str = ""
    cover_letter: str | None = None
    cv_option: str = "profile"
    uploaded_file: UploadFile | None = None

    if "multipart/form-data" in content_type:
        form = await request.form()
        job_offer_id = str(form.get("job_offer_id") or "")
        cover_val = form.get("cover_letter")
        if cover_val:
            cover_letter = str(cover_val)
        cv_option = str(form.get("cv_option") or "profile")
        file_val = form.get("cv_file")
        if file_val and hasattr(file_val, "filename") and file_val.filename:
            uploaded_file = file_val
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid request body"
            )
        job_offer_id = str(body.get("job_offer_id") or "")
        cover_letter = body.get("cover_letter")
        cv_option = str(body.get("cv_option") or "profile")

    if not job_offer_id:
        raise HTTPException(
            status_code=400,
            detail="Job offer ID is required"
        )

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
    job = get_job_offer(job_offer_id)

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
        "job_offer_id": job_offer_id
    })

    if existing_application:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job"
        )

    # Handle CV selection
    cv_filename: str | None = None
    cv_path: str | None = None

    if cv_option == "custom":
        if not uploaded_file or not uploaded_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Custom CV file is required when choosing custom CV option"
            )

        allowed_exts = {".pdf", ".doc", ".docx", ".txt", ".rtf"}
        ext = os.path.splitext(uploaded_file.filename)[1].lower()
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Allowed: PDF, DOC, DOCX, TXT, RTF"
            )

        os.makedirs(APP_CV_UPLOAD_DIR, exist_ok=True)
        file_id = uuid.uuid4().hex
        safe_filename = "".join(c for c in uploaded_file.filename if c.isalnum() or c in "._- ")
        saved_name = f"app_{job_offer_id}_{candidate_id}_{file_id}_{safe_filename}"
        saved_path = os.path.join(APP_CV_UPLOAD_DIR, saved_name)

        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

        cv_filename = uploaded_file.filename
        cv_path = saved_path
    elif cv_option == "profile":
        if not candidate.get("cv_path") or not os.path.exists(candidate["cv_path"]):
            raise HTTPException(
                status_code=400,
                detail="No CV found in your profile. Please upload a CV to your profile or choose the custom CV option."
            )
        cv_filename = candidate.get("cv_filename")
        cv_path = candidate.get("cv_path")

    now = datetime.now(timezone.utc)

    application_document = {
        "candidate_id": candidate_id,
        "job_offer_id": job_offer_id,
        "cover_letter": cover_letter,
        "cv_filename": cv_filename,
        "cv_path": cv_path,
        "status": "pending",
        "applied_at": now,
        "updated_at": now
    }

    try:
        result = applications_collection.insert_one(
            application_document
        )
    except Exception as error:
        from pymongo.errors import DuplicateKeyError
        if isinstance(error, DuplicateKeyError):
            raise HTTPException(
                status_code=409,
                detail="You have already applied for this job"
            )
        raise

    application_document["id"] = str(result.inserted_id)

    # Dispatch application confirmation email asynchronously in background
    try:
        candidate_email = current_user.get("email")
        candidate_name = candidate.get("full_name") or current_user.get("full_name") or "Candidate"
        job_title = job.get("title", "Position")

        # Retrieve company name
        company_name = "SmartRecruit Partner"
        if job.get("company_id"):
            try:
                comp = companies_collection.find_one({"_id": ObjectId(job["company_id"])})
                if comp and comp.get("name"):
                    company_name = comp["name"]
            except Exception:
                pass

        if candidate_email:
            background_tasks.add_task(
                email_service.send_application_confirmation,
                to_email=candidate_email,
                candidate_name=candidate_name,
                job_title=job_title,
                company_name=company_name,
            )
    except Exception as exc:
        # Never fail application creation if email task scheduling encounters an issue
        pass

    return application_document


# =====================================
# DOWNLOAD APPLICATION CV
# =====================================

@router.get("/{application_id}/cv")
def get_application_cv(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    application = get_application_or_404(application_id)

    # Candidate can view only their own application CV
    if current_user["role"] == "candidate":
        candidate = candidates_collection.find_one({
            "user_id": current_user["id"]
        })
        if not candidate or application["candidate_id"] != str(candidate["_id"]):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this CV"
            )
    elif current_user["role"] == "recruiter":
        job = get_job_offer(application["job_offer_id"])
        check_recruiter_permission(job, current_user)
    elif current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    cv_path = application.get("cv_path")
    cv_filename = application.get("cv_filename", "resume.pdf")

    if not cv_path or not os.path.exists(cv_path):
        raise HTTPException(
            status_code=404,
            detail="CV file not found for this application"
        )

    media_type = "application/pdf" if cv_filename.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(
        path=cv_path,
        filename=cv_filename,
        media_type=media_type
    )


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
