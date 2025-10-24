"""Rotas para serviços relacionados ao agente"""

from fastapi import APIRouter, Form, UploadFile
from typing_extensions import Annotated

from src.schemas import ApiKeyInput, ModelChangeInput, UserInput
from src.services import Chat, DataHandler

router = APIRouter()
data_handler = DataHandler()
chat = Chat()


@router.post('/upload', status_code=201)
async def csv_input(
    separator: str, file: UploadFile, session_id: Annotated[str, Form()]
):
    response = await data_handler.load_csv(session_id, file, separator)

    return {'data': response}


@router.post('/prompt', status_code=201)
async def prompt_model(input: UserInput):
    response = await chat.send_prompt(input.request, input.session_id)

    return response


@router.put('/change-model', status_code=200)
async def change_model(input: ModelChangeInput):
    response = await chat.change_model(input.model_name, input.session_id)

    return response


@router.post('/send-key', status_code=200)
async def send_key(input: ApiKeyInput):
    response = await chat.update_api_key(input)

    return response
