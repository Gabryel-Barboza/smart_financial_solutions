"""Esquemas para validação da entrada e saída do usuário."""

from pydantic import BaseModel


class UserInput(BaseModel):
    request: str
    session_id: str


class ApiKeyInput(BaseModel):
    api_key: str
    provider: str
    session_id: str


class ModelChangeInput(BaseModel):
    agent_task: str
    model_name: str
    session_id: str
