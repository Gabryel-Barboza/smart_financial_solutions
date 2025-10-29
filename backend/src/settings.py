from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Necessário para carregar o LangSmith
load_dotenv('.env', encoding='utf-8')


# Configurações de variáveis ambiente
class Settings(BaseSettings):
    debug_mode: bool = False
    database_uri: str
    sender_email: str
    sender_password: str
    qdrant_url: str = 'http://localhost:6333'

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
    )


settings = Settings()
