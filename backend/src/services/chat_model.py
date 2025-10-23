"""Serviço para instanciação do agente supervisor e funções de chat."""

import mistune
from pydantic_core import ValidationError

from src.agents import SupervisorAgent
from src.controllers.websocket_controller import manager
from src.data import StatusUpdate
from src.schemas import ApiKeyInput, JSONOutput
from src.settings import settings
from src.utils.exceptions import ModelNotFoundException

MODELS = {
    'qwen/qwen3-32b': 'groq',
    'llama-3.1-8b-instant': 'groq',
    'llama-3.3-70b-versatile': 'groq',
    'openai/gpt-oss-20b': 'groq',
    'openai/gpt-oss-120b': 'groq',
    'gemini-2.5-flash': 'google',
    'gemini-2.5-pro': 'google',
}


class Chat:
    """
    Representa o serviço de chat que interage com o Agente Supervisor.
    """

    def __init__(self):
        pass

    async def send_prompt(self, user_input: str, session_id: str):
        """
        Envia a entrada do usuário para o Agente Supervisor e processa a resposta.
        """
        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_INIT)
        agent = SupervisorAgent(session_id)

        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_PROCESS)
        response: str = await agent.arun(user_input)

        content = response['output'].strip('`').replace('json', '', 1)

        # Tenta converter a string de conteúdo em um objeto JSON tipado (JSONOutput).
        # Algumas respostas do agente podem não ser geradas no formato exato esperado.
        try:
            response: JSONOutput = JSONOutput.model_validate(content)
            response = response.model_dump()
        except ValidationError:
            response = {'response': content, 'graph_id': ''}
        finally:
            response['response'] = mistune.html(response['response'])

        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_RESPONSE)

        return response

        # TODO: Mudar lógica para alterar modelos em runtime

    async def change_model(self, model_name: str):
        """Altera o modelo de linguagem utilizado pelo agente."""
        return NotImplemented
        #     provider = MODELS.get(model_name, None)

        #     if not provider:
        #         raise ModelNotFoundException(
        #             'Wrong model name received, try again with a valid model.'
        #         )

        #     if provider == 'google':
        #         self.agent.init_gemini_model(model_name=model_name, temperature=0)
        #     elif provider == 'groq':
        #         self.agent.init_groq_model(model_name=model_name, temperature=0)

        #     # Re-inicializa o agente com o novo modelo, mantendo a memória e as ferramentas.
        #     self.agent.initialize_agent(
        #         memory_key='chat_history', tools=self.agent.tools, prompt=self.agent.prompt
        #     )

        # return {'detail': f'Model changed to {model_name} by {provider.upper()}'}

    async def update_api_key(self, input: ApiKeyInput):
        """
        Atualiza a chave de API para o provedor do modelo especificado.
        """
        provider = MODELS.GET(input.model_name)

        # Atualiza a chave nas configurações globais
        if provider == 'google':
            settings.gemini_api_key = input.api_key
        elif provider == 'groq':
            settings.groq_api_key = input.api_key
        else:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        return {
            'detail': f'API key registered successfully for the {provider.capitalize()} models'
        }
