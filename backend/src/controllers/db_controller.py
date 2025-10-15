from fastapi import APIRouter

from src.services import get_graph_db, init_db

router = APIRouter()

init_db()


@router.get('/graphs/{graph_id}', status_code=200)
async def get_graph(graph_id: str):
    results = get_graph_db(graph_id)

    return {'graph': results}
