"""Esquemas para validação de entradas e saídas no LLM."""

from pydantic import BaseModel, Field


class JSONOutput(BaseModel):
    response: str = Field(description='Model answer.')
    graph_id: str = Field(description='plotly graph_id returned when required.')


class QueryOutput(BaseModel):
    query: str = Field(description='Syntactically valid SQL query.')
