import asyncio
from uuid import uuid4

from qdrant_client import AsyncQdrantClient, models

from src.data.embeddings import get_fastembed_embedding
from src.schemas import PayloadDataModel
from src.settings import settings


class QdrantStore:
    """Classe para inicialização e manipulação da vector store."""

    STORE_URL = settings.qdrant_url
    embedder = get_fastembed_embedding()
    embedding_dimension = embedder.embedding_size

    def __init__(self):
        self.client = AsyncQdrantClient(url=self.STORE_URL)

    async def init_store(self, *collection_names: list[str]):
        """Inicializa a Vector Store com as coleções necessárias, é recomendada uma única coleção com os dados separados por ID de usuário no payload para performance.

        Args:
            collection_names (list[str]): Lista com todas as coleções criadas na inicialização.
        """

        for collection_name in collection_names:
            # Criando coleções que serão usadas na busca.
            if collection_name == 'user_data_collection':
                await self.create_collection(
                    collection_name,
                    hnsw_config=models.HnswConfigDiff(m=0, payload_m=16),
                    tenant_index=True,
                )
            else:
                await self.create_collection(collection_name)

        print('\t>> Vector Store initialized with the default collections.')

    async def create_collection(
        self,
        collection_name: str,
        *,
        force_recreate: bool = False,
        hnsw_config: models.HnswConfigDiff | None = None,
        tenant_index: bool = False,
    ):
        """Função para criar coleções no Vector Store com as configurações recomendadas.

        Args:
            collection_name (str): Nome da coleção a ser criada.
            hnsw_config (HnswConfigDiff, optional): Configuração para o mecanismo de busca ANN da coleção. Em coleções multi-tenancy é necessário aplicar as configurações recomendadas da documentação para performance de indexação.
            tenant_index (bool, optional): Se à coleção deve ser aplicado um índice de payload.
        """

        collection_parameters = {
            'collection_name': collection_name,
            'vectors_config': models.VectorParams(
                size=self.embedding_dimension,
                distance=models.Distance.COSINE,
                hnsw_config=hnsw_config,
            ),
        }

        if force_recreate:
            # Recria a coleção com as configurações recomendadas, dados são apagados
            await self.client.recreate_collection(**collection_parameters)
        else:
            collection_exists = await self.client.collection_exists(collection_name)

            if collection_exists:
                return

            await self.client.create_collection(**collection_parameters)

        if tenant_index:
            # Payload index necessário apenas em coleções multi-tenancy, criando índices para os grupos. Nesse caso, cada grupo de acesso é separado por id de usuário
            await self.client.create_payload_index(
                collection_name=collection_name,
                field_name='metadata.user_id',
                field_schema=models.KeywordIndexParams(
                    type='keyword',
                    is_tenant=True,
                ),
            )

    async def store_data(
        self,
        collection_name: str,
        data_chunks: list[PayloadDataModel],
        map_func=None,
    ):
        """Função para gerar embeddings e armazenar dados no Vector Store.

        Args:
            collection_name (str): Sessão para inserir os dados
            data_chunks (list[dict]): Lista de dicionários, onde cada item deve conter 'texto' e 'metadados' para o payload.
            map_func (any): Função para mapear os valores de data_chunks para o padrão desejado.
        """

        if map_func:
            try:
                data_chunks = list(map(map_func, data_chunks))
            except Exception as exc:
                print(f'Mapping function in Data Chunks failed: {exc}')

        texts_to_embed = [chunk['text'] for chunk in data_chunks]

        # Gerando vetores de embeddings do modelo padrão em thread separada
        embeddings_gen = await asyncio.to_thread(self.embedder.embed, texts_to_embed)

        # Pontos são estruturas com vetores e payload (metadados) no Vector Store
        points = [
            models.PointStruct(id=str(uuid4()), vector=vector.tolist(), payload=chunk)
            for vector, chunk in zip(embeddings_gen, data_chunks)
        ]

        await self.client.upsert(collection_name, wait=True, points=points)

        return [p.id for p in points]

    async def search_documents(self, collection_name: str, id: str, query: str):
        """Função para buscar em todos os documentos do usuário.

        Args:
         collection_name (str): Nome da coleção para manipular.
         id (str): Identificador para o dado do usuário na coleção,
         query (str): Consulta para busca por similaridade mais próxima (ANN).
        """

        query_embbeding = await asyncio.to_thread(self.embedder.embed, query)
        vector = next(query_embbeding).tolist()

        results = await self.client.query_points(
            collection_name,
            vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key='metadata.user_id', match=models.MatchValue(value=id)
                    )
                ]
            ),
            limit=10,
            with_payload=models.PayloadSelectorExclude(exclude=['metadata.user_id']),
        )

        return results

    async def search_filtered_documents(
        self, collection_name: str, id: str, filter: str
    ):
        """Função para buscar em documentos do usuário com base no filtro.

        Args:
          collection_name (str): Nome da coleção para manipular.
          id (str): Identificador para o dado do usuário na coleção.
          filter (str): String para filtrar os dados por metadata.
        """
        return NotImplemented

    async def delete_collection(self, collection_name: str):
        """Função para deleção de coleções no Vector Store.

        Args:
            collection_name (str): Nome da coleção para excluir.
        """

        await self.client.delete_collection(collection_name)

        print(f'\t>> Collection {collection_name} was deleted')

    async def delete_collection_data(self, collection_name: str, id: str):
        """Função para deleção de dados em coleções do Vector Store.

        Args:
            collection_name (str): Nome da coleção para manipular.
            id (str): Identificador para o dado do usuário na coleção.
        """

        # Criando filtro com base em um campo user_id do metadata e id recebido
        user_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key='metadata.user_id', match=models.MatchValue(value=id)
                )
            ]
        )

        # Deletando dados que possuírem esse match
        await self.client.delete(
            collection_name,
            points_selector=models.FilterSelector(filter=user_filter),
            wait=True,
        )

        print(f'\t>> {id}: Todos os pontos foram deletados da {collection_name}.')
