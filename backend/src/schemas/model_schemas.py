"""Esquemas para validação de entradas e saídas no LLM."""

from pydantic import BaseModel, Field


class JSONOutputModel(BaseModel):
    response: str = Field(description='Your final answer to the user.')
    graph_id: str | list[str] = Field(
        description='Id of generated graph returned from tools, can be an empty string. Multiple ids can be returned, use a list for that case.'
    )


class QueryOutput(BaseModel):
    query: str = Field(description='Syntactically valid SQL query.')
