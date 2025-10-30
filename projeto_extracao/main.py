# main.py - Versão simplificada
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("      SISTEMA FISCAL - PROCESSAMENTO DE NF-e")
    print("=" * 60)
    
    try:
        # Importar e testar o sistema
        from sistema_fiscal import AgenteFiscal
        
        print("✅ Módulos carregados com sucesso!")
        print("🚀 Inicializando Agente Fiscal...")
        
        agente = AgenteFiscal()
        print("✅ Agente Fiscal inicializado!")
        
        # Menu simples
        while True:
            print("\nOpções:")
            print("1. Testar processamento XML")
            print("2. Listar documentos")
            print("3. Sair")
            
            opcao = input("\nEscolha: ").strip()
            
            if opcao == '1':
                arquivo = input("Caminho do XML: ").strip()
                if os.path.exists(arquivo):
                    resultado = agente.processar_xml_nfe(arquivo)
                    print(f"Resultado: {resultado}")
                else:
                    print("❌ Arquivo não encontrado!")
            
            elif opcao == '2':
                documentos = agente.listar_documentos(limite=10)
                print(f"Documentos: {documentos}")
            
            elif opcao == '3':
                print("👋 Saindo...")
                break
            
            else:
                print("❌ Opção inválida!")
                
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se o arquivo sistema_fiscal.py existe na mesma pasta")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()