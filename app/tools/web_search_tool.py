from ddgs import DDGS


def web_search(
    query: str,
    max_results: int = 5,
):

    results = []

    with DDGS() as ddgs:

        search_results = ddgs.text(
            query,
            max_results=max_results,
        )

        for r in search_results:

            results.append(
                {
                    "title": r["title"],
                    "body": r["body"],
                    "link": r["href"],
                }
            )

    return results


web_search_tool_definition = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": """
        Search the web for current information.
        Use this for topics not found
        in uploaded documents.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                }
            },
            "required": ["query"]
        }
    }
}