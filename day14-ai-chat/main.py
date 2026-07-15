from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chat
from database import engine

app = FastAPI(title="AI Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "AI Chat API running"}
    
app.include_router(auth.router)
app.include_router(chat.router)   # ✅ add