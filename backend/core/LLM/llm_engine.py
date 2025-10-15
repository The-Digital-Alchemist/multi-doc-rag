"""
LLM Engine module for generating answers using OpenAI's language models.

This module provides functionality to generate contextual answers by combining
user queries with retrieved document contexts using OpenAI's GPT models.
"""

from openai import OpenAI
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


def generate_answer(query: str, contexts: list[str]) -> str:
    """
    Generate an answer to a user query using retrieved document contexts.
    
    This function implements the generation part of the RAG (Retrieval-Augmented Generation)
    pipeline. It takes a user query and relevant document contexts, then uses an LLM
    to generate a coherent answer based on the provided information.
    
    Args:
        query (str): The user's question or query
        contexts (list[str]): List of relevant document chunks retrieved from the knowledge base
        
    Returns:
        str: Generated answer based on the query and contexts
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If OpenAI API call fails
    """
    client = get_client()
    
    # Construct a prompt that instructs the model to answer using only the provided contexts
    prompt = f""""You are an assistant with access to retrieved contexts from various documents.
    Using the information you find in the documents, answer the user query using only the contexts below.


    Context: 
    {chr(10).join(contexts)}

    Query: {query}

    Answer: 
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2  # Low temperature for more deterministic, factual responses
    )
    return response.choices[0].message.content.strip() # type: ignore