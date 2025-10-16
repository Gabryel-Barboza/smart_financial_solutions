"""Classe base para outros agentes herdarem métodos comuns."""

import os
import tempfile

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.language_models import BaseChatModel
from langchain_core.memory import BaseMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.settings import settings
from src.utils.exceptions import APIKeyNotFoundException, ExecutorNotFoundException


# Agente base para reaproveitamento e herança
class BaseAgent:
    def __init__(
        self,
        llm: BaseChatModel | None = None,
    ):
        self._llm = llm
        self.agent = None
        self.prompt = ChatPromptTemplate(
            [
                (
                    'system',
                    'You are a helpful agent that answers questions, respond to the questions objectively and only when certain, use the tools available to create better answers',
                ),
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
    def init_gemini_model(self, model_name='gemini-1.5-pro', **kwargs) -> None:
        """Instancia um modelo de chat Gemini e o registra para o agente.

        Args:
            model_name (str, optional): Nome do modelo a ser usado. Padrão: 'gemini-1.5-pro'.
            temperature (int, optional): Temperatura usada no modelo.

        Raises:
            APIKeyNotFoundException: levantada quando nenhuma chave de API estiver presente."""
        if not settings.gemini_api_key:
            raise APIKeyNotFoundException(
                'Your Gemini API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGoogleGenerativeAI(
            model=model_name, google_api_key=settings.gemini_api_key, **kwargs
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
        if not settings.groq_api_key:
            raise APIKeyNotFoundException(
                'Your Groq API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGroq(
            model_name=model_name, api_key=settings.groq_api_key, **kwargs
        )
        self.model_name, self.provider = model_name, 'groq'

        return

    def _init_default_llm(self):
        """Instancia um modelo LLM predefinido quando necessário, com base nas chaves de API disponíveis."""

        if settings.groq_api_key:
            self.init_groq_model('qwen/qwen3-32b', temperature=0)
        elif settings.gemini_api_key:
            self.init_gemini_model('gemini-2.5-flash', temperature=0)
        else:
            raise APIKeyNotFoundException

    def _get_session_memory(self, memory_key: str, session_id: str):
        # Criar um arquivo para armazenar a memória de cada sessão, diretório apagado a cada reinício
        temp = tempfile.gettempdir()
        history_file = os.path.join(temp, session_id + '_history.json')

        history = FileChatMessageHistory(history_file, encoding='utf-8')

        memory = ConversationSummaryMemory(
            chat_memory=history,
            memory_key=memory_key,
            input_key='input',
            output_key='output',
            return_messages=True,
            llm=self._llm,
        )

        return memory

    # instanciar um modelo com base na chave de API e um agente
    def initialize_agent(
        self,
        tools: list[BaseTool] = None,
        prompt: ChatPromptTemplate | None = None,
        *,
        session_id: str | None = None,
        memory: BaseMemory | None = None,
        memory_key: str | None = None,
        verbose: bool = True,
    ):
        """Instancia um agente usando as opções definidas. Deve ser usado após modificar o objeto LLM.

        Args:
            tools (any, optional): Ferramentas para o agente, se for None, o conjunto padrão de ferramentas é usado.
            prompt (ChatPromptTemplate | None, optional): Template de prompt usado no agente, se for None, o template padrão é usado.
            session_id (str | None, optional): Identificador de sessão para separar memória do agente. Necessário ser passado se memory_key existir.
            memory (BaseMemory | None, optional): Instância de memória usada para o agente, se for None, usa a ConversationSummarizeMemory padrão:

            ```ConversationSummaryMemory(
                chat_memory=history,
                memory_key=memory_key,
                input_key='input',
                output_key='output',
                return_messages=True,
                llm=self._llm,
            )
            ```
            memory_key (str | None, optional): Chave de memória usada no template de prompt para o histórico de chat, se for None, nenhuma memória será adicionada ao agente.
            verbose (bool, optional): Se o agente imprimirá suas ações no console.

        Raises:
            APIKeyNotFoundException: se nenhuma chave de API for fornecida para iniciar um LLM."""
        if self._llm is None:
            self._init_default_llm()

        # Criar um agente com função de tool calling
        agent = create_tool_calling_agent(
            self._llm, tools=tools or self.tools, prompt=prompt or self.prompt
        )

        # Se chave para histórico da memória, adicionar memória de sumarização ao agente
        if memory_key:
            memory = self._get_session_memory(memory_key, session_id)

        # Criar um ciclo de execução para o agente executar suas ferramentas
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools or self.tools,
            memory=memory,
            max_iterations=7,
            verbose=verbose,
        )

    def get_model_info(self):
        return (self.model_name, self.provider)

    def run(self, user_input):
        if not self.agent:
            raise ExecutorNotFoundException()

        return self.agent.invoke({'input': user_input})
