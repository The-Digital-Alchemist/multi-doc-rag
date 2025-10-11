from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from core.memory.memory_manager import MemoryManager
from core.splitters import recursive_token_split
from core.embeddings import embed_chunks
from utils.io import read_text_from_path, save_upload
from core.LLM.llm_engine import generate_answer
import numpy as np
import os


app = FastAPI(
    title="Multi Doc RAG",
    description="A multi-document retrieval augmented generation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FAISS_PATH = "data/index/index.faiss"
SQLITE_PATH = "data/index/chunks.db"
UPLOAD_DIR = "data/uploads"


os.makedirs(UPLOAD_DIR, exist_ok=True)
memory = MemoryManager(FAISS_PATH, SQLITE_PATH)

if os.path.exists(FAISS_PATH):
    memory.load_index()
    print("FAISS index loaded")
else: 
    print("No index found, starting fresh")


@app.post("/ping")
async def ping():
    return{ "Status": "OK"}


@app.post("/upload")
async def upload_file(file: UploadFile):

    path  = save_upload(file, UPLOAD_DIR)

    text = read_text_from_path(path)

    chunks = recursive_token_split(text)

    embeddings = np.array(embed_chunks(chunks))


    memory.add_document(chunks, embeddings, doc_id=file.filename, source_filename=file.filename) # type: ignore

    memory.save_index()
    return {"status": "OK", "chunks_added": len(chunks)}




@app.post("/query")
async def query_rag(query: str = Form(...), k: int = 3):
    q_emb = np.array(embed_chunks([query]))
    results = memory.search(q_emb, k=k)

    contexts = [r["content"] for r in results]

    answer = generate_answer(query, contexts)
    return {"answer": answer, "results": results}



