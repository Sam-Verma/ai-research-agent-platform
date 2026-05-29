import certifi
import httpx

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class LLMService:

    def __init__(self):

        http_client = httpx.AsyncClient(
        verify=False
        )
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            http_client=http_client
        )

        self.model = settings.LLM_MODEL

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
            messages=messages,
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
            messages=messages,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:

            delta = chunk.choices[0].delta.content

            if delta:
                yield delta