from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Message, Session as ChatSession

class ChatRepository:
    def __init__(self,db:Session):
        self.db=db

    def create_message(self, session_id: int, role: str, content: str):  # ✅ takes args
        message = Message(session_id=session_id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_sessions(self,user_id):
        query=select(ChatSession).where(ChatSession.user_id==user_id)
        return self.db.execute(query).scalars().all()
    
    def get_messages(self,session_id):
        query=select(Message).where(Message.session_id==session_id)
        return self.db.execute(query).scalars().all()

    def create_session(self, user_id: int, title: str = None):
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session