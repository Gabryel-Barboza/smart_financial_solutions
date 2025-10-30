# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DB', 'fiscal_db')
}

def get_mysql_uri():
    """Retorna a URI de conexão do MySQL"""
    config = MYSQL_CONFIG
    return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# SQLite fallback
SQLITE_URI = "sqlite:///sistema_fiscal.db"

# Chave da API DeepSeek (se for usar)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')