from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

from app.core.config import settings


class LLMService:

    def __init__(self):

        self.http_client = httpx.AsyncClient(
            verify=False
        )
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            http_client=self.http_client
        )

        self.model = settings.LLM_MODEL
        
    async def close(self):
        await self.http_client.aclose()

    def _format_messages(self, messages):
        formatted = []

        for msg in messages:

            if isinstance(msg, dict):
                formatted.append(msg)

            elif hasattr(msg, "role"):
                # OpenAI SDK messages
                formatted.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

            elif hasattr(msg, "type"):
                # LangChain messages
                formatted.append(
                    {
                        "role": (
                            "user"
                            if msg.type == "human"
                            else "assistant"
                            if msg.type == "ai"
                            else msg.type
                        ),
                        "content": msg.content,
                    }
                )

            else:
                raise TypeError(
                    f"Unsupported message type: {type(msg)}"
                )

        return formatted

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(
        self,
        messages: list,
        temperature: float = 0.7,
    ) -> str:

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self._format_messages(messages),
            temperature=temperature,
        )

        return response.choices[0].message.content

    async def stream_generate(
        self,
        messages: list,
        temperature: float = 0.7,
    ):

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=self._format_messages(messages),
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta