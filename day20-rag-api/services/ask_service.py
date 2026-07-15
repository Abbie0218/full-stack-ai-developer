from models import Conversation, Message
from services.rag_service import get_answer
from fastapi import HTTPException

class AskService:
    def __init__(self, db):
        self.db = db

    def ask(self, question: str, user_id: int, conversation_id: int = None) -> dict:
        # get or create conversation
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(
                user_id=user_id,
                title=question[:50]
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        # get history
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        history = [{"role": m.role, "content": m.content} for m in messages]

        # get answer
        result = get_answer(
            question=question,
            user_id=user_id,
            history=history
        )

        # save to DB
        self.db.add(Message(
            conversation_id=conversation.id,
            role="user",
            content=question
        ))
        self.db.add(Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"]
        ))
        self.db.commit()

        return {
            "answer": result["answer"],
            "conversation_id": conversation.id,
            "sources": result["sources"]
        }