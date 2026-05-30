from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.core.config import settings


class QdrantService:

    def __init__(self):

        self.client = QdrantClient(
            url=settings.QDRANT_URL
        )

        self.collection_name = "research_documents"

    def create_collection(self):

        collections = self.client.get_collections()

        exists = any(
            c.name == self.collection_name
            for c in collections.collections
        )

        if exists:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )
    
    def search(
        self,
        query_embedding: list[float],
        project_id: int,
        limit: int = 5,
    ):
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="project_id",
                        match=MatchValue(value=project_id),
                    )
                ]
            ),
        )

        return results.points