from fastapi import APIRouter
from pydantic import BaseModel
from agent import run_agent

router = APIRouter(prefix="/agent", tags=['Agent'])

class ChatRequest(BaseModel):
    message:str
    thread_id:str="default"

class ChatResponse(BaseModel):
    answer:str
    thread_id:str
    tool_used:list[str]=[]

@router.post("/chat", response_model=ChatResponse)
def chat(request:ChatRequest):
    result = run_agent(request.message, request.thread_id)
    return ChatResponse(
        answer=result['answer'],
        thread_id=request.thread_id,
        tool_used=result['tools_used']
    )
