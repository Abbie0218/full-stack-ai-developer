from sqlalchemy import select
from sqlalchemy.orm import Session
from models import UploadJob,Status

class UploadRepository:
    def __init__(self, db:Session):
        self.db=db
    
    def create_job(self, user_id:int, filename:str)->UploadJob:
        job = UploadJob(
            user_id=user_id,
            file_name=filename,
            status=Status.PROCESSING
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job(self, job_id:int, user_id:int)->UploadJob:
        return self.db.execute(
            select(UploadJob).where(
                UploadJob.id==job_id,
                UploadJob.user_id == user_id
            )
        ).scalar_one_or_none()

    def update_status(self, job_id:int, status:str, error:str=None):
        job = self.db.execute(
            select(UploadJob).where(
                UploadJob.id == job_id
            )
        ).scalar_one_or_none()

        if job:
            job.status = status
            job.error = error
            self.db.commit()