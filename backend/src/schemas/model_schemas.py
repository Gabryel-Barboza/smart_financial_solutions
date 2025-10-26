"""Esquemas para validação de entradas e saídas no LLM."""

from pydantic import BaseModel, Field


class JSONOutput(BaseModel):
    response: str = Field(description='Model answer.')
    graph_id: str | list = Field(
        description='plotly graph_id returned when required. Multiple graphs can be returned'
    )


class QueryOutput(BaseModel):
    query: str = Field(description='Syntactically valid SQL query.')
