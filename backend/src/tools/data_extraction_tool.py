from langchain.tools import tool

from src.schemas import PayloadDataModel
from src.services.vector_store_services import QdrantStore

qdrant_store = QdrantStore()


class DataExtractionTools:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.data_collection_name = 'user_data_collection'

    def _add_session_to_data(session_id: str):
        """Gera um 'callable' para injetar o 'session_id' no metadata de cada chunk de dados.

        Este 'callable' é usado na função map() antes da inserção no Vector Store.

        Args:
        session_id (str): Identificador da sessão atual.

        Returns:
            Callable (item[PayloadDataModel]): Uma função que recebe um chunk de dados e injeta o 'session_id' em 'metadata'.
        """

        def join_session_id(item: PayloadDataModel):
            item['metadata']['user_id'] = session_id

            return item

        return join_session_id

    async def create_data_extraction_tools(self):
        """Função para criar e retornar as ferramentas de extração do agente."""

        @tool('qdrant_data_insert')
        async def insert_data(data: list[dict]):
            """
            Stores structured data chunks and their embeddings into the Qdrant Vector Store.

            Expects a string list of dictionaries where each dictionary contains:
            - 'text': The text chunk from the fiscal document (e.g., an item line, a section).
            - 'metadata': A dictionary with structured fields (CNPJ, TotalValue, Date, etc.).

            Returns success confirmation.
            """

            ids = await qdrant_store.store_data(
                self.data_collection_name,
                data,
                self._add_session_to_data(self.session_id),
            )

            return {'results': f'Data inserted successfully! {ids}'}

        @tool('extract_data')
        async def extract_data(query: str):
            """
            Searches for tax documents in Qdrant by vector similarity with the provided query.

            Args:
                query (str): The natural language search query.

            Returns:
                dict: The search results from the Vector Store.
            """

            data = await qdrant_store.search_documents(
                self.data_collection_name, self.session_id, query
            )

            return {'results': data}

        # @tool('extract_filtered_data')
        # async def extract_filtered_data():
        #     return {'results': ''}

        return [insert_data, extract_data]

    async def cleanup(self):
        await qdrant_store.delete_collection_data(
            self.data_collection_name, self.session_id
        )
