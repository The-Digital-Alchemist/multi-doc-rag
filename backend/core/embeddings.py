from openai import OpenAI
import numpy as np

client = OpenAI()

def embed_chunks(chunks: list[str], model="text-embedding-3-large") -> list[np.ndarray]:
    response = client.embeddings.create(
        model=model,
        input=chunks
    )

    embeddings = [np.array(item.embedding) for item in response.data]
    return embeddings