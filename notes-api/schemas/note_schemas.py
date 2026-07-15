from pydantic import BaseModel
from datetime import datetime

class NoteRequest(BaseModel):
    title: str
    content: str
    tag: str

class NoteDetails(BaseModel):
    id: int
    title: str
    content: str
    tag: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    tag: str | None = None