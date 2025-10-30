"""Rotas para serviços relacionados ao agente"""

from fastapi import APIRouter, Form, UploadFile
from typing_extensions import Annotated

from src.schemas import ApiKeyInput, ModelChangeInput, UserEmailInput, UserInput
from src.services.chat_model_services import Chat
from src.services.data_processing_services import DataHandler

router = APIRouter()
data_handler = DataHandler()
chat = Chat()


@router.get('/agent-info', status_code=200)
async def get_agent_info(tasks: bool = False, defaults: bool = False):
    response = await chat.get_agent_info(tasks, defaults)

    return response


@router.post('/upload', status_code=201)
async def file_input(
    separator: str, file: UploadFile, session_id: Annotated[str, Form()]
):
    response = await data_handler.load_data(session_id, file, separator)

    if isinstance(response, dict) and response.get('process'):
        user_input = f'The following data was extracted from a XML file and possibly contain valid data to store, identify its context to understand if its useful to store and use the tools necessary, return a response in Portuguese Brazilian: \n\n{response.get("results")}'

        response = await chat.extract_data(session_id, user_input)

        return response

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


@router.post('/send-key', status_code=201)
async def send_key(input: ApiKeyInput):
    response = await chat.update_api_key(
        input.session_id, input.api_key, input.provider
    )

    return response


@router.post('/send-email', status_code=201)
async def register_email(input: UserEmailInput):
    response = await chat.insert_email(input.session_id, input.user_email)

    return response


@router.put('/change-model', status_code=200)
async def change_model(input: ModelChangeInput):
    response = await chat.change_model(
        input.session_id, input.model_name, input.agent_task
    )

    return response
