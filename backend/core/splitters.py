import tiktoken
from typing import List



def recursive_token_split(text: str, chunk_tokens=600, overlap=80, model="gpt-4o-mini")-> List[str]:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    chunks = []

    i = 0
    while i < len(tokens):
        window = tokens[i : i + chunk_tokens]
        text_chunk = enc.decode(window)
        chunks.append(text_chunk)
        i += chunk_tokens - overlap
    return [c.strip()]