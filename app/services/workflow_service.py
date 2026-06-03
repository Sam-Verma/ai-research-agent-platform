from langgraph.graph import StateGraph, END
import json

from app.agents.state import ResearchState
from app.services.llm_service import LLMService
from app.services.chat_memory_service import ChatMemoryService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.tools.retrieval_tool import search_documents
from app.tools.web_search_tool import web_search


class WorkflowService:
    def __init__(
        self,
        llm_service: LLMService,
        chat_memory_service: ChatMemoryService,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
    ):
        self.llm_service = llm_service
        self.memory_service = chat_memory_service
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ResearchState)
        workflow.add_node("planner", self.planner_node)
        workflow.add_node("researcher", self.researcher_node)
        workflow.add_node("summarizer", self.summarizer_node)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "summarizer")
        workflow.add_edge("summarizer", END)

        return workflow.compile()

    async def planner_node(self, state: ResearchState) -> ResearchState:
        question = state["question"]
        messages = [
            {
                "role": "system",
                "content": "You are a planning agent. Create a concise, step-by-step research plan for answering the user question."
            },
            {
                "role": "user",
                "content": question
            }
        ]

        response = await self.llm_service.generate(messages=messages)
        return {"plan": response}

    async def researcher_node(self, state: ResearchState) -> ResearchState:
        project_id = state["project_id"]
        question = state["question"]
        plan = state.get("plan", "")
        mode = state.get("mode", "")

        system_msg = f"You are a researcher agent. Your goal is to gather information to answer the user's question.\nHere is the research plan: {plan}\n\nAvailable Tools:\n- search_documents: searches internal documents.\n- web_search: searches the internet.\n- scrape_website: extracts detailed text from a specific URL.\n\nUse the tools to gather necessary context. Return the raw gathered context."
        if mode == 'deep':
            system_msg = "DEEP RESEARCH MODE ENABLED. Be thorough: iterate on searches, query multiple angles, use both internal document search and web search, and prioritize primary sources. If appropriate, perform additional tool calls to expand coverage and return extensive context with clear citations.\n\n" + system_msg

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ]

        response = await self.llm_service.client.chat.completions.create(
            model=self.llm_service.model,
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_documents",
                        "description": "Search uploaded documents for relevant information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "scrape_website",
                        "description": "Scrapes the content of a specific webpage URL to extract detailed information.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "The full URL of the website to scrape."}
                            },
                            "required": ["url"]
                        }
                    }
                }
            ],
            tool_choice="auto",
        )

        message = response.choices[0].message
        research_context = ""
        citations = []

        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if func_name == "search_documents":
                    results = search_documents(
                        query=args.get("query"),
                        project_id=project_id,
                        embedding_service=self.embedding_service,
                        qdrant_service=self.qdrant_service
                    )
                    for idx, item in enumerate(results, start=1):
                        research_context += (
                            f"\n\n[Document Search Result {idx} from {item['source']}]:\n{item['snippet']}"
                        )
                        citations.append({
                            "type": "document",
                            "source": item["source"],
                            "snippet": item["snippet"],
                            "query": args.get("query"),
                            "id": item.get("id"),
                        })
                
                elif func_name == "web_search":
                    results = web_search(query=args.get("query"))
                    for idx, result in enumerate(results, start=1):
                        research_context += (
                            f"\n\n[Web Search Result {idx} - {result.get('title', 'online source')}]:\n{result.get('body', '')[:800]}"
                        )
                        citations.append({
                            "type": "web",
                            "title": result.get("title", "Web Source"),
                            "link": result.get("link"),
                            "snippet": result.get("body", "")[:200],
                            "query": args.get("query"),
                        })
                
                elif func_name == "scrape_website":
                    from app.tools.scrape_tool import scrape_website
                    result = scrape_website(url=args.get("url"))
                    research_context += (
                        f"\n\n[Website Scrape Result for {args.get('url')}]:\n{result[:800]}"
                    )
                    citations.append({
                        "type": "web",
                        "title": args.get("url"),
                        "link": args.get("url"),
                        "snippet": result[:200],
                        "query": args.get("url"),
                    })

        # If no tools were used, the researcher might just have answered directly
        if not research_context and message.content:
            research_context = message.content

        return {"research": research_context, "citations": citations}

    async def summarizer_node(self, state: ResearchState) -> ResearchState:
        question = state["question"]
        research = state.get("research", "")
        citations = state.get("citations", [])

        source_text = ""
        if citations:
            source_lines = []
            for idx, source in enumerate(citations, start=1):
                if source["type"] == "document":
                    source_lines.append(f"[{idx}] Document source: {source['source']}\nSnippet: {source['snippet']}")
                else:
                    source_lines.append(f"[{idx}] Web source: {source.get('title', source.get('link', 'unknown'))} ({source.get('link', source.get('title'))})\nSnippet: {source['snippet']}")
            source_text = "\n\n".join(source_lines)

        prompt_content = f"Original Question: {question}\n\nResearch Context: {research}"
        if source_text:
            prompt_content += f"\n\nSources:\n{source_text}"

        messages = [
            {
                "role": "system",
                "content": "You are a summarization agent. Create a concise, well-formatted final answer based on the provided research context. Clearly cite sources using numbered references like [1], [2], and include a Sources section at the end."
            },
            {
                "role": "user",
                "content": prompt_content
            }
        ]

        response = await self.llm_service.generate(messages=messages)
        return {"answer": response, "citations": citations}

    async def execute(self, project_id: int, session_id: str, question: str) -> dict:
        await self.memory_service.get_or_create_session(
            project_id=project_id,
            session_id=session_id,
        )

        # Get history to optionally pass in, but for now we focus on the main state
        history = await self.memory_service.get_history(
            project_id=project_id,
            session_id=session_id,
        )

        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="user",
            content=question,
        )

        initial_state = {
            "project_id": project_id,
            "session_id": session_id,
            "question": question,
            "messages": history,
            "plan": "",
            "research": "",
            "answer": "",
            "citations": [],
        }

        # Run the workflow
        final_state = await self.graph.ainvoke(initial_state)

        answer = final_state.get("answer", "No answer generated.")

        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        return {
            "answer": answer,
            "plan": final_state.get("plan"),
            "research": final_state.get("research"),
            "citations": final_state.get("citations", []),
        }
