import numpy as np
import cohere
import os
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# your "database" of documents
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

# embed all documents (batch)
doc_response = co.embed(
    texts=documents,
    model="embed-english-v3.0",
    input_type="search_document"
)
doc_vectors = doc_response.embeddings

def search(query: str, top_k: int = 3):
    # embed the query
    query_response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"   # ✅ different input_type for queries
    )
    query_vector = query_response.embeddings[0]

    # calculate similarity with all documents
    scores = []
    for i, doc_vector in enumerate(doc_vectors):
        score = cosine_similarity(query_vector, doc_vector)
        scores.append((score, documents[i]))

    # sort by highest score
    scores.sort(reverse=True)

    print(f"\nQuery: '{query}'")
    print("Top results:")
    for score, doc in scores[:top_k]:
        print(f"  {score:.4f} → {doc}")

# test searches
search("how do I build an API?")
search("database storage options")
search("user login and security")