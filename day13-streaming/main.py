from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@app.get("/")
def greet():
    return{
        "message":"Streaming FAST API"
    }

def generate_stream(question:str):
    stream = client.chat.completions.create(
        model=os.getenv('DEFAULT_MODEL'),
        stream=True,
        messages=[{"role":"user","content":question}],
        max_tokens=500
    )

    for chunks in stream:
        token = chunks.choices[0].delta.content
        if token:
            yield f"data:{token}\n\n"
    yield f"data: [DONE]\n\n"

@app.get("/stream")
async def stream_response(question:str):
    return StreamingResponse(
        generate_stream(question),
        media_type="text/event-stream"
    )

