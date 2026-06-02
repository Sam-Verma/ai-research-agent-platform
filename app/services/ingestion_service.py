import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from qdrant_client.models import PointStruct

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class IngestionPipeline:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

    def ingest_pdf(
        self,
        file_path: str,
        project_id: int,
    ):

        loader = PyPDFLoader(file_path)

        documents = loader.load()

        chunks = self.text_splitter.split_documents(
            documents
        )

        points = []

        for chunk in chunks:

            embedding = self.embedding_service.embed_text(
                chunk.page_content
            )

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "project_id": project_id,
                    "text": chunk.page_content,
                    "source": file_path.split("/")[-1],
                }
            )

            points.append(point)

        self.qdrant_service.client.upsert(
            collection_name=self.qdrant_service.collection_name,
            points=points,
        )

        return {
            "chunks": len(chunks),
            "status": "completed"
        }