from openai import OpenAI
import numpy as np
import os

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)

def embed_chunks(chunks: list[str], model="text-embedding-3-large") -> list[np.ndarray]:
    client = get_client()
    response = client.embeddings.create(
        model=model,
        input=chunks
    )

    embeddings = [np.array(item.embedding) for item in response.data]
    return embeddings