from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

co_embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model="embed-english-v3.0"
)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_answer(question: str, user_id: int, history: list) -> dict:
    # ── Step 1: Search user's ChromaDB collection ─────────────
    vectorstore = Chroma(
        collection_name=f"user_{user_id}",   # ✅ user isolated
        embedding_function=co_embeddings,
        persist_directory="./chroma_db"
    )

    results = vectorstore.similarity_search(question, k=3)

    if not results:
        return {
            "answer": "No documents found. Please upload a PDF first.",
            "sources": []
        }

    # ── Step 2: Build context ─────────────────────────────────
    context = ""
    sources = []
    for doc in results:
        context += f"[Source: {doc.metadata.get('filename', 'unknown')}, page {doc.metadata.get('page', '?')}]\n"
        context += f"{doc.page_content}\n\n"
        sources.append(doc.metadata.get('filename', 'unknown'))

    # ── Step 3: Build messages with history ───────────────────
    messages = []

    # system prompt
    messages.append({
        "role": "system",
        "content": f"""Answer using ONLY the context below.
If answer not in context, say "I don't know based on the provided documents."
Always cite source.

Context:
{context}"""
    })

    # add conversation history
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})

    # add current question
    messages.append({"role": "user", "content": question})

    # ── Step 4: Get answer from Groq ──────────────────────────
    response = groq_client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant"),
        messages=messages,
        temperature=0,
        max_tokens=500
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": list(set(sources))
    }