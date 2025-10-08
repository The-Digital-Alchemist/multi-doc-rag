from openai import OpenAI
import os


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer(query: str, contexts: list[str]):
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