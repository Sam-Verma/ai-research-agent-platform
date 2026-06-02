from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class RetrievalContextService:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    async def retrieve(
        self,
        query: str,
        project_id: int,
        limit: int = 5
    ):

        query_embedding = (
            self.embedding_service.embed_text(query)
        )

        results = self.qdrant_service.search(
            query_embedding=query_embedding,
            project_id=project_id,
            limit=limit
        )

        documents = []

        for result in results:

            documents.append(
                {
                    "source":
                        result.payload.get(
                            "source",
                            "unknown"
                        ),

                    "content":
                        result.payload.get(
                            "text",
                            ""
                        ),

                    "score":
                        float(result.score)
                }
            )

        return documents