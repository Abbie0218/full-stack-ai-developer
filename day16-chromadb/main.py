import chromadb
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="my_documents",
    metadata={"hnsw:space": "cosine"}
)

# documents to add
documents = [
    "Python is a high-level programming language known for simplicity",
    "FastAPI is a modern web framework for building APIs with Python",
    "PostgreSQL is a powerful open-source relational database",
    "Docker helps you package applications into containers",
    "JWT tokens are used for stateless authentication",
    "React is a JavaScript library for building user interfaces",
    "SQLAlchemy is a Python ORM for database interactions",
    "Redis is an in-memory data store used for caching",
]

# generate embeddings
response = co.embed(
    texts=documents,
    model="embed-english-v3.0",
    input_type="search_document"
)

# upsert into collection
collection.upsert(
    ids=[f"doc_{i}" for i in range(len(documents))],
    embeddings=response.embeddings,
    documents=documents,
    metadatas=[
        {"source": "tech_docs", "page": i+1, "topic": "backend"}
        for i in range(len(documents))
    ]
)

print(f"Count after upsert: {collection.count()}")

# ── Search function ──────────────────────────────
def search(query: str, n_results: int = 3, where_filter: dict = None):
    query_response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )

    params = {
        "query_embeddings": query_response.embeddings,
        "n_results": n_results,
    }
    if where_filter:
        params["where"] = where_filter

    results = collection.query(**params)

    print(f"\nQuery: '{query}'")
    if where_filter:
        print(f"Filter: {where_filter}")
    print("Results:")
    for i in range(len(results["ids"][0])):
        print(f"  ID:       {results['ids'][0][i]}")
        print(f"  Doc:      {results['documents'][0][i][:60]}...")
        print(f"  Meta:     {results['metadatas'][0][i]}")
        print(f"  Distance: {results['distances'][0][i]:.4f}")
        print()

# ── Test 1 — normal search ───────────────────────
search("how do I build an API?")

# ── Test 2 — metadata filter (only page >= 5) ────
search("database", where_filter={"page": {"$gte": 5}})

# ── Test 3 — upsert deduplication ────────────────
print("--- Testing upsert deduplication ---")
print(f"Count before: {collection.count()}")

update_response = co.embed(
    texts=["Python UPDATED — now with type hints"],
    model="embed-english-v3.0",
    input_type="search_document"
)

collection.upsert(
    ids=["doc_0"],                          # same ID as existing doc
    embeddings=update_response.embeddings,
    documents=["Python UPDATED — now with type hints"],
    metadatas=[{"source": "tech_docs", "page": 1, "topic": "backend"}]
)

print(f"Count after:  {collection.count()}")  # still 8 — not 9 ✅
peek = collection.peek(limit=1)
print(f"doc_0 now:    {peek['documents'][0]}")  # shows updated text ✅

# ── Test 4 — delete by metadata ──────────────────
print("\n--- Testing delete ---")
print(f"Count before delete: {collection.count()}")

collection.delete(where={"page": {"$gte": 7}})  # delete page 7 and 8

print(f"Count after delete:  {collection.count()}")  # should be 6 ✅