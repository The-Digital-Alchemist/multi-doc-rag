"""
Memory Manager module for coordinating vector search and metadata storage.

This module provides a unified interface for managing both FAISS vector indices
and SQLite metadata storage, enabling efficient document storage and retrieval
in the RAG system.
"""

import faiss
import sqlite3
import os
import numpy as np
from datetime import datetime
from core.memory.sqlite_store import init_db
from core.memory.faiss_store import build_faiss_index


class MemoryManager:
    """
    Manages both FAISS vector index and SQLite metadata storage for document chunks.
    
    This class provides a unified interface for storing document chunks with their
    embeddings and metadata, as well as performing similarity search operations.
    It coordinates between FAISS for vector operations and SQLite for metadata storage.
    """
    
    def __init__(self, faiss_path: str, sqlite_path: str):
        """
        Initialize the MemoryManager with paths to FAISS index and SQLite database.
        
        Args:
            faiss_path (str): Path to the FAISS index file
            sqlite_path (str): Path to the SQLite database file
        """
        self.faiss_path = faiss_path
        self.sqlite_path = sqlite_path

        # Initialize SQLite database and connection
        init_db(sqlite_path)
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

        # Load existing FAISS index if available
        if os.path.exists(faiss_path):
            self.index = faiss.read_index(faiss_path)
        else:
            self.index = None



    def add_document(self, chunks: list[str], embeddings: np.ndarray, doc_id: str, source_filename: str) -> None:
        """
        Add a document's chunks and embeddings to both SQLite and FAISS storage.
        
        This method stores document chunks in SQLite for metadata retrieval and
        their corresponding embeddings in FAISS for similarity search. It handles
        both new index creation and adding to existing indices.
        
        Args:
            chunks (list[str]): List of text chunks from the document
            embeddings (np.ndarray): 2D array of embeddings for each chunk
            doc_id (str): Unique identifier for the document
            source_filename (str): Original filename of the source document
        """
        cursor = self.conn.cursor()
        chunks_ids = []
        
        # Store each chunk in SQLite and collect the generated IDs
        for idx, chunk in enumerate(chunks):
            created_at = datetime.now().isoformat()
            cursor.execute("""
            INSERT INTO chunks (doc_id, content, chunk_index, source_filename, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (doc_id, chunk, idx, source_filename, created_at))
            chunks_ids.append(cursor.lastrowid)
            
        self.conn.commit()

        # Prepare embeddings for FAISS storage
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        # Create new FAISS index if none exists
        if self.index is None:
            d = embeddings.shape[1]
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(d))

        # Add embeddings to FAISS index with corresponding chunk IDs
        self.index.add_with_ids(embeddings, np.array(chunks_ids, dtype=np.int64)) #type: ignore

        # Persist the updated index to disk
        self.save_index()


    def search(self, query_vector: np.ndarray, k: int = 3) -> list[dict]:
        """
        Search for the most similar chunks to a query vector.
        
        This method performs similarity search using the FAISS index and retrieves
        the corresponding metadata from SQLite. It returns a list of results with
        similarity scores and chunk information.
        
        Args:
            query_vector (np.ndarray): Query vector to search for
            k (int, optional): Number of top results to return. Defaults to 3.
            
        Returns:
            list[dict]: List of dictionaries containing:
                - id: Chunk ID from the database
                - score: Similarity score (higher is more similar)
                - doc_id: Document ID this chunk belongs to
                - content: The actual text content of the chunk
                - source_filename: Original filename of the source document
                
        Raises:
            ValueError: If no index is available and cannot be loaded
        """
        # Ensure index is loaded
        if self.index is None:
            print("Index not loaded in memory. Attempting to reload..")
            self.load_index()
            if self.index is None:
                raise ValueError("Failed to load index. Ensure /upload was called first.")
        
        # Prepare query vector for search
        q = np.asarray(query_vector, dtype=np.float32)
        if q.ndim == 1:
            q = q [None, :]

        # Normalize for cosine similarity
        faiss.normalize_L2(q)

        # Perform similarity search
        distances, ids = self.index.search(q, k) # type: ignore
        
        # Filter out invalid results (-1 indicates no match)
        id_list = [int(i) for i in ids[0] if i != -1]
        score_list = [float(s) for i, s in zip(ids[0], distances[0]) if i != -1]

        if not id_list:
            return []

        # Retrieve metadata for the found chunks
        placeholders = ",".join("?" for _ in id_list)
        rows = self.conn.execute(f"""
                           SELECT id, doc_id, content, source_filename FROM chunks WHERE id IN ({placeholders})
                           """, id_list).fetchall()

        # Create a lookup dictionary for efficient metadata retrieval
        by_id = {row["id"]: row for row in rows}
        results = []

        # Combine similarity scores with metadata
        for cid, score in zip(id_list, score_list):
            row = by_id.get(cid)
            if row:
                results.append({
                    "id": cid,
                    "score": score,
                    "doc_id": row["doc_id"],
                    "content": row["content"],
                    "source_filename": row["source_filename"],
                })
        return results
                    
    def save_index(self) -> None:
        """
        Save the current FAISS index to disk.
        
        This method persists the in-memory FAISS index to the specified file path,
        allowing the index to be loaded later without rebuilding from scratch.
        """
        if self.index is not None:
            faiss.write_index(self.index, self.faiss_path)

    def load_index(self) -> None:
        """
        Load a FAISS index from disk if it exists.
        
        This method attempts to load a previously saved FAISS index from the
        specified file path. If loading fails or no index exists, it initializes
        a new empty index.
        """
        if os.path.exists(self.faiss_path):
            try:
                self.index = faiss.read_index(self.faiss_path)
                print("FAISS index successfully loaded from disk.")
            except Exception as e:
                print(f"Failed to load FAISS index: {e}. Reinitializing new index.")
                self.index = None
        else:
            print("No FAISS index found, creating new.")
            self.index = None

    