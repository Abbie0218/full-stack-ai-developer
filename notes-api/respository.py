from sqlalchemy import select, func
from models import Notes
from sqlalchemy.orm import Session

class NoteRepository:
    def __init__(self, db:Session):
        self.db = db
    def get_note_by_id(self, note_id:int):
        return self.db.execute(
            select(Notes).where(Notes.id == note_id)
            ).scalar_one_or_none()
    
    # get all notes route
    def list_all_notes(
        self,
        user_id:int,
        tag:str | None = None,
        search:str | None = None,
        skip: int=0,
        limit:int=0):

        query = select(Notes).where(Notes.user_id == user_id)

        if tag:
            query = select(Notes).where(Notes.tag == tag)
        
        if search:
            query = select(Notes).where(Notes.title.ilike(f"%{search}%"))

        total = self.db.execute(select(func.count()).select_from(query.subquery())).scalar()

        query = query.offset(skip).limit(limit)

        notes = self.db.execute(
            select(Notes).where(Notes.user_id == user_id)
        ).scalars().all()

        return {"total": total, "notes": notes}
    
    # delete note route

    def delete_note(self, note_id:int):
        note = self.get_note_by_id(note_id)
        if not note:
            return None
        self.db.delete(note)
        self.db.commit()
    
    #create note route

    def create_note(self, note:Notes):
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def update_note(self, note:Notes):
        self.db.commit()
        self.db.refresh(note)
        return note