import chromadb
import cohere
import os
import json
import re
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# ── Clients ──────────────────────────────────────────────────
co = cohere.Client(os.getenv("COHERE_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./rag_db")

collection = chroma_client.get_or_create_collection(
    name="rag_docs",
    metadata={"hnsw:space": "cosine"}
)

# ── Sample document ───────────────────────────────────────────
document = """
FastAPI Performance and Features
FastAPI is one of the fastest Python web frameworks available.
It is built on Starlette for the web parts and Pydantic for the data parts.
FastAPI can handle up to 50,000 requests per second on modern hardware.
It supports both synchronous and asynchronous request handling.

Authentication in FastAPI
FastAPI has built-in support for OAuth2 with Password flow.
JWT tokens are commonly used with FastAPI for stateless authentication.
You can use the Depends() function to protect routes with authentication.
Token expiry should be set to 15 minutes for access tokens.
Refresh tokens should expire after 7 days.

Database Integration
FastAPI works seamlessly with SQLAlchemy ORM.
You should use async SQLAlchemy for better performance in async routes.
Alembic is used for database migrations with SQLAlchemy.
Always use connection pooling in production to manage database connections.
PostgreSQL is the recommended database for production FastAPI applications.

Deployment
FastAPI applications are typically deployed using Docker containers.
You should use Gunicorn with Uvicorn workers for production deployment.
The recommended number of workers is (2 * CPU cores) + 1.
Always use environment variables for sensitive configuration.
Use Railway or Render for simple cloud deployments.
"""

# ── Chunk ─────────────────────────────────────────────────────
def chunk_document(text: str, source: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return [
        {
            "text": chunk,
            "id": f"{source}_chunk_{i}",
            "metadata": {
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        }
        for i, chunk in enumerate(chunks)
    ]

# ── Embed and store ───────────────────────────────────────────
def index_document(chunks: list[dict]):
    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    response = co.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )

    collection.upsert(
        ids=ids,
        embeddings=response.embeddings,
        documents=texts,
        metadatas=metadatas
    )
    print(f"✅ Indexed {len(chunks)} chunks")

# ── Retrieve ──────────────────────────────────────────────────
def retrieve(query: str, n_results: int = 3) -> list[dict]:
    query_response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )

    results = collection.query(
        query_embeddings=query_response.embeddings,
        n_results=n_results
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i]
        })
    return chunks

# ── Generate answer ───────────────────────────────────────────
def generate_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I don't have enough context to answer this question."

    context = ""
    for chunk in chunks:
        context += f"[Source: {chunk['source']}, chunk {chunk['chunk_index']}]\n"
        context += f"{chunk['text']}\n\n"

    prompt = f"""Answer using ONLY the context below.
If the answer is not in the context, say "I don't know based on the provided context."
Always cite your source as [Source: filename, chunk N].

Context:
{context}

Question: {query}

Answer:"""

    response = groq_client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300
    )

    return response.choices[0].message.content

# ── Query expansion ───────────────────────────────────────────
def expand_query(query: str) -> list[str]:
    prompt = f"""Generate 3 different ways to ask this question.
Return ONLY a JSON array of 3 strings. No explanation.
Original: "{query}"
Output:"""

    response = groq_client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    text = response.choices[0].message.content
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        variants = json.loads(match.group())
        return [query] + variants
    return [query]

def retrieve_with_expansion(query: str, n_results: int = 3) -> list[dict]:
    queries = expand_query(query)
    print(f"Query variants: {queries}")

    all_chunks = {}
    for q in queries:
        chunks = retrieve(q, n_results=2)
        for chunk in chunks:
            key = f"{chunk['source']}_chunk_{chunk['chunk_index']}"
            if key not in all_chunks:
                all_chunks[key] = chunk

    return list(all_chunks.values())[:3]

# ── Full RAG ──────────────────────────────────────────────────
def rag(query: str) -> str:
    chunks = retrieve(query)
    return generate_answer(query, chunks)

print("DEBUG: starting query expansion test")  # ← add this
print("\n=== Query Expansion Test ===")
query = "what is the token expiry time?"
chunks = retrieve_with_expansion(query)
answer = generate_answer(query, chunks)
print(f"\nQ: {query}")
print(f"A: {answer}")

# ── Run ───────────────────────────────────────────────────────
chunks = chunk_document(document, source="fastapi_docs.txt")
index_document(chunks)
print(f"Total chunks in DB: {collection.count()}")

# basic RAG test
questions = [
    "How many requests per second can FastAPI handle?",
    "How long should access tokens expire?",
    "What database is recommended for production?",
    "What is the capital of France?",
]

print("\n" + "="*60)
for question in questions:
    print(f"\nQ: {question}")
    answer = rag(question)
    print(f"A: {answer}")
    print("-"*60)


