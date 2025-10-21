"""Rotas para serviços relacionados ao agente"""

from fastapi import APIRouter, UploadFile

from src.schemas import ApiKeyInput, UserInput
from src.services import Chat, DataHandler

router = APIRouter()
data_handler = DataHandler()
chat = Chat()


@router.post('/upload', status_code=201)
async def csv_input(
    separator: str,
    file: UploadFile,
):
    response = await data_handler.load_csv(file, separator)

    return {'data': response}


@router.post('/prompt', status_code=202)
async def prompt_model(input: UserInput):
    response = await chat.send_prompt(input.request, input.session_id)
    return response


@router.put('/change-model', status_code=202)
async def change_model(model: str):
    response = await chat.change_model(model)
    return response


@router.post('/send-key', status_code=202)
async def send_key(input: ApiKeyInput):
    response = await chat.update_api_key(input)

    return response
