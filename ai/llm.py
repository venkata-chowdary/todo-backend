from langchain_google_genai import GoogleGenerativeAI
import os

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in environment")

    return GoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
        api_key=api_key
    )
