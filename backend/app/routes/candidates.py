
import os
import shutil
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
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
        "cv_filename": candidate.get("cv_filename"),
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
            "cv_filename": updated_candidate.get("cv_filename"),
            "updated_at": updated_candidate["updated_at"]
        }
    }


# -------------------------
# Candidate CV Management
# -------------------------

CV_UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "cvs")


@router.post("/me/cv")
async def upload_candidate_cv(
    file: UploadFile = File(...),
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

    allowed_exts = {".pdf", ".doc", ".docx", ".txt", ".rtf"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Allowed: PDF, DOC, DOCX, TXT, RTF"
        )

    os.makedirs(CV_UPLOAD_DIR, exist_ok=True)
    file_id = uuid.uuid4().hex
    safe_filename = "".join(c for c in (file.filename or "cv.pdf") if c.isalnum() or c in "._- ")
    saved_name = f"profile_{candidate['_id']}_{file_id}_{safe_filename}"
    saved_path = os.path.join(CV_UPLOAD_DIR, saved_name)

    # Delete previous file if exists
    old_path = candidate.get("cv_path")
    if old_path and os.path.exists(old_path):
        try:
            os.remove(old_path)
        except OSError:
            pass

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    now = datetime.now(timezone.utc)
    candidates_collection.update_one(
        {"_id": candidate["_id"]},
        {"$set": {
            "cv_filename": file.filename,
            "cv_path": saved_path,
            "updated_at": now
        }}
    )

    return {
        "message": "CV uploaded successfully",
        "cv_filename": file.filename
    }


@router.get("/me/cv")
def get_candidate_cv(
    current_user: dict = Depends(require_role("candidate"))
):
    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if not candidate or not candidate.get("cv_path") or not os.path.exists(candidate["cv_path"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV file not found"
        )

    cv_filename = candidate.get("cv_filename", "resume.pdf")
    media_type = "application/pdf" if cv_filename.lower().endswith(".pdf") else "application/octet-stream"

    return FileResponse(
        path=candidate["cv_path"],
        filename=cv_filename,
        media_type=media_type
    )


@router.delete("/me/cv", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate_cv(
    current_user: dict = Depends(require_role("candidate"))
):
    candidate = candidates_collection.find_one({
        "user_id": current_user["id"]
    })

    if candidate and candidate.get("cv_path") and os.path.exists(candidate["cv_path"]):
        try:
            os.remove(candidate["cv_path"])
        except OSError:
            pass

    candidates_collection.update_one(
        {"user_id": current_user["id"]},
        {"$set": {
            "cv_filename": None,
            "cv_path": None,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    return None
