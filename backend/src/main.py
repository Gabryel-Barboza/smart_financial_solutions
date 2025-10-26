import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .controllers import agent_controller, db_controller, websocket_controller
from .exception_handler import ExceptionHandlerMiddleware
from .services.data_processing import session_manager
from .services.db_services import init_db

cleanup_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    agent_cleanup_task = asyncio.create_task(agent_controller.chat.cleanup_agents())
    data_cleanup_task = asyncio.create_task(session_manager.cleanup_task())

    yield

    if agent_cleanup_task:
        agent_cleanup_task.cancel()

    if data_cleanup_task:
        data_cleanup_task.cancel()


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
