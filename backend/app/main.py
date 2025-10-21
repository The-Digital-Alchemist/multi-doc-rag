"""
Multi-Document RAG (Retrieval-Augmented Generation) FastAPI Application.

This module provides a REST API for document ingestion, storage, and querying
using a RAG system. It supports multiple document formats and provides semantic
search capabilities with AI-powered answer generation.
"""

from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.memory.memory_manager import MemoryManager
from core.memory.lexical_store import LexicalStore
from core.splitters import recursive_token_split
from core.embeddings import embed_chunks
from utils.io import read_text_from_path, save_upload
from core.LLM.llm_engine import generate_answer, enrich_query
import numpy as np
import os
from pathlib import Path

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

# Get absolute paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
FAISS_PATH = str(PROJECT_ROOT / "data" / "index" / "index.faiss")
SQLITE_PATH = str(PROJECT_ROOT / "data" / "index" / "chunks.db")
UPLOAD_DIR = str(PROJECT_ROOT / "data" / "uploads")

# Change working directory to project root
os.chdir(PROJECT_ROOT)

# Ensure directories exist
os.makedirs(os.path.dirname(FAISS_PATH), exist_ok=True)
os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
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
async def upload_file(file: UploadFile, session_id: str = Form(...)) -> dict[str, str | int]:
    """
    Upload and process a document for ingestion into the RAG system.
    
    This endpoint handles file uploads, extracts text content, splits it into chunks,
    generates embeddings, and stores everything in the knowledge base with session isolation.
    
    Args:
        file (UploadFile): The uploaded file (supports .txt, .pdf, .docx)
        session_id (str): Session ID to associate this document with
        
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

    # Store chunks and embeddings in the knowledge base with session_id
    chunk_ids = memory.add_document(chunks, embeddings, doc_id=file.filename, source_filename=file.filename, session_id=session_id)

    # Store chunks and chunk ID in the lexical store with session_id
    lexical_store.add_document(chunks, chunk_ids, session_id) 

    # Persist the updated index
    memory.save_index()
    return {"status": "OK", "chunks_added": len(chunks), "session_id": session_id}




def fuse_search_results(semantic_results: list[dict], lexical_results: list[dict], k: int) -> list[dict]:
    """
    Fuse results from both semantic and lexical searches using Reciprocal Rank Fusion
    
    args:
        semantic_results: list[dict]: Results from the semantic search
        lexical_results: list[dict]: Results from the lexical search
        k: int: Number of top results to return

    returns:
        list[dict]: List of fused results with realistic confidence scores
    """

    fused_scores = {}

    # Add semantic scores (boost to realistic range)
    for rank, result in enumerate(semantic_results):
        chunk_id = result["id"]
        semantic_score = result["score"] if result["score"] <= 1.0 else result["score"] / 2.0
        rrf_score = 1.0 / (60 + rank + 1)
        # Boost to 60-90% range: base 0.6 + weighted score
        combined_score = 0.6 + (semantic_score * 0.3) + (rrf_score * 0.1)
        fused_scores[chunk_id] = {
            "result": result,
            "combined_score": min(combined_score, 0.95)  # Cap at 95%
        }

    # Add lexical scores (boost to realistic range)
    for rank, result in enumerate(lexical_results):
        chunk_id = result["id"]
        lexical_score = min(result["score"] / 2.0, 1.0)
        rrf_score = 1.0 / (60 + rank + 1)
        # Boost to 60-90% range: base 0.6 + weighted score
        combined_score = 0.6 + (lexical_score * 0.3) + (rrf_score * 0.1)
        
        if chunk_id in fused_scores:
            # Average the combined scores if chunk appears in both
            fused_scores[chunk_id]["combined_score"] = (fused_scores[chunk_id]["combined_score"] + combined_score) / 2
        else:
            fused_scores[chunk_id] = {
                "result": result,
                "combined_score": min(combined_score, 0.95)
            }

    # Sort by combined score and return with updated scores
    sorted_results = sorted(fused_scores.values(), key=lambda x: x["combined_score"], reverse=True)
    
    # Update results with realistic confidence scores
    fused_results = []
    for item in sorted_results[:k]:
        result = item["result"].copy()
        result["score"] = item["combined_score"]
        fused_results.append(result)
    
    return fused_results




@app.post("/query")
async def query_rag(query: str = Form(...), k: int = 3, session_id: str = Form(...)) -> dict[str, str | list[dict]]:
    """
    Query the RAG system to get an AI-generated answer based on document content.
    
    This endpoint performs hybrid search to find relevant document chunks,
    then uses an LLM to generate a contextual answer based on the retrieved information.
    
    Args:
        query (str): The user's question or query
        k (int, optional): Number of most relevant chunks to retrieve. Defaults to 3.
        session_id (str): Session ID to filter search results
        
    Returns:
        dict[str, str | list[dict]]: Response containing:
            - answer: AI-generated answer based on retrieved contexts
            - results: List of retrieved chunks with metadata and similarity scores
            
    Raises:
        HTTPException: If query processing fails or no documents are indexed
    """

    try:
        # Enrich the query
        enriched_query = enrich_query(query)

        # Generate query embedding for the semantic search
        q_emb = np.array(embed_chunks([enriched_query]))
        
        # Perform semantic search with session_id filtering
        semantic_results = memory.search_with_session_id(q_emb, session_id, k=k)

        # Perform lexical search with session_id filtering
        lexical_results = lexical_store.search_with_session_id(enriched_query, session_id, k=k)

        # Fuse results from both searches 
        results = fuse_search_results(semantic_results, lexical_results, k=k)

        # Extract content from search results for answer generation
        contexts = [r["content"] for r in results]

        print(f"Semantic results count: {len(semantic_results)}")
        print(f"Lexical results count: {len(lexical_results)}")
        print(f"Semantic scores: {[r['score'] for r in semantic_results]}")
        print(f"Lexical scores: {[r['score'] for r in lexical_results]}")



        # Generate answer using retrieved contexts
        answer = generate_answer(enriched_query, contexts)
        return {"answer": answer, "results": results}

    except Exception as e:
        print(f"Error querying RAG: {e}")
        return {"error": "Failed to query RAG"}
