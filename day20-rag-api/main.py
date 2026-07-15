from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, upload, ask

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(ask.router)
@app.get("/")
def root():
    return {"message": "RAG API running"}