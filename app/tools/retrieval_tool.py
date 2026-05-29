from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


embedding_service = EmbeddingService()
qdrant_service = QdrantService()

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
    limit: int = 5,
):

    query_embedding = (
        embedding_service.embed_text(query)
    )

    results = qdrant_service.search(
        query_embedding=query_embedding,
        limit=limit,
    )

    contexts = []

    for r in results:

        contexts.append(
            r.payload["text"]
        )

    return "\n\n".join(contexts)