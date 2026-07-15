from fastapi import APIRouter, Depends
from database import get_db
from schemas import NoteRequest, NoteUpdateRequest
from service import NotesService
from sqlalchemy.orm import Session
from respository import NoteRepository
from auth import get_current_user, require_role
from models import UserRole
router = APIRouter()

def get_service(db:Session=Depends(get_db))->NotesService:
    return NotesService(NoteRepository(db))

@router.post("/notes",tags=["Notes"])
async def add_new_note(note:NoteRequest,service:NotesService=Depends(get_service),current_user: dict = Depends(get_current_user)):
    return service.create_note(note, user_id=1)

@router.get("/notes",tags=["Notes"])
async def list_notes(
    tag: str | None = None,      # ?tag=work
    search: str | None = None,   # ?search=python
    skip: int = 0,               # ?skip=0
    limit: int = 10,             # ?limit=10
    service: NotesService = Depends(get_service),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    return service.get_all_notes(
        user_id=1,
        tag=tag,
        search=search,
        skip=skip,
        limit=limit
    )

@router.get("/notes/{note_id}",tags=["Notes"])
async def fetch_note_by_id(note_id:int, service:NotesService=Depends(get_service),current_user: dict = Depends(get_current_user)):
    return service.get_note(note_id,user_id=1)

@router.patch("/notes/{note_id}",tags=["Notes"])
async def patch_note(note_id:int, data:NoteUpdateRequest, service:NotesService=Depends(get_service),current_user: dict = Depends(get_current_user)):
    return service.update_note(note_id,data,user_id=1)

@router.delete("/notes/{note_id}",tags=["Notes"])
async def remove_note(note_id:int, service:NotesService=Depends(get_service),current_user: dict = Depends(require_role(UserRole.ADMIN))):
    return service.delete_note(note_id,user_id=1)