from app.schemas.context import (
    UnifiedContext
)


class PromptBuilder:

    @staticmethod
    def build(
        question: str,
        context: UnifiedContext
    ):

        memory_context = ""

        if context.memory:

            memory_context = "\n".join(
                [
                    (
                        f"{message.role}: "
                        f"{message.content}"
                    )
                    for message in context.memory
                ]
            )

        document_context = ""

        if context.documents:

            document_context = (
                "\n\n".join(
                    [
                        f"""
SOURCE:
{document.source}

CONTENT:
{document.content}
                        """.strip()

                        for document
                        in context.documents
                    ]
                )
            )

        web_context = ""

        if context.web_results:

            web_context = (
                "\n\n".join(
                    [
                        f"""
TITLE:
{web.title}

URL:
{web.url}

SNIPPET:
{web.snippet}
                        """.strip()

                        for web
                        in context.web_results
                    ]
                )
            )

        return [

            {
                "role": "system",
                "content": """
You are an advanced AI research assistant.

Your job is to answer using:

1. Project documents
2. Previous conversation memory
3. Web context (if available)

Rules:

- Prefer project documents first.
- Use memory for continuity.
- If information is unavailable,
say:
'I could not find this in the project documents.'

- Never hallucinate.
- Mention sources when relevant.
- Be concise but informative.
- Use bullet points when useful.
- If comparing things, use tables.
                """.strip()
            },

            {
                "role": "user",
                "content": f"""
CONVERSATION MEMORY:
{memory_context}


PROJECT DOCUMENTS:
{document_context}


WEB RESULTS:
{web_context}


QUESTION:
{question}
                """.strip()
            }
        ]