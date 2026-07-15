from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from schemas import AskRequest
from services.ask_service import AskService

router = APIRouter(prefix="/ask", tags=["Ask"])

def get_service(db: Session = Depends(get_db)) -> AskService:
    return AskService(db)

@router.post("/")
def ask(
    request: AskRequest,
    current_user: dict = Depends(get_current_user),
    service: AskService = Depends(get_service)
):
    return service.ask(
        question=request.question,
        user_id=current_user["user_id"],
        conversation_id=request.conversation_id
    )