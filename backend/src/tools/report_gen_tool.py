"""Ferramentas para o agente de geração de relatórios."""

import asyncio
import io
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain.tools import tool
from markdown_pdf import MarkdownPdf, Section

from src.agents.base_agent import BaseAgent
from src.settings import settings


def _send_report(recipient_email: str, filename: str, report_file: io.BytesIO):
    """Envia o relatório para o email do usuário recebido."""

    sender_email = settings.sender_email
    sender_password = settings.sender_password

    if not recipient_email:
        return {'error': 'No email received from the user!'}

    email = MIMEMultipart()
    email['From'] = sender_email
    email['To'] = recipient_email
    email['Subject'] = 'Envio automático de relatório PDF - Smart Financial Solutions'

    # Corpo do email
    body = f'Segue em anexo {filename}, arquivo PDF com seu relatório automatizado.'
    email.attach(MIMEText(body, 'plain'))

    # Anexar arquivo PDF
    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(report_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
    email.attach(attachment)

    # Enviar email
    try:
        print('Connecting to SMTP server...')
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(sender_email, sender_password)
        servidor.send_message(email)
        servidor.quit()

        return 'Email sent successfully!'

    except smtplib.SMTPAuthenticationError:
        return {
            'error': 'SMTP authentication failed. Check sender email/password or App Password.'
        }

    except smtplib.SMTPConnectError:
        return {'error': 'Failed to connect to SMTP server: smtp.gmail.com .'}

    except Exception as e:
        print(f'An error occurred when sending the report: {str(e)}')

        return {'error': 'An error occurred when sending the report.'}


async def _create_and_send_report(filename: str, content: str, recipient_email: str):
    if not recipient_email:
        return {'error': 'No email found, please register an email first'}

    # Geração do PDF
    try:
        # Criação do pdf e table of contents de nível 2
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(content))

        pdf_buffer = io.BytesIO()
        pdf.save(pdf_buffer)
        pdf_buffer.seek(0)

    except Exception as exc:
        print(f'Error when generating the report: {exc}')

        return {'error': 'Failed to generate the PDF document'}

    # Envio do relatório
    return await asyncio.to_thread(_send_report, recipient_email, filename, pdf_buffer)


def create_report_tools(current_session: dict[str, BaseAgent | str]):
    """Função para criação das ferramentas com injeção de dependências.

    Args:
        session_id (str): Identificador da sessão atual.
        current_session (dict[str, BaseAgent | str]): Sessão do usuário atual.
    """

    @tool('create_and_send_report')
    async def create_and_send_report(filename: str, content: str):
        """This tool should be used for creating the report as a PDF file and sending the document to the user. The input is the file name (lowercase) and content of the report in **markdown**."""

        recipient_email = current_session.get('user_email')

        return await _create_and_send_report(filename, content, recipient_email)

    return [create_and_send_report]
