"""Serviço para processamento de dados recebidos via upload."""

import asyncio
import zipfile
from io import BytesIO
from time import time

import pandas as pd
import pytesseract
from fastapi import UploadFile
from PIL import Image

from src.controllers.websocket_controller import manager
from src.data import StatusUpdate
from src.utils.exceptions import WrongFileTypeError


class SessionManager:
    """Gerenciador de sessão para armazenar os dados de análise do usuário."""

    def __init__(self):
        self.dataframes: dict[str, dict[str, pd.DataFrame | int]] = {}

    async def get_df(self, session_id: str) -> pd.DataFrame | None:
        """Recupera um DataFrame do Pandas na sessão atual.

        Args:
            session_id (str): Identificador da sessão atual.

        Returns:
            pd.DataFrame: DataFrame recuperado da sessão.
        """
        dataframe = self.dataframes.get(session_id)

        if dataframe:
            dataframe['timestamp'] = time()

            return dataframe.get('df')

        return None

    async def insert_df(self, session_id: str, df: pd.DataFrame) -> None:
        """Insere um DataFrama do Pandas na sessão atual.

        Args:
            session_id (str): Identificador da sessão atual.
            df (pd.DataFrame): DataFrame para inserção na sessão.
        """

        self.dataframes[session_id] = {'df': df, 'timestamp': time()}

    async def cleanup_task(self, interval: int = 300, ttl: int = 600):
        """Função de limpeza para dados, removendo DataFrames não mais utilizados.

        Args:
            interval (int, optional): Intervalo de tempo para checar a pool, em segundos.
            ttl (int, optional): Tempo de vida máximo de um agente na pool, em segundos.
        """
        time_now = time()
        delete_list = []

        print(
            f'\t>> Initializing cleanup task for data. Checking for expired objects (last access > {ttl}s) with intervals of {interval}s.'
        )

        while True:
            try:
                await asyncio.sleep(interval)

                for session_id, dataframe in self.dataframes.items():
                    if time_now - dataframe['timestamp'] > ttl:
                        delete_list.append(session_id)

                if delete_list:
                    print(f'\t>> Cleaning unused objects: {len(delete_list)} in total')
                    for session_id in delete_list:
                        del self.dataframes[session_id]

            except Exception as exc:
                print(f'\t>> Error in DataFrame cleanup task: {exc}')
                asyncio.sleep(interval)


session_manager = SessionManager()


class DataHandler:
    """
    Manipulador de Dados (DataHandler).
    Gerencia o carregamento de dados e o preenchimento do DataFrame.
    Uma instância desta classe pode ser usada para carregar um conjunto de dados
    a partir de um arquivo CSV ou ZIP.
    """

    def __init__(self):
        pass

    async def load_data(
        self,
        session_id: str,
        data: UploadFile,
        separator: str = ',',
        header: int = 0,
    ) -> bool:
        """
        Carrega dados de um arquivo enviado (XLSX, CSV ou ZIP contendo um CSV)
        para um DataFrame do pandas. Injeta os dados na sessão atual.

        Args:
            data (UploadFile): Arquivo a ser lido.
            separator (str, optional): Separador do CSV. Padrão é ','.
            header (int, optional): Linha dos cabeçalhos. Padrão é 0.

        Raises:
            WrongFileTypeError: Quando o tipo de arquivo recebido não é suportado.

        Returns:
            bool: True se a leitura foi bem-sucedida.
        """

        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_INIT)

        file = await data.read()
        file_bytes = BytesIO(file)

        if data.content_type == 'application/zip':
            df = await self._load_zip(session_id, file_bytes, separator, header)

        elif data.content_type == 'text/csv':
            # Recursos síncronos são executados em Thread separada para manter assincronia
            def sync_read_csv():
                return pd.read_csv(file_bytes, sep=separator, header=header)

            df = await asyncio.to_thread(sync_read_csv)

        elif data.content_type == 'application/vnd.ms-excel':

            def sync_read_excel():
                return pd.read_excel(file_bytes, header=header)

            df = await asyncio.to_thread(sync_read_excel)

        else:
            raise WrongFileTypeError(
                f'Unsupported file type: {data.content_type}. '
                'Please upload a XLSX, CSV or ZIP file containing a CSV.'
            )

        await session_manager.insert_df(session_id, df)
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
            df (DataFrame): O DataFrame resultante da leitura.
        """
        await manager.send_status_update(session_id, StatusUpdate.UPLOAD_ZIP)

        def sync_read_zip():
            with zipfile.ZipFile(file) as zip_file:
                # Encontra o primeiro arquivo que termina com '.csv' ou '.xlsx' dentro do zip
                filename = next(
                    (
                        name
                        for name in zip_file.namelist()
                        if name.endswith(('.csv', '.xlsx'))
                    ),
                    None,
                )

                if not filename:
                    raise FileNotFoundError(
                        'No CSV or XLSX file found in the zip archive.'
                    )

                if filename.endswith('.csv'):
                    with zip_file.open(filename) as csv_file:
                        return pd.read_csv(csv_file, sep=sep, header=header)

                elif filename.endswith('.xlsx'):
                    with zip_file.open(filename) as xlsx_file:
                        return pd.read_excel(xlsx_file, header=header)

        return await asyncio.to_thread(sync_read_zip)

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

            text = 'The following text has been extracted from an image, try to identify its context and return a response in Brazilian Portuguese, including parts of the text when applicable. If its related to invoice data, create an analysis about it, if not return a simple response.\n\n'

            await manager.send_status_update(session_id, StatusUpdate.UPLOAD_IMAGE)

            image = await image_file.read()
            image_bytes = BytesIO(image)

            def sync_read_img():
                with Image.open(image_bytes) as img:
                    return pytesseract.image_to_string(img, lang='por+eng')

            text += await asyncio.to_thread(sync_read_img)

        except Exception as exc:
            print(exc)
            raise

        return text
