"""Ferramenta para execução de código Python."""

import pandas as pd
import plotly.express as px
from langchain.tools import Tool
from langchain_experimental.tools import PythonAstREPLTool

from src.services.data_processing import session_manager
from src.tools.data_analysis_tool import _save_graph_to_db

python_ast_repl = Tool(
    name='Python_code',
    func=PythonAstREPLTool(
        locals={
            'get_dataframe': session_manager.get_df,
            '_save_graph_to_db': _save_graph_to_db,
            'pd': pd,
            'px': px,
        }
    ),
    description="""Executes Python code in a secure environment. Use this tool for complex tasks requiring data processing, statistics, or custom DataFrame manipulation, such as filtering, grouping, complex calculations, or graph generation.
You have access to the following.
    pd: Pandas.
    px: Plotly Express.
    get_dataframe(): retrieve the current dataframe data.
    _save_graph_to_db(fig, metadata): save a Plotly figure.
Mandatory Execution Steps:
LOAD DATA: start your code by loading the data into a variable named df:
df = get_dataframe()
if df is None or df.empty:
    # Stop execution if data is missing
    ...
* CALCULATIONS: For analysis, use print() to return results. Keep the output small and concise for efficiency; avoid printing large DataFrames.
* Graph Generation Protocol:
To create a graph, follow these steps:
    * Generate Figure.
    * Generate Metadata: create a concise, textual summary of the graph (include stats from dataframe if possible for better understanding, be efficient in the data returned).
    * Save Figure: Call the required saving function and print metadata for analysis:
    print(_save_graph_to_db(fig, metadata), metadata)
The function's output (graph_id, metadata) will be returned to you.""",
)
