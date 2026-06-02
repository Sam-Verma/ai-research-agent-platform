from fastapi import Depends
from app.db.session import get_db

from app.services.llm_service import LLMService
from app.services.chat_memory_service import ChatMemoryService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


# Global instances for services that should be singletons
_llm_service = None
_embedding_service = None
_qdrant_service = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_qdrant_service() -> QdrantService:
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service


def get_chat_memory_service() -> ChatMemoryService:
    # ChatMemoryService can be instanced per request or globally,
    # but it just wraps DB calls. Since we are refactoring it to take get_db,
    # let's just return a new instance or it can take db session.
    # We will modify ChatMemoryService to take db session.
    return ChatMemoryService()

def get_workflow_service(
    llm_service = Depends(get_llm_service),
    chat_memory_service = Depends(get_chat_memory_service),
    embedding_service = Depends(get_embedding_service),
    qdrant_service = Depends(get_qdrant_service),
):
    from app.services.workflow_service import WorkflowService
    return WorkflowService(
        llm_service=llm_service,
        chat_memory_service=chat_memory_service,
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )
