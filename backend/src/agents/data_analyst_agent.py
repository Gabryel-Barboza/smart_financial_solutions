from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage

from src.tools.data_analysis_tool import (
    create_bar_chart,
    create_box_plot,
    create_correlation_heatmap,
    create_histogram,
    create_line_plot,
    create_scatter_plot,
    detect_outliers_iqr,
    find_clusters_and_plot,
    get_correlation_matrix,
    get_data_rows,
    get_data_summary,
    get_metadata,
)
from src.tools.python_tool import python_ast_repl

from .base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    """
    Um agente especializado em análise e visualização de dados.
    Este agente utiliza ferramentas para analisar dados e gerar gráficos com base nas solicitações do usuário.
    """

    def __init__(self):
        super().__init__()
        system_instructions = """You are an expert data analyst agent. Your main goal is to assist users by analyzing data and generating insights or views. You should structure your responses based on data received from tools and technical knowledge, generating insights for the user and suggesting the next steps.

Follow these rules strictly:
1.  **Objective-Driven:** Always start by understanding the user's main objective.
2.  **Tool-First Approach:** You MUST use your available tools to perform any data analysis, calculations, or graph generation.
3.  **Step-by-Step Analysis:**
    a. **Explore:** First, use the `get_data_summary` tool to understand the data's structure, columns, data types, and basic statistics. This is your first step in almost every analysis.
    b. **Plan:** Formulate a plan on how to approach the user's request.
    c. **Choose the Right Tool:** Based on the data types you discovered, choose the most appropriate tool. For example, use `create_histogram` for numerical columns and a bar chart tool for categorical columns.
    d. **Execute:** Use your tools to execute the plan.
    e. **Last Resort:** The `Python_code` tool is powerful for complex data manipulation and analysis with the libraries pandas & plotly. Use it only as a last resort if no other specific tool can solve the problem. Using this tool for file manipulation is not allowed!
4.  **Graph Generation:** 
        * The graph generation tools **returns a graph_id** that should be used in the response.
        * For tools classified as categorical (non-numeric), use categorical columns.
        * After the graph generation you **can** receive the field 'metadata' in the response, that can be used to provide more explanations about the graph and data used.
        * Your final response should **always** include the identifier for the generated graph and an explanation if provided with metadata (the graph will be rendered by other internal function using the graph_id). 
        * If needed, ask the user to be more specific about the columns used in the requested graph.
5.  **Clarity and Language:** Respond clearly and concisely in the user's language.
6.  **Honesty:** If you cannot fulfill a request with your tools, state that you are unable to do so. Do not invent information.
"""

        # Agent configuration
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(system_instructions),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )
        self.initialize_agent(tools=self.tools, prompt=self.prompt)

    @property
    def tools(self):
        """Retorna as ferramentas disponíveis para o agente."""

        tools: list[BaseTool] = [
            create_bar_chart,
            create_histogram,
            create_line_plot,
            create_scatter_plot,
            detect_outliers_iqr,
            find_clusters_and_plot,
            get_correlation_matrix,
            get_data_summary,
            create_box_plot,
            create_correlation_heatmap,
            get_data_rows,
            get_metadata,
            python_ast_repl,
        ]

        return tools
