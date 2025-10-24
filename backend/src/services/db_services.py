"""Serviço para manipulação do banco de dados"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

from src.settings import settings
from src.utils.exceptions import DatabaseFailedException

# Cria o motor de conexão com o banco de dados usando a URI das configurações
engine = create_engine(settings.database_uri)


def execute_query(
    user_query: str,
    parameters: dict[str, any] | None = None,
    commit: bool = False,
) -> Result:
    """
    Executa uma consulta SQL no banco de dados.

    Args:
        user_query: A string da consulta SQL a ser executada.
        parameters: Um dicionário de parâmetros para ligar (bind) à consulta.
        commit: Se True, efetua o commit da transação após a execução.

    Returns:
        O objeto Result retornado pelo SQLAlchemy.

    Raises:
        SQLAlchemyError: Se ocorrer qualquer erro de banco de dados.
    """

    try:
        # Abre uma conexão com o motor do banco de dados
        with engine.connect() as conn:
            query = text(user_query)
            result = conn.execute(query, parameters)

            if commit:
                conn.commit()
            return result
    except SQLAlchemyError as e:
        print(f'Database query failed: {e}')
        raise


def init_db() -> None:
    """Inicializa o banco de dados criando a tabela 'charts' se ela não existir."""

    query = """\
    CREATE TABLE IF NOT EXISTS charts(
    uuid VARCHAR(36) PRIMARY KEY,
    graph_json JSON,
    metadata VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """

    try:
        # Executa a query de criação da tabela
        execute_query(query)
        print('\t>> Database initialized successfully.')
    except SQLAlchemyError as e:
        # Captura e relança exceção de falha na inicialização
        print(f'Failed to initialize database: {e}')
        raise DatabaseFailedException


def get_graph_db(graph_id: str) -> str | None:
    """
    Recupera o JSON do gráfico para um determinado ID.

    Args:
        graph_id: O UUID do gráfico a ser recuperado.

    Returns:
        Os dados do gráfico como uma string JSON, ou None se não for encontrado.
    """

    query = 'SELECT graph_json FROM charts WHERE "uuid" = :graph_id LIMIT 1'
    try:
        # Executa a consulta e retorna o resultado escalar
        result = execute_query(query, {'graph_id': graph_id})
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        # Em caso de erro, levanta a exceção customizada
        raise DatabaseFailedException


def get_graph_metadata(graph_id: str) -> str | None:
    """
    Recupera os metadados para um determinado ID de gráfico.

    Args:
        graph_id: O UUID do gráfico para o qual recuperar os metadados.

    Returns:
        Os metadados como uma string, ou None se não forem encontrados.
    """

    query = 'SELECT metadata FROM charts WHERE "uuid" = :graph_id LIMIT 1;'
    try:
        # Executa a consulta e retorna o resultado escalar
        result = execute_query(query, {'graph_id': graph_id})
        return result.scalar_one_or_none()
    except SQLAlchemyError:
        raise DatabaseFailedException


def insert_graphs_db(
    graph_id: str, graph_json: str, metadata: str | None = None
) -> None:
    """Insere um novo registro de gráfico no banco de dados."""

    query = 'INSERT INTO charts ("uuid", "graph_json", "metadata") VALUES (:graph_id, :graph_json, :metadata)'
    params = {'graph_id': graph_id, 'graph_json': graph_json, 'metadata': metadata}

    execute_query(query, params, commit=True)
