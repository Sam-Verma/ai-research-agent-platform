from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.llm_service import LLMService


class RetrievalService:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.llm_service = LLMService()

    async def ask(
        self,
        project_id: int,
        question: str
    ):

        query_embedding = (
            self.embedding_service.embed_text(question)
        )

        results = self.qdrant_service.search(
            query_embedding=query_embedding,
            project_id=project_id
        )

        context = "\n\n".join(
            [
                r.payload["text"]
                for r in results
            ]
        )

        messages = [
            {
                "role": "system",
                "content": """
                You are a research assistant.

                Answer ONLY from the provided context.

                If answer is not present, say:
                'I could not find this in the documents.'
                """
            },
            {
                "role": "user",
                "content": f"""
                Context:
                {context}

                Question:
                {question}
                """
            }
        ]

        response = await self.llm_service.generate(
            messages=messages
        )

        return {
            "answer": response,
            "sources_found": len(results),
            "sources": [
                r.payload.get("source")
                for r in results
            ]
        }