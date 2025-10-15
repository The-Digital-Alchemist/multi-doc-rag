"""
Embeddings module for generating vector embeddings using OpenAI's embedding models.

This module provides functionality to convert text chunks into vector embeddings
that can be used for semantic search and similarity matching in the RAG system.
"""

from openai import OpenAI
import numpy as np
import os


def get_client() -> OpenAI:
    """
    Initialize and return an OpenAI client using the API key from environment variables.
    
    Returns:
        OpenAI: Configured OpenAI client instance
        
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)


def embed_chunks(chunks: list[str], model: str = "text-embedding-3-large") -> list[np.ndarray]:
    """
    Generate vector embeddings for a list of text chunks using OpenAI's embedding model.
    
    This function takes text chunks and converts them into high-dimensional vector
    representations that capture semantic meaning, enabling similarity-based search
    and retrieval in the RAG system.
    
    Args:
        chunks (list[str]): List of text chunks to embed
        model (str, optional): OpenAI embedding model to use. Defaults to "text-embedding-3-large".
        
    Returns:
        list[np.ndarray]: List of numpy arrays representing the embeddings for each chunk
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If OpenAI API call fails
    """
    client = get_client()
    response = client.embeddings.create(
        model=model,
        input=chunks
    )

    # Convert OpenAI embedding objects to numpy arrays for easier manipulation
    embeddings = [np.array(item.embedding) for item in response.data]
    return embeddings