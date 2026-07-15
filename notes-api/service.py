from respository import NoteRepository
from schemas import NoteRequest, NoteUpdateRequest
from fastapi import HTTPException
from models import Notes

ALLOWED_TAGS=['work','personal','study']
class NotesService:
    def __init__(self, repo:NoteRepository):
        self.repo = repo
    
    def create_note(self, data:NoteRequest, user_id:int):
        
        # title cannot be less than 3 characters
        if len(data.title.strip()) < 3:
            raise HTTPException(status_code=400, detail="title is too short")
        
        # title cannot be greater than 100 characters
        if len(data.title.strip()) > 100:
            raise HTTPException(
                status_code=400,
                detail="Title cannot exceed 100 characters"
            )
        
        #content cannot be empty
        if not data.content.strip():
            raise HTTPException(
                status_code=400,
                detail="Content cannot be empty"
            )
        
        if data.tag not in ALLOWED_TAGS:
            raise HTTPException(
                status_code=400,
                detail=f"Tage must be one of the {ALLOWED_TAGS}"
            )
        new_note = Notes(
            title=data.title,
            content=data.content,
            tag=data.tag,
            user_id=user_id
        )

        return self.repo.create_note(new_note)


    def get_all_notes(self,user_id:int, tag:str | None = None, search:str | None = None, skip:int = 0, limit:int=0):
        return self.repo.list_all_notes(
            user_id=user_id,
            tag=tag,
            search=search,
            skip=skip,
            limit=limit
            )


    def get_note(self, note_id:int,user_id:int):
        note = self.repo.get_note_by_id(note_id)
        if not note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        if note.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized"
            )
        return note

    
    def delete_note(self, note_id:int, user_id:int):
        note = self.repo.get_note_by_id(note_id)
        if not note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        if note.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized"
            )
        return self.repo.delete_note(note_id)
    
    def update_note(self, note_id:int, data:NoteUpdateRequest, user_id:int):
       
        note = self.repo.get_note_by_id(note_id)
        if not note:
            raise HTTPException(
                status_code=404,
                detail="Note not found"
            )
        if note.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized"
            )
        if data.title is not None:
            if len(data.title.strip()) < 3:
                raise HTTPException(status_code=400, detail="title is too short")
            
            # title cannot be greater than 100 characters
            if len(data.title.strip()) > 100:
                raise HTTPException(
                    status_code=400,
                    detail="Title cannot exceed 100 characters"
                )
        if data.content is not None:

            #content cannot be empty
            if not data.content.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Content cannot be empty"
                )
        if data.tag is not None:

            if data.tag not in ALLOWED_TAGS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tage must be one of the {ALLOWED_TAGS}"
                )
            
        update_note = data.model_dump(exclude_unset=True)
        
        for key, value in update_note.items():
            setattr(note, key, value)
            
        return self.repo.update_note(note)