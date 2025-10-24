"""Serviço para instanciação do agente supervisor e funções de chat."""

import asyncio
import json
from time import time

import mistune
from pydantic_core import ValidationError

from src.agents import SupervisorAgent
from src.controllers.websocket_controller import manager
from src.data import MODELS, StatusUpdate
from src.data.models import ModelTask
from src.schemas import ApiKeyInput, JSONOutput
from src.settings import settings
from src.utils.exceptions import ModelNotFoundException


class Chat:
    """
    Representa o serviço de chat que interage com o pool de agentes e gerencia as sessões ativas.
    """

    def __init__(self):
        self.active_sessions: dict[str, SupervisorAgent] = {}
        self.agent_timestamp: dict[str, float] = {}

    async def _get_or_create_agent(self, session_id: str):
        """Função para instanciação e inserção de agentes no pool de sessões. Se invocada em uma sessão ativa, retorna o agente ativo ou instancia um novo caso contrário.

        Agentes ativos são mantidos vivos enquanto estiverem em uso.

        Args:
            session_id (str): Identificador da sessão para instancia do agente.
        """
        if session_id not in self.active_sessions:
            agent = SupervisorAgent(session_id)
            self.active_sessions[session_id] = agent
            self.agent_timestamp[session_id] = time()
            return agent

        self.agent_timestamp[session_id] = time()
        return self.active_sessions[session_id]

    async def cleanup_agents(self, interval: int = 300, ttl: int = 1800):
        """Função de limpeza para o pool de agentes, removendo agentes que expiraram (possuem tempo de vida maior do que o especificado).

        Args:
            interval (int, optional): Intervalo de tempo para checar a pool.
            ttl (int, optional): Tempo de vida máximo de um agente na pool.
        """

        while True:
            await asyncio.sleep(interval)

            print('Começando serviço de limpeza da pool de agentes.')
            time_now = time()
            expired_sessions = []

            for session_id, last_access in self.agent_timestamp.items():
                isExpired = (time_now - last_access) > ttl

                if isExpired:
                    expired_sessions.push(session_id)

            for session_id in expired_sessions:
                del self.agent_timestamp[session_id]
                del self.active_sessions[session_id]

    async def send_prompt(self, user_input: str, session_id: str):
        """
        Envia a entrada do usuário para o Agente Supervisor e processa a resposta.

        Args:
            session_id (str): Identificador de sessão para vincular o agente.
        """
        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_INIT)
        agent = await self._get_or_create_agent(session_id)

        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_PROCESS)
        response = await agent.arun(user_input)

        content = response['output'].strip('`').replace('json', '', 1)

        # Tenta converter a string em um dicionário
        # Algumas respostas do agente podem não ser geradas no formato exato esperado
        try:
            response = json.loads(content)
            JSONOutput.model_validate(response)
        except (ValidationError, json.JSONDecodeError):
            response = {'response': content, 'graph_id': ''}
        finally:
            response['response'] = mistune.html(response['response'])

        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_RESPONSE)

        return response

    async def change_model(self, model_name: str, session_id: str):
        """Altera o modelo de linguagem utilizado pelo agente.

        Args:
            model_name (str): Nome do novo modelo à ser usado.
            session_id (str): Identificador de sessão para recuperar o agente.
        """
        provider = MODELS.get(model_name, None)
        agent = self.active_sessions.get(session_id)

        if not provider:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        if not agent:
            raise ModelNotFoundException(
                'No model available for current session, please initialize an agent first!'
            )

        if provider == 'google':
            agent.init_gemini_model(model_name=model_name, temperature=0)
        elif provider == 'groq':
            agent.init_groq_model(model_name=model_name, temperature=0)

        # Reinicializa o agente com o novo modelo, mantendo a memória e as ferramentas.
        agent.initialize_agent(
            task_type=ModelTask.SUPERVISE,
            tools=self.tools,
            prompt=self.prompt,
            session_id=self.session_id,
        )

        return {'detail': f'Model changed to {model_name} from {provider.upper()}'}

    async def update_api_key(self, input: ApiKeyInput):
        """
        Atualiza a chave de API para o provedor do modelo especificado.

        Args:
            input (ApiKeyInput): Dicionário com o nome do modelo e uma chave de API para trocar. O modelo deve ser do mesmo provedor do que a chave.
        """
        provider = MODELS.get(input.model_name)

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
