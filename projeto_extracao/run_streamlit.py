# run_streamlit.py
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

try:
    from sistema_fiscal import AgenteFiscal, MYSQL_CONFIG
    from app_streamlit import main
    
    # Executar o Streamlit
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("💡 Verifique os arquivos:")
    print("   - sistema_fiscal.py existe?")
    print("   - app_streamlit.py existe?")
    print("   - As classes estão com os nomes corretos?")