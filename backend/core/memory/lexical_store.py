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
    

    def add_document(self, chunks: List[str], chunk_ids: List[int]) -> None:
        """
        Add document chunks to the BM25 lexical index.
        
        This method tokenizes the provided chunks and adds them to the BM25
        index for lexical search operations.
        
        Args:
            chunks (List[str]): List of text chunks to add
            chunk_ids (List[int]): List of chunk IDs corresponding to each chunk
        """
        # Tokenize all chunks using the preprocessor
        tokenized_chunks = batch_preprocess_texts(chunks)
        
        # Add to corpus and chunk_ids
        self.corpus.extend(tokenized_chunks)
        self.chunk_ids.extend(chunk_ids)
        
        # Rebuild BM25 index with updated corpus
        self._build_bm25_index()
    

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Search for the most relevant chunks using BM25 lexical matching.
        
        This method performs lexical search using the BM25 algorithm and returns
        results with similarity scores and chunk information.
        
        Args:
            query (str): Query string to search for
            k (int, optional): Number of top results to return. Defaults to 3.
            
        Returns:
            List[Dict]: List of dictionaries containing:
                - id: Chunk ID from the database
                - score: BM25 similarity score (higher is more similar)
                - doc_id: Document ID this chunk belongs to
                - content: The actual text content of the chunk
                - source_filename: Original filename of the source document
                
        Raises:
            ValueError: If no index is available
        """
        if self.bm25_index is None:
            raise ValueError("No BM25 index available. Ensure documents have been added.")
        
        # Preprocess the query using the same tokenization rules
        query_tokens = preprocess_text(query)
        
        # Get BM25 scores for all documents
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        # Filter out results with zero scores
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                chunk_id = self.chunk_ids[idx]
                score = scores[idx]
                
                # Get metadata from database
                cursor = self.conn.cursor()
                row = cursor.execute(
                    "SELECT id, doc_id, content, source_filename FROM chunks WHERE id = ?",
                    (chunk_id,)
                ).fetchone()
                
                if row:
                    results.append({
                        "id": row["id"],
                        "score": score,
                        "doc_id": row["doc_id"],
                        "content": row["content"],
                        "source_filename": row["source_filename"],
                    })
        
        return results
    

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