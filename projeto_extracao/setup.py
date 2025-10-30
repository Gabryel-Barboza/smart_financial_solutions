import os
import subprocess
import sys

def install_requirements():
    """Instala todas as dependências necessárias"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False
    
    return True

def download_spacy_model():
    """Baixa o modelo do spaCy em português"""
    print("\n🔧 Baixando modelo spaCy em português...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "pt_core_news_sm"])
        print("✅ Modelo spaCy baixado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Aviso: Não foi possível baixar o modelo spaCy: {e}")
        print("💡 Você pode instalar manualmente com: python -m spacy download pt_core_news_sm")

def check_tesseract():
    """Verifica se o Tesseract está instalado"""
    print("\n🔍 Verificando Tesseract OCR...")
    
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract encontrado!")
    except Exception as e:
        print("❌ Tesseract não encontrado ou configurado incorretamente")
        print("💡 Instale o Tesseract:")
        print("   Windows: Baixe do GitHub oficial")
        print("   Linux: sudo apt-get install tesseract-ocr-por")
        print("   Mac: brew install tesseract")

def create_env_file():
    """Cria arquivo .env de exemplo se não existir"""
    if not os.path.exists(".env"):
        print("\n📄 Criando arquivo .env de exemplo...")
        
        env_content = """# Configuração do Sistema de Extração Fiscal
DEEPSEEK_API_KEY=sua_chave_deepseek_aqui

# Banco de Dados - Escolha um:
# MongoDB (padrão):
MONGO_URI=mongodb://localhost:27017/

# PostgreSQL:
POSTGRES_URI=postgresql://usuario:senha@localhost:5432/fiscal_db

# Configurações adicionais
DEBUG=true
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado!")
        print("💡 Edite o arquivo .env com suas configurações antes de executar o sistema")

def main():
    """Configuração inicial do sistema"""
    print("🛠️  CONFIGURAÇÃO DO SISTEMA DE EXTRAÇÃO FISCAL")
    print("=" * 50)
    
    # Instalar dependências
    if not install_requirements():
        return
    
    # Baixar modelo spaCy
    download_spacy_model()
    
    # Verificar Tesseract
    check_tesseract()
    
    # Criar .env
    create_env_file()
    
    print("\n🎉 Configuração concluída!")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("1. Edite o arquivo .env com suas configurações")
    print("2. Configure sua chave da API DeepSeek")
    print("3. Execute: python main.py")
    print("4. Escolha a opção 4 para testar com o XML fornecido")

if __name__ == "__main__":
    main()