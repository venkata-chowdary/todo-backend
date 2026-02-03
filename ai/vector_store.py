import chromadb
CHROMA_PATH = "./chroma_data"

client=chromadb.PersistentClient(CHROMA_PATH)
collection = client.get_or_create_collection(
    name="todos"
)
