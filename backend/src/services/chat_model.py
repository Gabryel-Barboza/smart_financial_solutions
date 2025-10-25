"""Serviço para instanciação do agente supervisor e funções de chat."""

import asyncio
import json
from time import time

import mistune
from pydantic_core import ValidationError

from src.agents import SupervisorAgent
from src.controllers.websocket_controller import manager
from src.data import MODELS, ModelTask, StatusUpdate, TASK_PREDEFINED_MODELS
from src.schemas import JSONOutput
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
            interval (int, optional): Intervalo de tempo para checar a pool, em segundos.
            ttl (int, optional): Tempo de vida máximo de um agente na pool, em segundos.
        """

        print(
            f'\t>> Initializing cleanup task. Checking for expired agents (last access > {ttl}s) with intervals of {interval}s.'
        )
        expired_sessions = []
        while True:
            try:
                await asyncio.sleep(interval)

                time_now = time()

                for session_id, last_access in self.agent_timestamp.items():
                    isExpired = (time_now - last_access) > ttl

                    if isExpired:
                        expired_sessions.append(session_id)

                if expired_sessions:
                    total_expired = len(expired_sessions)
                    message = 'entities' if total_expired > 1 else 'entity'

                    print(f'\t>> Executing cleanup task on {total_expired} {message}')

                    for session_id in expired_sessions:
                        del self.agent_timestamp[session_id]
                        del self.active_sessions[session_id]
                    else:
                        expired_sessions = []

            except Exception as exc:
                print(f'\t>> Error in cleanup event: {exc}')
                await asyncio.sleep(30)

    async def send_prompt(self, session_id: str, user_input: str):
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

    async def change_model(
        self,
        session_id: str,
        model_name: str,
    ):
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
            agent = await self._get_or_create_agent(session_id)

        if provider == 'google':
            agent.init_gemini_model(model_name=model_name, temperature=0)
        elif provider == 'groq':
            agent.init_groq_model(model_name=model_name, temperature=0)

        # Reinicializa o agente com o novo modelo, mantendo a memória e as ferramentas.
        agent.initialize_agent(
            task_type=ModelTask.SUPERVISE,
            tools=agent.tools,
            prompt=agent.prompt,
            session_id=agent.session_id,
        )

        return {'detail': f'Model changed to {model_name} from {provider.upper()}'}

    async def get_agent_info(self, is_tasks: bool, is_default_models: bool) -> dict[str, list]:
        """Função para recuperar informações de agentes, como todos os modelos disponíveis para instancia.

        Args:
            is_tasks (bool): Se deve ser retornado todos os tipos de tarefas dos agentes.
            is_default_models (bool): Se deve ser retornado o modelo padrão para cada tarefa.

        Returns:
            result_list (list[str]): Retorna uma lista com todos os modelos ou tarefas para os agentes.
        """

        if is_tasks:
            result = [task.value for task in ModelTask]
        elif is_default_models:
            result = TASK_PREDEFINED_MODELS
        else:
            result = MODELS

        return result

    async def update_api_key(self, api_key: str, provider: str):
        """
        Atualiza a chave de API para o provedor do modelo especificado.

        Args:
            api_key (str): Chave de API para o modelo desejado.
            provider (str): Provedor da chave de API recebida.
        """

        # Atualiza a chave nas configurações globais
        if provider == 'google':
            settings.gemini_api_key = api_key
        elif provider == 'groq':
            settings.groq_api_key = api_key
        else:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        return {
            'detail': f'API key registered successfully for the {provider.capitalize()} models'
        }
