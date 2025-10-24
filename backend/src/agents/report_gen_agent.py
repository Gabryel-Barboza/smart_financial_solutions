from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.agents import BaseAgent
from src.data import ModelTask
from src.tools.report_gen_tool import create_and_send_report


class ReportGenAgent(BaseAgent):
    """Agente de criação de relatórios profissionais e documentos."""

    def __init__(self):
        super().__init__()

        system_instructions = """You are a **professional report writer** responsible for writing the report in a formal but friendly language for better understanding of the information.
You will receive a detailed request in the 'input' that contains the report type, the data for analysis, and possibly an email for delivery. If no data is received, return a response requiring the data.

**Workflow:**
1.  **Analyze Input:** Carefully read the entire input string to identify the core data and the email recipient (if available).
2.  **Draft Report:** Draft the professional report (as a markdown string) based on the supplied data, finding key points, action items, and clear insights.
3.  **Use Tool:** Use the `create_report_document` tool, passing a **file name** in lowercase, the **entire drafted report string** and the **email address**. If no email is available you can return the draft to the user directly instead.
4.  **Final Response:** Your final response to the user is the output returned by the tool.

**Strict Rules**
* Never invent information. Use only what is available and technical knowledge.
* Create the report using Brazilian portuguese language.
"""
        self.prompt = ChatPromptTemplate(
            [
                SystemMessage(system_instructions),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )

        self.initialize_agent(
            task_type=ModelTask.REPORT_GENERATION, tools=self.tools, prompt=self.prompt
        )

    @property
    def tools(self):
        """Adiciona ferramentas para amplificar as capacidades do agente."""
        tools = [create_and_send_report]

        return tools
