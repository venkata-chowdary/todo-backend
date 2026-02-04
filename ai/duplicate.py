from app.ai.embeddings import generate_embedding
from app.ai.vector_store import collection
DUPLICATE_THRESHOLD = 0.75


async def check_duplicate(title: str, description: str):
    # title="Finish ML"
    # description="revise basics of ML by end of this week"
    combined_text = f"{title} . {description or ''}"
    print("checking for duplicates")
    emd=await generate_embedding(combined_text)
    
    results = collection.query(
        query_embeddings=[emd],
        n_results=3
    )
    
    similar_tasks = []    
    if not results['distances']:
        return []

    for i, distance in enumerate(results["distances"][0]):
        similarity = 1 - distance

        if similarity >= DUPLICATE_THRESHOLD:
            similar_tasks.append({
            "title": results["documents"][0][i],
            "similarity": round(similarity, 2),
            "source": results["metadatas"][0][i]["source"]
        })

    return similar_tasks[0] if similar_tasks else []
