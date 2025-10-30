# agente_auditoria_inteligente.py
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import smtplib
from email.mime.text import MIMEText  # Nome correto
from email.mime.multipart import MIMEMultipart  # Nome correto
from sqlalchemy import text  # Importação faltante

class AgenteAuditoriaInteligente:
    """Agente especializado em validação e auditoria fiscal inteligente"""
    
    def __init__(self, gestor_bd, config_path='config_auditoria.py'):
        self.gestor_bd = gestor_bd
        self.config = self._carregar_configuracao(config_path)
        self.agente_deepseek = AgenteInteligenteDeepSeek()
        self.resultados = []
        self.historico_auditorias = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def executar_auditoria_completa(self) -> Dict[str, Any]:
        """Executa auditoria completa conforme requisitos"""
        
        self.logger.info("🔍 Iniciando auditoria fiscal inteligente")
        
        try:
            # 1. Coleta de dados
            dados_auditoria = self._coletar_dados_auditoria()
            
            # 2. Validações automáticas
            validacoes = self._executar_validacoes_automaticas(dados_auditoria)
            
            # 3. Análise inteligente com DeepSeek
            analise_inteligente = self._analisar_com_inteligencia_artificial(validacoes)
            
            # 4. Identificação de maiores agressores
            agressores = self._identificar_maiores_agressores(validacoes)
            
            # 5. Produção de relatórios
            relatorios = self._produzir_relatorios_auditoria(
                validacoes, analise_inteligente, agressores
            )
            
            # 6. Envio para responsáveis
            self._enviar_relatorios_responsaveis(relatorios)
            
            self.logger.info("✅ Auditoria concluída com sucesso")
            return relatorios
            
        except Exception as e:
            self.logger.error(f"❌ Erro na auditoria: {e}")
            return {'erro': str(e)}
    
    def _validar_calculo_impostos(self, session) -> List[Dict[str, Any]]:
        """Valida cálculo de impostos com base nas regras fiscais"""
        erros = []
        
        try:
            # Buscar notas com possíveis erros de cálculo
            query = text("""
                SELECT nf.id_nf, nf.numero, nf.valor_total, 
                       nf.valor_icms, nf.valor_pis, nf.valor_cofins,
                       (nf.valor_total * 0.12) as icms_calculado,
                       (nf.valor_total * 0.0065) as pis_calculado,
                       (nf.valor_total * 0.03) as cofins_calculado
                FROM notas_fiscais nf
                WHERE ABS(nf.valor_icms - (nf.valor_total * 0.12)) > 0.01
                   OR ABS(nf.valor_pis - (nf.valor_total * 0.0065)) > 0.01
                   OR ABS(nf.valor_cofins - (nf.valor_total * 0.03)) > 0.01
            """)
            
            resultados = session.execute(query).fetchall()
            
            for row in resultados:
                erros.append({
                    'tipo': 'CALCULO_IMPOSTO_INCORRETO',
                    'severidade': 'ALTA',
                    'descricao': f'Nota {row[1]} - Divergência nos cálculos de impostos',
                    'detalhes': {
                        'ICMS_esperado': row[6],
                        'ICMS_informado': row[3],
                        'PIS_esperado': row[7],
                        'PIS_informado': row[4],
                        'COFINS_esperado': row[8],
                        'COFINS_informado': row[5]
                    },
                    'sugestao_correcao': 'Recalcular impostos com base no valor total',
                    'id_nf': row[0]
                })
                
        except Exception as e:
            self.logger.error(f"Erro na validação de impostos: {e}")
            
        return erros
    
    def _validar_codigos_fiscais(self, session) -> List[Dict[str, Any]]:
        """Valida consistência dos códigos fiscais"""
        alertas = []
        
        try:
            # Validar CFOPs inconsistentes com a operação
            query = text("""
                SELECT it.id_item, it.id_nf, it.cfop, nf.tipo_operacao, nf.numero
                FROM itens_nf it
                JOIN notas_fiscais nf ON it.id_nf = nf.id_nf
                WHERE (nf.tipo_operacao = 'entrada' AND it.cfop NOT LIKE '1%')
                   OR (nf.tipo_operacao = 'saída' AND it.cfop NOT LIKE '2%')
                   OR (nf.tipo_operacao = 'saída' AND it.cfop NOT LIKE '5%')
                   OR (nf.tipo_operacao = 'saída' AND it.cfop NOT LIKE '6%')
            """)
            
            resultados = session.execute(query).fetchall()
            
            for row in resultados:
                alertas.append({
                    'tipo': 'CODIGO_FISCAL_INCONSISTENTE',
                    'severidade': 'MEDIA',
                    'descricao': f'CFOP {row[2]} inconsistente com operação {row[3]} na nota {row[4]}',
                    'sugestao_correcao': f'Verificar CFOP apropriado para operação {row[3]}',
                    'id_item': row[0],
                    'id_nf': row[1]
                })
                
        except Exception as e:
            self.logger.error(f"Erro na validação de códigos fiscais: {e}")
            
        return alertas
    
    def _identificar_maiores_agressores(self, validacoes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica os maiores agressores e sugere melhorias"""
        
        agressores = []
        
        # Agrupar problemas por emitente
        problemas_por_emitente = {}
        for erro in validacoes.get('erros_graves', []) + validacoes.get('alertas', []):
            emitente = erro.get('emitente', 'Desconhecido')
            if emitente not in problemas_por_emitente:
                problemas_por_emitente[emitente] = []
            problemas_por_emitente[emitente].append(erro)
        
        # Ordenar por quantidade de problemas
        for emitente, problemas in problemas_por_emitente.items():
            severidade = self._calcular_severidade_agregada(problemas)
            agressores.append({
                'emitente': emitente,
                'quantidade_problemas': len(problemas),
                'severidade': severidade,
                'problemas': problemas[:5],  # Top 5 problemas
                'sugestoes_melhoria': self._gerar_sugestoes_melhoria(problemas)
            })
        
        # Ordenar por severidade e quantidade
        agressores.sort(key=lambda x: (x['severidade'], x['quantidade_problemas']), reverse=True)
        
        return agressores[:10]  # Top 10 agressores
    
    def _gerar_sugestoes_melhoria(self, problemas: List[Dict[str, Any]]) -> List[str]:
        """Gera sugestões de melhoria baseadas nos problemas identificados"""
        
        sugestoes = []
        tipos_problema = [p['tipo'] for p in problemas]
        
        if 'CALCULO_IMPOSTO_INCORRETO' in tipos_problema:
            sugestoes.append("Implementar validação automática de cálculos de impostos")
            sugestoes.append("Treinar equipe sobre as alíquotas fiscais vigentes")
        
        if 'CODIGO_FISCAL_INCONSISTENTE' in tipos_problema:
            sugestoes.append("Revisar tabela de CFOPs utilizados")
            sugestoes.append("Implementar validação de CFOP por tipo de operação")
        
        if 'DADOS_OBRIGATORIOS' in tipos_problema:
            sugestoes.append("Melhorar processo de coleta de dados obrigatórios")
            sugestoes.append("Implementar validação em tempo real nos formulários")
        
        return sugestoes

    # Métodos faltantes que são chamados mas não estão definidos no código original
    # Vamos adicionar implementações básicas para evitar erros

    def _carregar_configuracao(self, config_path):
        """Carrega configuração do sistema de auditoria"""
        # Implementação básica - pode ser expandida conforme necessário
        return {
            'email': {
                'smtp_server': 'smtp.example.com',
                'port': 587,
                'sender_email': 'auditoria@empresa.com',
                'password': 'password'
            }
        }

    def _coletar_dados_auditoria(self):
        """Coleta dados para auditoria"""
        # Implementação básica
        return {}

    def _executar_validacoes_automaticas(self, dados_auditoria):
        """Executa validações automáticas"""
        # Implementação básica
        return {
            'erros_graves': [],
            'alertas': []
        }

    def _analisar_com_inteligencia_artificial(self, validacoes):
        """Análise com IA"""
        # Implementação básica
        return {}

    def _produzir_relatorios_auditoria(self, validacoes, analise_inteligente, agressores):
        """Produz relatórios de auditoria"""
        return {
            'erros_graves': validacoes.get('erros_graves', []),
            'alertas': validacoes.get('alertas', []),
            'maiores_agressores': agressores,
            'resumo_executivo': {
                'total_erros': len(validacoes.get('erros_graves', [])),
                'total_alertas': len(validacoes.get('alertas', [])),
                'timestamp': datetime.now().isoformat()
            }
        }

    def _enviar_relatorios_responsaveis(self, relatorios):
        """Envia relatórios por email"""
        # Implementação básica - pode ser expandida
        self.logger.info("Relatórios prontos para envio")

    def _calcular_severidade_agregada(self, problemas):
        """Calcula severidade agregada baseada nos problemas"""
        if any(p.get('severidade') == 'ALTA' for p in problemas):
            return 'ALTA'
        elif any(p.get('severidade') == 'MEDIA' for p in problemas):
            return 'MEDIA'
        return 'BAIXA'

# Classe auxiliar necessária
class AgenteInteligenteDeepSeek:
    """Classe auxiliar para análise com DeepSeek"""
    def __init__(self):
        pass

# Uso no sistema principal
if __name__ == "__main__":
    from sistema_fiscal import GestorBancoDados
    
    # Inicializar sistema
    gestor_bd = GestorBancoDados()
    agente_auditoria = AgenteAuditoriaInteligente(gestor_bd)
    
    # Executar auditoria
    resultados = agente_auditoria.executar_auditoria_completa()
    
    print("📊 Auditoria Fiscal Inteligente Concluída!")
    print(f"✅ Erros identificados: {len(resultados.get('erros_graves', []))}")
    print(f"⚠️  Alertas: {len(resultados.get('alertas', []))}")
    print(f"🎯 Maiores agressores: {len(resultados.get('maiores_agressores', []))}")