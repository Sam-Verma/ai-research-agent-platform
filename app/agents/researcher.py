from app.rag.retrieval import RetrievalService


retrieval_service = RetrievalService()


async def researcher_node(state):

    question = state["question"]

    result = await retrieval_service.ask(
        question
    )

    return {
        "research": result["answer"]
    }