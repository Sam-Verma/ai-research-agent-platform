from pydantic import BaseModel, Field
from typing import List, Optional


class MemoryMessage(BaseModel):
    role: str
    content: str


class RetrievedDocument(BaseModel):
    source: str
    content: str
    score: float


class WebResult(BaseModel):
    title: str
    url: str
    snippet: str


class UnifiedContext(BaseModel):

    memory: List[MemoryMessage] = Field(
        default_factory=list
    )

    documents: List[
        RetrievedDocument
    ] = Field(
        default_factory=list
    )

    web_results: List[
        WebResult
    ] = Field(
        default_factory=list
    )

    summary: Optional[str] = None