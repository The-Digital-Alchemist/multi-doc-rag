"""
Lexical Store module for BM25-based text search.

This module provides functionality to build and search BM25 lexical indices
for exact term matching, complementing the semantic search capabilities
in the RAG system.
"""

import sqlite3
import os
from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi
from utils.preprocessor import preprocess_text, batch_preprocess_texts


class LexicalStore:
    """
    Manages BM25 lexical index for exact term matching and search.
    
    This class provides a unified interface for storing document chunks with their
    tokenized representations and performing lexical search operations using BM25.
    It coordinates with SQLite for metadata storage and maintains an in-memory
    BM25 index for fast lexical search.
    """
    
    def __init__(self, sqlite_path: str):   
        """
        Initialize the LexicalStore with path to SQLite database.
        
        Args:
            sqlite_path (str): Path to the SQLite database file
        """
        self.sqlite_path = sqlite_path
        self.bm25_index: Optional[BM25Okapi] = None
        self.corpus: List[List[str]] = []
        self.chunk_ids: List[int] = []
        
        # Initialize database connection
        self.conn = sqlite3.connect(sqlite_path)
        self.conn.row_factory = sqlite3.Row
        
        # Rebuild BM25 index from existing data
        self._rebuild_from_database()
    

    def add_document(self, chunks: List[str], chunk_ids: List[int], session_id: str) -> None:
        """
        Add document chunks to the BM25 lexical index with session_id.
        
        This method tokenizes the provided chunks and adds them to the BM25
        index for lexical search operations, associating them with a session_id.
        
        Args:
            chunks (List[str]): List of text chunks to add
            chunk_ids (List[int]): List of chunk IDs corresponding to each chunk
            session_id (str): Session ID to associate with these chunks
        """
        # Tokenize all chunks using the preprocessor
        tokenized_chunks = batch_preprocess_texts(chunks)
        
        # Add to corpus and chunk_ids
        self.corpus.extend(tokenized_chunks)
        self.chunk_ids.extend(chunk_ids)
        
        # Rebuild BM25 index with updated corpus
        self._build_bm25_index()

        
    def search_with_session_id(self, query: str, session_id: str, k: int = 3) -> List[Dict]:
        """
        Search for the most relevant chunks using BM25 within a specific session.
        
        This method performs lexical search using BM25 and retrieves the
        corresponding metadata from SQLite, filtered by session_id.
        
        Args:
            query (str): Query string to search for
            session_id (str): Session ID to filter results by
            k (int, optional): Number of top results to return. Defaults to 3.
            
        Returns:
            List[Dict]: List of dictionaries containing:
                - id: Chunk ID from the database
                - score: BM25 relevance score
                - doc_id: Document ID this chunk belongs to
                - content: The actual text content of the chunk
                - source_filename: Original filename of the source document
                - session_id: Session ID this chunk belongs to
        """
        if not self.bm25_index:
            return []

        # Preprocess the query
        query_tokens = preprocess_text(query)
        
        # Get BM25 scores for all documents
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k * 2]  # Get 2x more for filtering
        
        # Filter out results with zero scores
        results = []
        cursor = self.conn.cursor()
        
        for idx in top_indices:
            if scores[idx] > 0:
                chunk_id = self.chunk_ids[idx]
                score = scores[idx]
                
                # Get metadata from database with session_id filter
                row = cursor.execute(
                    "SELECT id, doc_id, content, source_filename, session_id FROM chunks WHERE id = ? AND session_id = ?",
                    (chunk_id, session_id)
                ).fetchone()
                
                if row:
                    results.append({
                        "id": row["id"],
                        "score": float(score),
                        "doc_id": row["doc_id"],
                        "content": row["content"],
                        "source_filename": row["source_filename"],
                        "session_id": row["session_id"],
                    })
        
        # Sort by score and return top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
    

    def _build_bm25_index(self) -> None:
        """
        Build or rebuild the BM25 index from the current corpus.
        
        This internal method creates a new BM25Okapi index from the tokenized
        corpus and chunk IDs.
        """
        if self.corpus:
            self.bm25_index = BM25Okapi(self.corpus)
    

    def _rebuild_from_database(self) -> None:
        """
        Rebuild the BM25 index from existing chunks in the database.
        
        This method reads all existing chunks from the SQLite database,
        tokenizes them, and rebuilds the BM25 index for search operations.
        """
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT id, content FROM chunks ORDER BY id"
        ).fetchall()
        
        if rows:
            # Extract chunk IDs and contents
            chunk_ids = [row["id"] for row in rows]
            contents = [row["content"] for row in rows]
            
            # Tokenize all chunks
            tokenized_chunks = batch_preprocess_texts(contents)
            
            # Update corpus and chunk_ids
            self.corpus = tokenized_chunks
            self.chunk_ids = chunk_ids
            
            # Build BM25 index
            self._build_bm25_index()