"""Ferramentas utilitárias para o agente."""

import json
from datetime import datetime

from langchain.tools import tool
from pytz import timezone

TIMEZONE = 'America/Sao_Paulo'


@tool('Date_today')
def get_current_datetime():
    """This tool returns the current date and time in Brazil when called."""
    time_format = '%d/%m/%Y %H:%M:%S'
    now = datetime.now(timezone(TIMEZONE)).strftime(time_format)

    return {'result': now}


@tool('json_output_parser', return_direct=True)
def json_output_parser(response: str, graph_id: str = '') -> str:
    """Use this tool to create a valid JSON output after generating the response and as last step. This function receives the response and graph_id values, the graph_id parameter is optional. A string json formatted output is returned."""

    return json.dumps({'response': response, 'graph_id': graph_id})
