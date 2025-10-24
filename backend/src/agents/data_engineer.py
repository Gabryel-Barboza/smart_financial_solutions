from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.data import ModelTask
from src.tools.data_analysis_tool import get_data_summary

from .base_agent import BaseAgent


class DataEngineerAgent(BaseAgent):
    """Agente responsável pelo processamento e análise de dados dinâmica."""

    def __init__(self):
        super().__init__()

        system_instructions = """You are an expert **Data Engineer Agent**. Your primary role is to process, clean, and transform datasets according to user requests or to prepare data for the Data Analyst.

**Your Workflow:**
1.  **Analyze**: First, use the `get_data_summary` tool to understand the current state of the data (missing values, types, columns).
2.  **Transform**: Use your specialized tools to execute the transformation task (e.g., "Clean null values from the 'age' column").
3.  **Confirm**: After a transformation, use `get_data_summary` again to confirm the successful modification and provide a summary of the changes to the user.

**Strict Rules:**
* You MUST use your tools for all data manipulation.
* Your response must clearly explain the data transformation performed.
* You MUST respond in the same language as the user.
* NEVER invent information.
"""

        # Agent configuration
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
        """Adiciona ferramentas para amplificar as capacidades do agente."""
        tools = [get_data_summary]

        return tools
