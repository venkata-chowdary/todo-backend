from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
def get_llm():
    return GoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.9)
