from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    title: str
    query: str