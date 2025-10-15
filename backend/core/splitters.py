"""
Text splitting module for chunking documents into manageable pieces.

This module provides functionality to split large documents into smaller chunks
with configurable token limits and overlap, ensuring optimal processing for
embedding generation and retrieval in the RAG system.
"""

import tiktoken
from typing import List


def recursive_token_split(text: str, chunk_tokens: int = 400, overlap: int = 100, model: str = "gpt-4o-mini") -> List[str]:
    """
    Split text into overlapping chunks based on token count using tiktoken encoding.
    
    This function takes a large text document and splits it into smaller, overlapping
    chunks that are suitable for embedding generation. The overlap ensures that
    important information at chunk boundaries is not lost.
    
    Args:
        text (str): The input text to be split into chunks
        chunk_tokens (int, optional): Maximum number of tokens per chunk. Defaults to 400.
        overlap (int, optional): Number of tokens to overlap between consecutive chunks. Defaults to 100.
        model (str, optional): OpenAI model name for tokenization. Defaults to "gpt-4o-mini".
        
    Returns:
        List[str]: List of text chunks with overlap, filtered to remove empty chunks
        
    Example:
        >>> text = "This is a long document that needs to be split..."
        >>> chunks = recursive_token_split(text, chunk_tokens=100, overlap=20)
        >>> print(len(chunks))  # Number of chunks created
    """
    # Initialize the tokenizer for the specified model
    enc = tiktoken.encoding_for_model(model)
    
    # Convert text to tokens for accurate counting
    tokens = enc.encode(text)
    chunks = []

    # Slide a window across the tokens with overlap
    i = 0
    while i < len(tokens):
        # Extract a window of tokens
        window = tokens[i : i + chunk_tokens]
        
        # Convert tokens back to text
        text_chunk = enc.decode(window)
        chunks.append(text_chunk)
        
        # Move the window forward, accounting for overlap
        i += chunk_tokens - overlap
    
    # Filter out empty chunks and strip whitespace
    return [c.strip() for c in chunks if c.strip()]