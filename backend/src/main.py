import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.tools.data_extraction_tool import qdrant_store

from .controllers import agent_controller, db_controller, websocket_controller
from .exception_handler import ExceptionHandlerMiddleware
from .services.data_processing_services import session_manager
from .services.db_services import init_db

cleanup_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização de Bancos e Stores
    init_db()
    await qdrant_store.init_store('legislation_base_collection', 'user_data_collection')

    # Criação de tarefas de limpeza
    agent_cleanup_task = asyncio.create_task(agent_controller.chat.cleanup_agents())
    data_cleanup_task = asyncio.create_task(session_manager.cleanup_task())

    yield

    for task in (agent_cleanup_task, data_cleanup_task):
        if task:
            task.cancel()


app = FastAPI(
    title='Smart Financial Solutions API',
    summary='API orquestradora de requisições para agentes e processamento de dados.',
    description="""## Agente Inteligente e ferramenta EDA para dados 🧠.
    
    """,
    root_path='/api',
    version='1.0.0',
    lifespan=lifespan,
)

# CORS para restrição de domínios, liberal por padrão.
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(ExceptionHandlerMiddleware)

# Rotas


@app.head('/healthz', status_code=200)
async def ping():
    """
    Verifica o status operacional da API.
    Retorna HTTP 200 OK se a aplicação estiver em execução.
    """
    return


app.include_router(agent_controller.router)
app.include_router(db_controller.router)
app.include_router(websocket_controller.router)
