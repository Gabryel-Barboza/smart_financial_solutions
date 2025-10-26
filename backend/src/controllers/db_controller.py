"""Rotas para serviços relacionados ao banco de dados"""

import asyncio

from fastapi import APIRouter

from src.services import get_graph_db

router = APIRouter()


@router.get('/graphs/{graph_id}', status_code=200)
async def get_graph(graph_id: str):
    results = await asyncio.to_thread(get_graph_db, graph_id)

    return {'graph': results}
