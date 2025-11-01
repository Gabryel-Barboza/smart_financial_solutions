from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.data import ModelTask

from .base_agent import BaseAgent


class OutputGuard(BaseAgent):
    """Um agente simples para corrigir erros de saída em respostas de outros agentes."""

    def __init__(self, *, current_session: dict[str, BaseAgent | str]):
        gemini_key = current_session.get('gemini_key')
        groq_key = current_session.get('groq_key')

        super().__init__(gemini_key=gemini_key, groq_key=groq_key)

        system_instructions = """You are an output guard, that is, you will receive response strings from other agents that failed to follow their output schema. Your objective is to parse the string to the output schema provided, while making the sure that the original data remains unaltered. You will receive the validation error after the format instructions too, use it to fix the output response.

**Mandatory Rules**
* Your only output should be the parsed response, no explanations or extra characters allowed!
* Double check if the output is compliant with the format instructions and the rules, parse it again if not.

**Example Workflow**

    **Input**:

The output should be formatted as a JSON instance that conforms to the JSON schema below.

{"properties": {"response": {"description": "Your final answer to the user.", "title": "Response", "type": "string"}, "graph_id": {"anyOf": [{"type": "string"}, {"items": {"type": "string"}, "type": "array"}], "description": "Id of generated graph returned from tools, can be an empty string. Multiple ids can be returned, use a list for that case.", "title": "Graph Id"}}, "required": ["response", "graph_id"]}

Olá! 😊 Tudo bem por aqui. Como posso te ajudar hoje? Se precisar de análise de dados, tratamento de documentos fiscais ou geração de relatórios, estou à disposição!

    **Expected Output**:

{"response": "Olá! 😊 Tudo bem por aqui. Como posso te ajudar hoje? Se precisar de análise de dados, tratamento de documentos fiscais ou geração de relatórios, estou à disposição!", "graph_id": ""}

"""

        self.prompt = ChatPromptTemplate(
            [
                SystemMessage(system_instructions),
                ('system', '{format_instructions}'),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )

        self.initialize_agent(
            task_type=ModelTask.DEFAULT,
            prompt=self.prompt,
            session_id=self.session_id,
        )
