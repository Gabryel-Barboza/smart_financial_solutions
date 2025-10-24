"""Classe para gerenciamento de exceções e respostas ao usuário"""

import logging
from zipfile import BadZipFile

from fastapi import status
from fastapi.responses import JSONResponse
from google.api_core.exceptions import ResourceExhausted
from groq import APIStatusError
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.exceptions import (
    APIKeyNotFoundException,
    ModelNotFoundException,
    WrongFileTypeError,
)


# sobrescrevendo métodos da classe base
class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)

            return response
        except (
            APIKeyNotFoundException,
            WrongFileTypeError,
            ModelNotFoundException,
        ) as exc:
            return JSONResponse(
                content=exc.msg, status_code=status.HTTP_400_BAD_REQUEST
            )
        except BadZipFile:
            return JSONResponse(
                content='Bad zip file sent, maybe the file is corrupted or empty.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except FileNotFoundError as exc:
            return JSONResponse(
                content=exc.strerror,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except APIStatusError as exc:
            logging.exception(exc.message)
            return JSONResponse(
                content="Failed in API call! Please check if your API is valid and haven't exceeded its limits",
                status_code=exc.status_code,
            )
        except ResourceExhausted as exc:
            logging.exception(exc.message)
            return JSONResponse(
                content="Failed in API call! Please check if your API key is valid and haven't exceeded its limits",
                status_code=exc.code,
            )
        except ChatGoogleGenerativeAIError:
            return JSONResponse(
                content='Failed to create a new Gemini model chat, check if your API key is correct or try sending it again.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
