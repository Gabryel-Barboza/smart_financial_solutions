"""Ferramentas para o agente de geração de relatórios."""

import io
import re

import requests
from langchain.tools import tool
from markdown_pdf import MarkdownPdf, Section

from src.settings import settings

N8N_WEBHOOK = settings.n8n_webhook


async def _send_report(recipient_email: str, filename: str, report_file):
    """Envia o relatório para o email do usuário recebido."""

    # Padrão: início (^) com um ou mais caracteres ([...]+) alfanuméricos ou símbolos específicos ([...]), seguido de um @ e mais caracteres. Depois um ponto e por fim uma quantidade mínima de dois caracteres ({2,}) no final ($).
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_email = re.fullmatch(email_pattern, recipient_email)

    if not is_email:
        return {
            'error': f'Invalid email received: {recipient_email}. Try again with a valid email (e.g. email32@email.com).'
        }

    file = (filename, report_file, 'application/pdf')

    response = requests.post(
        N8N_WEBHOOK,
        data={'recipient_email': recipient_email},
        files={'file': file},
    )

    if response.ok:
        return {
            'results': f'Email sent to {recipient_email}! The user should check the inbox, as the email will arrive soon.'
        }

    return {'error': 'An error occurred when sending the report.'}


@tool
async def create_and_send_report(filename: str, content: str, recipient_email: str):
    """This tool should be used for creating the report as a PDF file and sending the document to the user. The input is the file name (lowercase), content of the report in **markdown** and the user email."""
    # Geração do PDF
    try:
        # Criação do pdf e table of contents de nível 2
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(content))

        pdf_buffer = io.BytesIO()
        pdf.save(pdf_buffer)
        pdf_buffer.seek(0)

    except Exception as e:
        print(e)
        return {'error': 'Failed to generate the PDF document'}

    # Envio do relatório
    try:
        return await _send_report(recipient_email, filename, pdf_buffer)
    except requests.exceptions.RequestException as e:
        print(e)
        return {'error': 'Failed when connecting to the email service'}
