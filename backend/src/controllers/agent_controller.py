"""Rotas para serviços relacionados ao agente"""

from fastapi import APIRouter, Form, UploadFile
from typing_extensions import Annotated

from src.schemas import ApiKeyInput, ModelChangeInput, UserInput
from src.services import Chat, DataHandler

router = APIRouter()
data_handler = DataHandler()
chat = Chat()


@router.get('/agent-info', status_code=200)
async def get_agent_info(tasks: bool = False, defaults: bool = False):
    response = await chat.get_agent_info(tasks, defaults)

    return response


@router.post('/upload', status_code=201)
async def csv_input(
    separator: str, file: UploadFile, session_id: Annotated[str, Form()]
):
    response = await data_handler.load_csv(session_id, file, separator)

    return {'data': response}


@router.post('/upload/image', status_code=201)
async def image_processing(file: UploadFile, session_id: Annotated[str, Form()]):
    image_text = await data_handler.read_uploaded_image(session_id, file)

    response = await chat.send_prompt(session_id, image_text)

    return response


@router.post('/prompt', status_code=201)
async def prompt_model(input: UserInput):
    response = await chat.send_prompt(input.session_id, input.request)

    return response


# TODO: Adicionar key separada por sessão
@router.post('/send-key', status_code=200)
async def send_key(input: ApiKeyInput):
    response = await chat.update_api_key(input.api_key, input.provider)

    return response


# TODO: Implementar alteração do modelo para outros agentes
@router.put('/change-model', status_code=200)
async def change_model(input: ModelChangeInput):
    response = await chat.change_model(input.session_id, input.model_name)

    return response
