"""Classe base para outros agentes herdarem métodos comuns."""

import os
import tempfile

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.memory import BaseMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.data import TASK_PREDEFINED_MODELS, ModelTask
from src.settings import settings
from src.utils.exceptions import (
    APIKeyNotFoundException,
    ExecutorNotFoundException,
    ModelNotFoundException,
)

DEBUG_MODE = settings.debug_mode


# TODO: Verificar o motivo de ConversationSummarizeMemory não injetar no histórico e implementá-lo novamente
# Agente base para reaproveitamento e herança
class BaseAgent:
    def __init__(
        self,
        llm: BaseChatModel | None = None,
        *,
        gemini_key: str | None = None,
        groq_key: str | None = None,
        memory_key: str = 'chat_history',
    ):
        self._llm = llm
        self.agent = None
        self.gemini_key = gemini_key
        self.groq_key = groq_key
        self.memory_key = memory_key
        self.prompt = ChatPromptTemplate(
            [
                (
                    'system',
                    'You are a helpful agent that answers questions, respond to the questions objectively and only when certain, use the tools available to create better answers',
                ),
                MessagesPlaceholder(self.memory_key),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )

    @property
    def tools(self):
        """Adiciona ferramentas para amplificar as capacidades do agente."""
        tools = []

        return tools

    # Criar modelo de chat do Gemini
    def init_gemini_model(self, model_name='gemini-2.5-flash', **kwargs) -> None:
        """Instancia um modelo de chat Gemini e o registra para o agente.

        Args:
            model_name (str, optional): Nome do modelo a ser usado. Padrão: 'gemini-2.5-flash'.
            temperature (int, optional): Temperatura usada no modelo.

        Raises:
            APIKeyNotFoundException: levantada quando nenhuma chave de API estiver presente."""
        if not self.gemini_key:
            raise APIKeyNotFoundException(
                'Your Gemini API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGoogleGenerativeAI(
            model=model_name, google_api_key=self.gemini_key, **kwargs
        )
        self.model_name, self.provider = model_name, 'google'

        return

    # Criar modelo de chat do Groq
    def init_groq_model(self, model_name='qwen/qwen3-32b', **kwargs) -> None:
        """Instancia um modelo de chat Groq e o registra para o agente.

        Args:
            model_name (str, optional): Nome do modelo a ser usado. Padrão: 'qwen/qwen3-32b'.
            temperature (int, optional): Temperatura usada no modelo.

        Raises:
            APIKeyNotFoundException: levantada quando nenhuma chave de API estiver presente."""
        if not self.groq_key:
            raise APIKeyNotFoundException(
                'Your Groq API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGroq(model_name=model_name, api_key=self.groq_key, **kwargs)
        self.model_name, self.provider = model_name, 'groq'

        return

    def _init_default_llm(self, task_type: ModelTask):
        """Instancia um modelo LLM predefinido quando necessário, com base nas chaves de API disponíveis.

        Args:
            task_type (ModelTask): O tipo de tarefa para instanciar o modelo recomendado.
        """

        try:
            groq_model_name = TASK_PREDEFINED_MODELS['groq'][task_type]
            gemini_model_name = TASK_PREDEFINED_MODELS['google'][task_type]
        except KeyError:
            groq_model_name = TASK_PREDEFINED_MODELS['groq'][ModelTask.DEFAULT]
            gemini_model_name = TASK_PREDEFINED_MODELS['google'][ModelTask.DEFAULT]

        if self.groq_key:
            self.init_groq_model(groq_model_name, temperature=0)
        elif self.gemini_key:
            self.init_gemini_model(gemini_model_name, temperature=0)
        else:
            raise APIKeyNotFoundException

    def _get_session_memory(self, session_id: str):
        """Instancia um armazenamento de memória local para o agente.

        Args:
            session_id (str): Identificador para o arquivo de sessão do usuário."""
        # Criar um arquivo temporário para armazenar a memória de cada sessão, diretório apagado a cada reinício do container ou do sistema.
        temp = tempfile.gettempdir()
        history_file = os.path.join(temp, session_id + '_history.json')

        history = FileChatMessageHistory(history_file, encoding='utf-8')

        memory = ConversationBufferWindowMemory(
            chat_memory=history,
            memory_key=self.memory_key,
            input_key='input',
            output_key='output',
            return_messages=True,
            k=10,
        )

        return memory

    # instanciar um modelo com base na chave de API e um agente
    def initialize_agent(
        self,
        task_type: ModelTask = ModelTask.DEFAULT,
        tools: list[BaseTool] = None,
        prompt: ChatPromptTemplate | None = None,
        *,
        session_id: str | None = None,
        memory: BaseMemory | None = None,
        verbose: bool = DEBUG_MODE,
    ):
        """Instancia um agente usando as opções definidas. Deve ser usado após modificar o objeto LLM.

        Args:
            task_type (ModelTask, optional): O tipo de tarefa para instanciar o modelo recomendado. Se vazio, instancia um modelo genérico.
            tools (any, optional): Ferramentas para o agente, se for None, o conjunto padrão de ferramentas é usado.
            prompt (ChatPromptTemplate | None, optional): Template de prompt usado no agente, se for None, o template padrão é usado.
            session_id (str | None, optional): Identificador de sessão para separar memória do agente. Necessário ser passado para criar instancia de memória.
            memory (BaseMemory | None, optional): Instância de memória usada para o agente, se for None, usa a ConversationBufferWindowMemory padrão:

            ```ConversationBufferWindowMemory(
            chat_memory=history,
            memory_key=self.memory_key,
            input_key='input',
            output_key='output',
            return_messages=True,
            k=10,
        )
            ```
            verbose (bool, optional): Se o agente imprimirá suas ações no console.

        Raises:
            APIKeyNotFoundException: se nenhuma chave de API for fornecida para iniciar um LLM."""
        if not self._llm:
            self._init_default_llm(task_type)

        # Criar um agente com função de tool calling
        agent = create_tool_calling_agent(
            self._llm, tools=tools or self.tools, prompt=prompt or self.prompt
        )

        # Se nenhuma memória disponível e id de sessão recebido, adicionar memória de conversação ao agente
        if session_id and not memory:
            memory = self._get_session_memory(session_id)

        # Criar um ciclo de execução para o agente executar suas ferramentas
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools or self.tools,
            memory=memory,
            max_iterations=7,
            verbose=verbose,
        )

    def get_model_info(self):
        if not self._llm:
            raise ModelNotFoundException

        return (self.model_name, self.provider)

    def run(self, user_input, **kwargs):
        if not self.agent:
            raise ExecutorNotFoundException()

        return self.agent.invoke({'input': user_input, **kwargs})

    async def arun(self, user_input, **kwargs):
        if not self.agent:
            raise ExecutorNotFoundException()

        return await self.agent.ainvoke({'input': user_input, **kwargs})
