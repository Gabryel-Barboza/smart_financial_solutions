"""Serviço para instanciação do agente supervisor e funções de chat."""

import asyncio
import json
from collections import defaultdict
from time import time

import mistune
from langchain.output_parsers import PydanticOutputParser
from pydantic_core import ValidationError

from src.agents import (
    BaseAgent,
    DataAnalystAgent,
    DataEngineerAgent,
    ReportGenAgent,
    SupervisorAgent,
)
from src.controllers.websocket_controller import manager
from src.data import MODELS, TASK_PREDEFINED_MODELS, ModelTask, StatusUpdate
from src.schemas import JSONOutputModel
from src.utils.exceptions import APIKeyNotFoundException, ModelNotFoundException


class Chat:
    """
    Representa o serviço de chat que interage com o pool de agentes e gerencia as sessões ativas.
    """

    def __init__(self):
        self.active_sessions: dict[str, dict[str, BaseAgent | str]] = defaultdict(dict)
        self.agents_timestamp: dict[str, float] = {}

    async def _get_session(self, session_id: str) -> dict[str, BaseAgent | str] | None:
        return self.active_sessions.get(session_id)

    async def _del_session(self, session_id: str) -> None:
        if await self._get_session(session_id):
            del self.active_sessions[session_id]

        del self.agents_timestamp[session_id]

    async def _get_or_create_agent(
        self,
        session_id: str,
        agent_task: str = ModelTask.SUPERVISE,
        *,
        force_recreate: bool = False,
    ):
        """Função para instanciação e inserção de agentes no pool de sessões. Se invocada em uma sessão ativa, retorna o agente ativo ou instancia um novo caso contrário.

        Agentes ativos são mantidos vivos enquanto o Supervisor estiver em uso.
        Os agentes são guardados em um dicionário de sessões no formato:
        `{ session_id: { agent_task: BaseAgent } }`

        Args:
            session_id (str): Identificador da sessão para instancia do agente.
            agent_task (str, optional): Constante de ModelTask para identificação do agente a ser recuperado. Por padrão, retorna o Supervisor.
            force_recreate (bool, optional): Se os agentes devem ser instanciados novamente na sessão.
        Returns:
            agent (BaseAgent): Agente identificado por sessão e tipo de tarefa
        """
        current_session = await self._get_session(session_id)

        if not current_session:
            raise APIKeyNotFoundException(
                "Your current session doesn't have an API key, please add an API key before proceeding."
            )

        has_api_key = 'gemini_key' in current_session or 'groq_key' in current_session

        if not has_api_key:
            raise APIKeyNotFoundException(
                "Your current session doesn't have an API key, please add an API key before proceeding."
            )

        is_not_agent_instance = ModelTask.SUPERVISE not in current_session

        if is_not_agent_instance or force_recreate:
            # Instanciando todos os agentes que serão utilizados e passando o objeto da sessão
            current_session[ModelTask.DATA_ANALYSIS] = DataAnalystAgent(
                session_id, current_session=current_session
            )
            current_session[ModelTask.DATA_TREATMENT] = DataEngineerAgent(
                current_session=current_session
            )
            current_session[ModelTask.REPORT_GENERATION] = ReportGenAgent(
                current_session=current_session
            )
            # Supervisor por último para receber os agentes anteriores
            current_session[ModelTask.SUPERVISE] = SupervisorAgent(
                session_id, current_session=current_session
            )

        self.agents_timestamp[session_id] = time()

        return current_session[agent_task]

    async def send_prompt(self, session_id: str, user_input: str):
        """
        Envia a entrada do usuário para o Agente Supervisor e processa a resposta.

        Args:
            session_id (str): Identificador de sessão para vincular o agente.
            user_input (str): Mensagem do usuário para enviar ao agente
        """
        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_INIT)
        agent = await self._get_or_create_agent(session_id, ModelTask.SUPERVISE)

        # Formatador de saída para o agente
        parser = PydanticOutputParser(pydantic_object=JSONOutputModel)
        format_instructions = parser.get_format_instructions()

        # Execução do agente
        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_PROCESS)
        response = await agent.arun(
            user_input, **{'format_instructions': format_instructions}
        )

        content = response['output'].strip('`').replace('json', '', 1)

        # Tenta converter a string em um dicionário
        # Algumas respostas do agente podem não ser geradas no formato exato esperado
        try:
            response = json.loads(content)
            JSONOutputModel.model_validate(response)
        except (ValidationError, json.JSONDecodeError):
            response = {'response': content, 'graph_id': ''}
        finally:
            response['response'] = mistune.html(response['response'])

        await manager.send_status_update(session_id, StatusUpdate.SUPERVISOR_RESPONSE)

        return response

    async def change_model(self, session_id: str, model_name: str, agent_task: str):
        """Altera o modelo de linguagem utilizado pelo agente.

        Args:
            session_id (str): Identificador de sessão para recuperar o agente.
            model_name (str): Nome do novo modelo à ser usado.
            agent_task (str): Constante de ModelTask que identifica o agente para alteração por tarefa.
        """
        provider = MODELS.get(model_name, None)

        if not provider:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        agent: BaseAgent = await self._get_or_create_agent(session_id, agent_task)

        if provider == 'google':
            agent.init_gemini_model(model_name=model_name, temperature=0)
        elif provider == 'groq':
            agent.init_groq_model(model_name=model_name, temperature=0)

        # Reinicializa o agente com o novo modelo, mantendo a memória e as ferramentas.
        agent.initialize_agent(
            tools=agent.tools,
            prompt=agent.prompt,
            session_id=agent.session_id,
        )

        return {'detail': f'Model changed to {model_name} from {provider.upper()}'}

    async def get_agent_info(
        self, is_tasks: bool, is_default_models: bool
    ) -> dict[str, list]:
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

    async def update_api_key(self, session_id: str, api_key: str, provider: str):
        """
        Atualiza a chave de API para o provedor do modelo especificado.

        Args:
            api_key (str): Chave de API para o modelo desejado.
            provider (str): Provedor da chave de API recebida.
        """

        current_session = self.active_sessions[session_id]
        init_agent = False

        # Se já existir uma chave, re-instanciar o agente com novos valores
        if current_session.get('gemini_key') or current_session.get('groq_key'):
            init_agent = True

        # Atualiza a chave disponível na sessão
        if provider == 'google':
            current_session['gemini_key'] = api_key

        elif provider == 'groq':
            current_session['groq_key'] = api_key

        else:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        if init_agent:
            await self._get_or_create_agent(session_id, force_recreate=True)

        return {
            'detail': f'API key registered successfully! You can now use {provider.capitalize()} models'
        }

    async def cleanup_agents(self, interval: int = 300, ttl: int = 1800) -> None:
        """Função de limpeza para o pool de agentes, removendo agentes que expiraram (possuem tempo de vida maior do que o especificado).

        Args:
            interval (int, optional): Intervalo de tempo para checar a pool, em segundos.
            ttl (int, optional): Tempo de vida máximo de um agente na pool, em segundos.
        """

        print(
            f'\t>> Initializing cleanup task for agents. Checking for expired agents (last access > {ttl}s) with intervals of {interval}s.'
        )
        expired_sessions = []
        while True:
            try:
                await asyncio.sleep(interval)

                time_now = time()

                for session_id, last_access in self.agents_timestamp.items():
                    is_expired = (time_now - last_access) > ttl

                    if is_expired:
                        expired_sessions.append(session_id)

                if expired_sessions:
                    total_expired = len(expired_sessions)
                    message = 'entities' if total_expired > 1 else 'entity'

                    print(f'\t>> Executing cleanup task on {total_expired} {message}')

                    for session_id in expired_sessions:
                        await self._del_session(session_id)
                    else:
                        expired_sessions = []

            except Exception as exc:
                print(f'\t>> Error in cleanup event: {exc}')
                await asyncio.sleep(30)
