from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


retrieval_tool_definition = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": """
        Search uploaded documents
        for relevant information.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    }
}

def search_documents(
    query: str,
    project_id: int,
    embedding_service: EmbeddingService,
    qdrant_service: QdrantService,
    limit: int = 5,
):

    query_embedding = (
        embedding_service.embed_text(query)
    )

    results = qdrant_service.search(
        query_embedding=query_embedding,
        project_id=project_id,
        limit=limit,
    )

    documents = []

    for r in results:
        text = r.payload.get("text", "")
        source = r.payload.get("source", "unknown source")

        documents.append({
            "id": getattr(r, "id", None),
            "text": text,
            "source": source,
            "snippet": text[:800],
        })

    return documents
