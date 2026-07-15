from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from database import get_db
from services.chat_service import ChatService
from repository.chat_repository import ChatRepository
from schemas.messages_schemas import ChatRequest
from auth import get_current_user
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_service(db:Session=Depends(get_db))->ChatService:
    return ChatService(ChatRepository(db))

@router.post('/session',tags=['Chat'])
async def create_session(user_id:int, title:str, service:ChatService=Depends(get_service),current_user: dict = Depends(get_current_user)):
    return service.create_session(current_user["user_id"], title)

@router.post('/message',tags=['Chat'])
async def create_chat(data:ChatRequest,service:ChatService=Depends(get_service)):
    return service.create_message(
        session_id=data.session_id,
        role="user",
        content=data.content
    )

@router.get("/session-list",tags=['Chat'])
async def fetch_all_session(user_id:int,service:ChatService=Depends(get_service)):
    return service.get_all_session(user_id)

@router.get("/session-list/{session_id}",tags=['Chat'])
async def fetch_session_by_id(session_id:int,service:ChatService=Depends(get_service)):
    return service.get_session_by_id(session_id)


def generate_stream(content: str, session_id: int, repo: ChatRepository, history: list):
    full_response = ""
    
    stream = client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL"),
        max_tokens=500,              # ✅ fixed typo
        stream=True,
        messages=history
    )

    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            full_response += token
            yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"

    # save directly via repo
    repo.create_message(
        session_id=session_id,
        role="assistant",
        content=full_response
    )

@router.post("/", tags=["Chat"])
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_service),
    db: Session = Depends(get_db)
):
    repo = ChatRepository(db)

    service.create_message(
        session_id=request.session_id,
        role="user",
        content=request.content
    )

    messages = service.get_session_by_id(request.session_id)

    # ✅ Add system prompt to control behavior
    history = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Answer only the user's most recent question directly. "
                "Do not repeat, summarize, or recap previous answers in the conversation "
                "unless explicitly asked to."
            )
        }
    ] + [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    return StreamingResponse(
        generate_stream(
            content=request.content,
            session_id=request.session_id,
            repo=repo,
            history=history
        ),
        media_type="text/event-stream"
    )