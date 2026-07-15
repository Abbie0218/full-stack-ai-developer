from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: int    
    content: str       

class SessionList(BaseModel):
    id:int
    user_id:int
    title:str|None
    created_at:datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id:int
    role:str
    content:str
    created_at:str
    session_id:int

    class Config:
        from_attributes = True