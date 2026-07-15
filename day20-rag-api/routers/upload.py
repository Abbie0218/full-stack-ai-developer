from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from repository.upload_repository import UploadRepository
from services.pdf_service import process_pdf

router = APIRouter(prefix="/upload", tags=["Upload"])

def get_repo(db: Session = Depends(get_db)) -> UploadRepository:
    return UploadRepository(db)

@router.post("/", status_code=202)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    repo: UploadRepository = Depends(get_repo)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # save temp file
    temp_path = f"./temp_{file.filename}"
    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)

    # create job in DB
    job = repo.create_job(
        user_id=current_user["user_id"],
        filename=file.filename
    )

    # start background processing
    background_tasks.add_task(
        process_pdf,
        temp_path=temp_path,
        job_id=job.id,
        user_id=current_user["user_id"],
        filename=file.filename
    )

    return {
        "job_id": job.id,
        "status": "processing",
        "filename": file.filename
    }

@router.get("/status/{job_id}")
def get_job_status(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    repo: UploadRepository = Depends(get_repo)
):
    job = repo.get_job(job_id, current_user["user_id"])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status.value,
        "file_name": job.file_name,
        "error": job.error
    }