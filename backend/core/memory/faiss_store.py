"""
FAISS vector store module for efficient similarity search.

This module provides functionality to build and search FAISS (Facebook AI Similarity Search)
vector indices for fast similarity search operations in the RAG system.
"""

import faiss
import numpy as np


def build_faiss_index(embeddings: np.ndarray, chunk_ids: np.ndarray) -> faiss.IndexIDMap:
    """
    Build a FAISS vector index from embeddings with associated chunk IDs.
    
    This function creates a FAISS IndexIDMap that allows for efficient similarity search
    while maintaining the ability to map results back to original chunk IDs. The index
    uses inner product (cosine similarity) for similarity measurement.
    
    Args:
        embeddings (np.ndarray): 2D array of embeddings where each row is a vector
        chunk_ids (np.ndarray): Array of chunk IDs corresponding to each embedding
        
    Returns:
        faiss.IndexIDMap: FAISS index ready for similarity search
        
    Note:
        The embeddings are L2-normalized before indexing to enable cosine similarity
        search using inner product.
    """    
    dimension = embeddings.shape[1]
    
    # Create an IndexIDMap with inner product similarity (cosine similarity after L2 normalization)
    index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add embeddings to index with their corresponding IDs
    index.add_with_ids(embeddings, np.array(chunk_ids, dtype=np.int64)) # type: ignore

    return index


def search_index(index: faiss.IndexFlatIP, query_vector: np.ndarray, k: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """
    Search a FAISS index for the top-k most similar vectors to a query embedding.
    
    This function performs similarity search on a FAISS index and returns the
    most similar vectors along with their similarity scores and IDs.
    
    Args:
        index (faiss.IndexFlatIP): FAISS index to search
        query_vector (np.ndarray): Query vector to search for
        k (int, optional): Number of top results to return. Defaults to 3.
        
    Returns:
        tuple[np.ndarray, np.ndarray]: Tuple containing (distances, ids) where:
            - distances: Array of similarity scores (higher is more similar)
            - ids: Array of chunk IDs corresponding to the results
            
    Note:
        The query vector is L2-normalized before search to ensure cosine similarity
        calculation is correct.
    """
    # Ensure query vector is in the correct format
    q = np.asarray(query_vector, dtype=np.float32)

    # Reshape to 2D if needed (FAISS expects 2D arrays)
    if q.ndim == 1:
        q = q[None, :]
    
    # Normalize query vector for cosine similarity
    faiss.normalize_L2(q)
    
    # Perform the search
    distances, ids = index.search(q, k) # type: ignore
    return distances, ids