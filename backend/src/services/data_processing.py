"""Serviço para processamento de dados recebidos via upload."""

import zipfile
from io import BytesIO

import pandas as pd
import pytesseract
from fastapi import UploadFile
from PIL import Image

from src.controllers.websocket_controller import manager
from src.data import StatusUpdate
from src.utils.exceptions import WrongFileTypeError

df: pd.DataFrame | None = None


def get_dataframe():
    """Retorna o DataFrame global do pandas em uso."""
    return df


class DataHandler:
    """
    Manipulador de Dados (DataHandler).
    Gerencia o carregamento de dados e o preenchimento do DataFrame.
    Uma instância desta classe pode ser usada para carregar um conjunto de dados
    a partir de um arquivo CSV ou ZIP.
    """

    def __init__(self):
        pass

    async def load_csv(
        self,
        session_id: str,
        data: UploadFile,
        separator: str = ',',
        header: int = 0,
    ) -> bool:
        """
        Carrega dados de um arquivo enviado (CSV ou ZIP contendo um CSV)
        para um DataFrame do pandas. Injeta os dados na variável global df.

        Args:
            data (UploadFile): Arquivo a ser lido.
            separator (str, optional): Separador do CSV. Padrão é ','.
            header (int, optional): Linha dos cabeçalhos. Padrão é 0.

        Raises:
            WrongFileTypeError: Quando o tipo de arquivo recebido não é suportado.

        Returns:
            bool: True se a leitura foi bem-sucedida.
        """
        global df

        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_INIT)

        file = await data.read()
        file_bytes = BytesIO(file)

        if data.content_type == 'application/zip':
            df = await self._load_zip(session_id, file_bytes, separator, header)

        elif data.content_type in ['text/csv', 'application/vnd.ms-excel']:
            df = pd.read_csv(file_bytes, sep=separator, header=header)

        else:
            raise WrongFileTypeError(
                f'Unsupported file type: {data.content_type}. '
                'Please upload a CSV or a ZIP file containing a CSV.'
            )

        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_FINISH)
        # Retorna as primeiras linhas do DataFrame em formato JSON para pré-visualização
        return df.head().to_json()

    async def _load_zip(self, session_id: str, file: BytesIO, sep: str, header: int):
        """
        Função auxiliar para ler arquivos ZIP, descompactar e retornar o DataFrame resultante.

        Args:
            file (BytesIO): O arquivo ZIP em memória.
            sep (str): Separador do CSV.
            header (int): Linha dos cabeçalhos.

        Raises:
            FileNotFoundError: Quando nenhum arquivo CSV é encontrado após a descompactação.

        Returns:
            DataFrame: O DataFrame resultante da leitura.
        """
        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_ZIP)

        with zipfile.ZipFile(file) as zip_file:
            # Encontra o primeiro arquivo que termina com '.csv' dentro do zip
            csv_filename = next(
                (name for name in zip_file.namelist() if name.endswith('.csv')),
                None,
            )

            if not csv_filename:
                raise FileNotFoundError('No CSV file found in the zip archive.')

            with zip_file.open(csv_filename) as csv_file:
                return pd.read_csv(csv_file, sep=sep, header=header)

    async def read_uploaded_image(self, session_id: str, image_file: UploadFile):
        """Realiza a leitura de imagens utilizando a OCR open-source Tesseract.

        Args:
            image_file (UploadFile): arquivo com a imagem para realizar a leitura.

        Raises:
            WrongFileTypeError: levantada quando o arquivo recebido não é compatível.

        Returns:
            text (str): string com o texto identificado na imagem.
        """
        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_INIT)
        try:
            file_type = image_file.content_type.split('image/')[1]
            supported_types = ('jpeg', 'png', 'tiff', 'bmp')

            if file_type not in supported_types:
                raise WrongFileTypeError(
                    f'Unsupported file type received: .{file_type}! Supported file types: {" ".join([f".{type}" for type in supported_types])}'
                )

            image = await image_file.read()
            image_bytes = BytesIO(image)

            text = 'The following text has been extracted from an image, try to identify its context and return a response in Brazilian Portuguese. If its related to invoice data, create an analysis about it, if not return a simple response.\n\n'
            await manager.send_status_update(session_id, StatusUpdate.UPLOAD_IMAGE)
            with Image.open(image_bytes) as img:
                text += pytesseract.image_to_string(img, lang='por+eng')

        except Exception as exc:
            print(exc)
            raise

        return text
