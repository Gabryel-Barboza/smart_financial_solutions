from pathlib import Path

from fastembed import TextEmbedding

ROOT_PATH = Path(__file__).parent.parent.parent


def get_fastembed_embedding(
    model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
) -> TextEmbedding:
    """Função para retornar o modelo de embedding do FastEmbed.

    Args:
        model_name (str, optional): Nome do modelo de embedding utilizado. Por padrão, é usado o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
    """
    embeddings = TextEmbedding(
        model_name=model_name, cache_dir=ROOT_PATH / 'fastembed_cache/'
    )

    return embeddings
