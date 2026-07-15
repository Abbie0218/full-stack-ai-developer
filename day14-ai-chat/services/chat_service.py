from repository.chat_repository import ChatRepository
from fastapi import HTTPException


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def create_session(self, user_id: int, title: str):

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID  is mandatory")

        if len(title.strip()) < 3:
            raise HTTPException(status_code=400, detail="title is too short")
        return self.repo.create_session(user_id, title)

    def get_all_session(self, user_id: int):

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        return self.repo.get_sessions(user_id)

    def get_session_by_id(self, session_id: int):

        if not session_id:
            raise HTTPException(status_code=400, detail="session ID is required")
        return self.repo.get_messages(session_id)


    def create_message(self, session_id: int, role: str, content: str):
        if not content.strip():
            raise HTTPException(status_code=400, detail="content required")
        return self.repo.create_message(session_id, role, content)  # ✅ pass args
