"""Serviço para processamento de dados recebidos via upload."""

import zipfile
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

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
        file = await data.read()
        file_bytes = BytesIO(file)

        if data.content_type == 'application/zip':
            df = await self._load_zip(file_bytes, separator, header)

        elif data.content_type in ['text/csv', 'application/vnd.ms-excel']:
            df = pd.read_csv(file_bytes, sep=separator, header=header)

        else:
            raise WrongFileTypeError(
                f'Unsupported file type: {data.content_type}. '
                'Please upload a CSV or a ZIP file containing a CSV.'
            )

        # Retorna as primeiras linhas do DataFrame em formato JSON para pré-visualização
        return df.head().to_json()

    async def _load_zip(self, file: BytesIO, sep: str, header: int):
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
