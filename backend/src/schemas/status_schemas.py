"""Esquemas para modelo de status da comunicação WebSocket."""

from typing import Literal

from pydantic import BaseModel


class StatusOutput(BaseModel):
    name: str
    desc: str
    status: Literal['pending', 'in-progress', 'complete', 'error']
