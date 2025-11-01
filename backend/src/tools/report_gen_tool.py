"""Ferramentas para o agente de geração de relatórios."""

import asyncio
import base64
import io
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain.tools import tool
from markdown_pdf import MarkdownPdf, Section

from src.agents.base_agent import BaseAgent
from src.services.db_services import get_graph_db
from src.settings import settings


def _send_report(recipient_email: str, filename: str, report_file: io.BytesIO):
    """Envia o relatório para o email do usuário recebido."""

    sender_email = settings.sender_email
    sender_password = settings.sender_password

    if not (sender_email and sender_password):
        print('\t>> No credentials found for email sender function.')
        return {'error': 'Email sender deactivated.'}

    if not recipient_email:
        return {'error': 'No email received from the user!'}

    if not filename.endswith('.pdf'):
        filename += '.pdf'

    email = MIMEMultipart('alternative')
    email['From'] = sender_email
    email['To'] = recipient_email
    email['Subject'] = 'Envio automático de relatório PDF - Smart Financial Solutions'

    # Corpo do email
    plain_body = f'Relatório Concluído! 📄 Olá! Seu relatório **{filename}** foi gerado com sucesso e está anexado abaixo. Obrigado por usar nossos serviços automatizados Atenciosamente, Smart Financial Solutions'

    html_body = f"""
<html>
<head></head>
<body>
    <h1>Relatório Concluído! 📄</h1>

    <p>Olá!</p>
    <p>Seu relatório <strong>{filename}</strong> foi gerado com sucesso e está anexado abaixo.</p>
    <p>Obrigado por usar nossos serviços automatizados.</p>

    <p><em>Atenciosamente,</em><br>
    <span style="font-weight: bold; color: blue;">Smart Financial Solutions</span></p>
</body>"""

    email.attach(MIMEText(plain_body, 'plain'))
    email.attach(MIMEText(html_body, 'html'))

    # Anexar arquivo PDF
    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(report_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={filename}')
    email.attach(attachment)

    # Enviar email
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(sender_email, sender_password)
        servidor.send_message(email)
        servidor.quit()

        return {'results': 'Email sent successfully!'}

    except smtplib.SMTPAuthenticationError:
        return {
            'error': 'SMTP authentication failed. Check sender email/password or App Password.'
        }

    except smtplib.SMTPConnectError:
        return {'error': 'Failed to connect to SMTP server: smtp.gmail.com .'}

    except Exception as e:
        print(f'An error occurred when sending the report: {str(e)}')

        return {'error': 'An error occurred when sending the report.'}


async def _replace_with_images(content: str):
    """
    Procura por placeholders de markdown [texto](graph_id:[UUID]) e os substitui
    por referências a arquivos de imagem.

    Args:
        content (str): Conteúdo original para substituir.

    Returns:
        content (str): Retorna o conteúdo Markdown modificado.
    """

    # Regex para capturar o texto e o UUID dentro do graph_id
    pattern = r'\[(.*?)\]\(graph_id:([a-z0-9-]+)\)'

    modified_content = content

    # Encontra todas as ocorrências
    matches = list(re.finditer(pattern, content))

    # Processa cada match de trás para frente para evitar problemas de índice
    for match in reversed(matches):
        image_alt_text = match.group(1)
        graph_id = match.group(2)

        try:
            graph_data = await asyncio.to_thread(get_graph_db, graph_id, image=True)

            if not graph_data:
                continue

            image64 = base64.b64encode(graph_data).decode('utf-8')

            # Substitui o placeholder por uma tag de imagem Markdown
            new_image_tag = f'![{image_alt_text}](data:image/png;base64,{image64})'

            # Substitui a ocorrência no conteúdo
            modified_content = (
                modified_content[: match.start()]
                + new_image_tag
                + modified_content[match.end() :]
            )

        except Exception as e:
            print(f'Erro ao processar gráfico {graph_id}: {e}. Mantendo placeholder.')
            continue

    return modified_content


async def _create_and_send_report(filename: str, content: str, recipient_email: str):
    if not recipient_email:
        return {'error': 'No email found, please register an email first'}

    if not content:
        return {'error': 'No content found for generating the report.'}

    content = await _replace_with_images(content)

    # Geração do PDF
    try:
        # Criação do pdf e table of contents de nível 2
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(content))

        pdf_buffer = io.BytesIO()
        pdf.save(pdf_buffer)
        pdf_buffer.seek(0)

        # Envio do relatório
        return await asyncio.to_thread(
            _send_report, recipient_email, filename, pdf_buffer
        )

    except Exception as exc:
        print(f'Error when generating the report: {exc}')

        return {'error': 'Failed to generate the PDF document'}


def create_report_tools(current_session: dict[str, BaseAgent | str]):
    """Função para criação das ferramentas com injeção de dependências.

    Args:
        current_session (dict[str, BaseAgent | str]): Sessão do usuário atual.

    Returns:
        list (Tool): Lista de ferramentas do agente.
    """

    @tool('create_and_send_report')
    async def create_and_send_report(filename: str, content: str):
        """This tool should be used for creating the report as a PDF file and sending the document to the user. The input is the file name (lowercase) and content of the report in **markdown**."""

        recipient_email = current_session.get('user_email')

        return await _create_and_send_report(filename, content, recipient_email)

    return [create_and_send_report]
