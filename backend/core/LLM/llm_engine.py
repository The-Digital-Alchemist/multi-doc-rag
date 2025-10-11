from openai import OpenAI
import os

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=api_key)


def generate_answer(query: str, contexts: list[str]):
    client = get_client()
    prompt = f""""You are an assistant with access to retrieved contexts from various documents.
    Using the information you find in the documents, answer the user query using only the contexts below.


    Context: 
    {chr(10).join(contexts)}

    Query: {query}

    Answer: 
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip() # type: ignore