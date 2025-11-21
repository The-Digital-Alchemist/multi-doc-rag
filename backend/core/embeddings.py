"""
Embeddings module for generating vector embeddings using OpenAI's embedding models.

This module provides functionality to convert text chunks into vector embeddings
that can be used for semantic search and similarity matching in the RAG system.
"""

from openai import OpenAI
import numpy as np
import os


def get_client(api_key: str | None = None) -> OpenAI:
    """
    Initialize and return an OpenAI client using the provided API key or environment variables.
    
    Args:
        api_key (str | None): Optional API key. If not provided, uses OPENAI_API_KEY environment variable.
    
    Returns:
        OpenAI: Configured OpenAI client instance
        
    Raises:
        ValueError: If no API key is provided and OPENAI_API_KEY environment variable is not set
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("API key is required. Provide it as a parameter or set OPENAI_API_KEY environment variable")
    return OpenAI(api_key=key)


def embed_chunks(chunks: list[str], model: str = "text-embedding-3-large", api_key: str | None = None) -> list[np.ndarray]:
    """
    Generate vector embeddings for a list of text chunks using OpenAI's embedding model.
    
    This function takes text chunks and converts them into high-dimensional vector
    representations that capture semantic meaning, enabling similarity-based search
    and retrieval in the RAG system.
    
    Args:
        chunks (list[str]): List of text chunks to embed
        model (str, optional): OpenAI embedding model to use. Defaults to "text-embedding-3-large".
        api_key (str | None): Optional API key. If not provided, uses environment variable.
        
    Returns:
        list[np.ndarray]: List of numpy arrays representing the embeddings for each chunk
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If OpenAI API call fails
    """
    client = get_client(api_key)
    response = client.embeddings.create(
        model=model,
        input=chunks
    )

    # Convert OpenAI embedding objects to numpy arrays for easier manipulation
    embeddings = [np.array(item.embedding) for item in response.data]
    return embeddings