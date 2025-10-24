"""Esquemas para validação da entrada e saída do usuário."""

from pydantic import BaseModel


class UserInput(BaseModel):
    request: str
    session_id: str


class ApiKeyInput(BaseModel):
    api_key: str
    model_name: str


class ModelChangeInput(BaseModel):
    model_name: str
    session_id: str
