from app.ai.vector_store import collection
from app.ai.embeddings import generate_embedding

async def semantic_search(
    query: str,
    limit: int = 5
):
    query_embedding = await generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit
    )

    return results
