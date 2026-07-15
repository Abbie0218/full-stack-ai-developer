from dotenv import load_dotenv
from database import localSession
from repository.upload_repository import UploadRepository
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import Status
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
import os

load_dotenv()

def process_pdf(temp_path:str, job_id:int, user_id:int, filename:str):
    db=localSession()
    repo=UploadRepository(db)

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        for doc in docs:
            doc.metadata["user_id"] =  str(user_id)
            doc.metadata["filename"] =  filename

        # chunks

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(docs)

         # embed + store
        embeddings = CohereEmbeddings(
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            model="embed-english-v3.0"
        )
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db",
            collection_name=f"user_{user_id}"  # ✅ per-user isolation
        )

        repo.update_status(job_id, Status.DONE)
        

    except Exception as e:
        repo.update_status(job_id, Status.FAILED, error=str(e))
    finally:
        db.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)