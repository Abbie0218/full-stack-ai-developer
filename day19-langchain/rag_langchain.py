from langchain_cohere import CohereEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

load_dotenv()

embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"), model="embed-english-v3.0"
)

# llm

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("DEFAULT_MODEL"),
    temperature=0,
)


# ── Document ──────────────────────────────────────────────────
document_text = """
FastAPI Performance and Features
FastAPI is one of the fastest Python web frameworks available.
FastAPI can handle up to 50,000 requests per second on modern hardware.
It supports both synchronous and asynchronous request handling.

Authentication in FastAPI
JWT tokens are commonly used with FastAPI for stateless authentication.
Token expiry should be set to 15 minutes for access tokens.
Refresh tokens should expire after 7 days.

Database Integration
FastAPI works seamlessly with SQLAlchemy ORM.
PostgreSQL is the recommended database for production FastAPI applications.

Deployment
FastAPI applications are typically deployed using Docker containers.
Use Railway or Render for simple cloud deployments.
"""

docs = [Document(page_content=document_text, metadata={"source": "fastapi_docs.txt"})]

splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
chunks = splitter.split_documents(docs)

vectorStore = Chroma.from_documents(
    documents=chunks, embedding=embeddings, persist_directory="./chroma_langchain"
)

retriever = vectorStore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

prompt = PromptTemplate(
    template="""Answer using ONLY the context below.
If answer not in context, say "I don't know based on provided context."
Always cite source.

Context: {context}
Question: {question}
Answer:""",
    input_variables=["context", "question"]
)

# ── Format retrieved docs ─────────────────────────────────────
def format_docs(docs):
    return "\n\n".join([
        f"[Source: {d.metadata['source']}]\n{d.page_content}"
        for d in docs
    ])

# ── LCEL chain ────────────────────────────────────────────────
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ── Test ──────────────────────────────────────────────────────
questions = [
    "How many requests per second can FastAPI handle?",
    "How long should access tokens expire?",
    "What is the capital of France?",
]

print("\n" + "="*50)
for q in questions:
    answer = chain.invoke(q)
    print(f"\nQ: {q}")
    print(f"A: {answer}")
    print("-"*50)