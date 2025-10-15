from pydantic import BaseModel


class UserInput(BaseModel):
    request: str
    thread_id: str


class ApiKeyInput(BaseModel):
    api_key: str
    model_name: str
