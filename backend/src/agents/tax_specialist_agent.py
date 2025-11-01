from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage

from src.data import ModelTask
from src.tools.data_extraction_tool import DataExtractionTools

from .base_agent import BaseAgent


class TaxSpecialistAgent(BaseAgent):
    """Agente especialista responsável por cálculos e validação de impostos."""

    def __init__(
        self, tools: list[BaseTool], *, current_session: dict[str, BaseAgent | str]
    ):
        self._tools = tools

        gemini_key = current_session.get('gemini_key')
        groq_key = current_session.get('groq_key')

        super().__init__(gemini_key=gemini_key, groq_key=groq_key)
        system_instructions = """You are a **specialist taxes calculator and documents validator** that checks if taxes are properly applied based on Brazil's legislation and taxes documents (e.g.: nf-e, ct-e, DANFE, DACTE...).

"""
        self.prompt = ChatPromptTemplate(
            [
                SystemMessage(system_instructions),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )
        self.initialize_agent(
            task_type=ModelTask.DATA_TREATMENT,
            tools=self.tools,
            prompt=self.prompt,
        )

    @property
    def tools(self):
        """Função para amplificar as capacidades do agente."""

        return self._tools

    @classmethod
    async def create(cls, session_id: str, current_session: dict[str, BaseAgent | str]):
        extract_tools = DataExtractionTools(session_id)
        _, extract_data = await extract_tools.create_data_extraction_tools()

        return cls([extract_data], current_session=current_session)
