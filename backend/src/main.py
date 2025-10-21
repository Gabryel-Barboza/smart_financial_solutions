from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .controllers import agent_controller, db_controller
from .exception_handler import ExceptionHandlerMiddleware

app = FastAPI(
    title='Smart Financial Solutions API',
    summary='API orquestradora de requisições para agentes e processamento de dados.',
    description="""## Agente Inteligente e ferramenta EDA para dados 🧠.
    
    """,
    root_path='/api',
    version='1.0.0',
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
    return True


app.include_router(agent_controller.router)
app.include_router(db_controller.router)
