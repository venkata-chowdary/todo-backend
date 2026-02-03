from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from dotenv import load_dotenv
load_dotenv()

print("Starting Embedding Model demo...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

async def generate_embedding(text:str) -> list[float]:
    return await embeddings.aembed_query(text)