from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Necessário para carregar o LangSmith
load_dotenv('.env', encoding='utf-8')


# Configurações de variáveis ambiente
class Settings(BaseSettings):
    database_uri: str
    n8n_webhook: str

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
    )


settings = Settings()
