from langchain_core.prompts import ChatPromptTemplate


RESEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an expert AI research assistant.

            Your job is to provide:
            - accurate answers
            - concise explanations
            - structured responses
            """
        ),
        (
            "human",
            """
            Research Topic:
            {topic}
            """
        )
    ]
)