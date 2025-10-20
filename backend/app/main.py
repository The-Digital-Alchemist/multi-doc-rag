"""
Multi-Document RAG (Retrieval-Augmented Generation) FastAPI Application.

This module provides a REST API for document ingestion, storage, and querying
using a RAG system. It supports multiple document formats and provides semantic
search capabilities with AI-powered answer generation.
"""

from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from core.memory.memory_manager import MemoryManager
from core.memory.lexical_store import LexicalStore
from core.splitters import recursive_token_split
from core.embeddings import embed_chunks
from utils.io import read_text_from_path, save_upload
from core.LLM.llm_engine import generate_answer
import numpy as np
import os

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Cortex API",
    description="AI Document Assistant - A multi-document retrieval augmented generation system",
    version="1.0.0"
)

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Specify the prod IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration constants
FAISS_PATH = "data/index/index.faiss"  # Path to FAISS vector index file
SQLITE_PATH = "data/index/chunks.db"   # Path to SQLite metadata database
UPLOAD_DIR = "data/uploads"            # Directory for uploaded files

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize memory manager for document storage and retrieval
memory = MemoryManager(FAISS_PATH, SQLITE_PATH)

# Initialize lexical store
lexical_store = LexicalStore(SQLITE_PATH)

# Load existing index if available
if os.path.exists(FAISS_PATH):
    memory.load_index()
    print("FAISS index loaded")
else: 
    print("No index found, starting fresh")


@app.post("/ping")
async def ping() -> dict[str, str]:
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict[str, str]: Status message indicating the API is operational
    """
    return {"Status": "OK"}


@app.post("/upload")
async def upload_file(file: UploadFile) -> dict[str, str | int]:
    """
    Upload and process a document for ingestion into the RAG system.
    
    This endpoint handles file uploads, extracts text content, splits it into chunks,
    generates embeddings, and stores everything in the knowledge base.
    
    Args:
        file (UploadFile): The uploaded file (supports .txt, .pdf, .docx)
        
    Returns:
        dict[str, str | int]: Response containing status and number of chunks added
        
    Raises:
        HTTPException: If file processing fails or unsupported file type
    """
    # Save uploaded file to disk
    path = save_upload(file, UPLOAD_DIR)

    # Extract text content from the file
    text = read_text_from_path(path)

    # Split text into manageable chunks with overlap
    chunks = recursive_token_split(text)

    # Generate embeddings for each chunk
    embeddings = np.array(embed_chunks(chunks))

    # Store chunks and embeddings in the knowledge base
    chunk_ids = memory.add_document(chunks, embeddings, doc_id=file.filename, source_filename=file.filename)

    # Store chunks and chunk ID in the lexical store
    lexical_store.add_document(chunks, chunk_ids) 

    # Persist the updated index
    memory.save_index()
    return {"status": "OK", "chunks_added": len(chunks)}


@app.post("/query")
async def query_rag(query: str = Form(...), k: int = 3) -> dict[str, str | list[dict]]:
    """
    Query the RAG system to get an AI-generated answer based on document content.
    
    This endpoint performs semantic search to find relevant document chunks,
    then uses an LLM to generate a contextual answer based on the retrieved information.
    
    Args:
        query (str): The user's question or query
        k (int, optional): Number of most relevant chunks to retrieve. Defaults to 3.
        
    Returns:
        dict[str, str | list[dict]]: Response containing:
            - answer: AI-generated answer based on retrieved contexts
            - results: List of retrieved chunks with metadata and similarity scores
            
    Raises:
        HTTPException: If query processing fails or no documents are indexed
    """
    # Generate embedding for the query
    q_emb = np.array(embed_chunks([query]))
    
    # Search for most similar chunks
    results = memory.search(q_emb, k=k)

    # Extract content from search results for answer generation
    contexts = [r["content"] for r in results]

    # Generate answer using retrieved contexts
    answer = generate_answer(query, contexts)
    return {"answer": answer, "results": results}



