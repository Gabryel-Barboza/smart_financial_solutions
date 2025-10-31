# sistema_gerencial_corrigido.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, func, extract, and_, or_, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from io import BytesIO
import logging
import traceback

# Carregar variáveis de ambiente
load_dotenv()

# Importar configurações centralizadas
try:
    from config import get_mysql_uri, DEEPSEEK_API_KEY
except ImportError:
    # Fallback para desenvolvimento
    def get_mysql_uri():
        return os.getenv('MYSQL_URI', 'mysql+pymysql://user:password@localhost/fiscal_db')
    
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
#   ASSISTENTE CONSULTOR COM DEEPSEEK (APRIMORADO)
# =========================================================

class AssistenteConsultorDeepSeek:
    """Assistente especializado em contabilidade, tributação e análises gerenciais"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.contexto_especializado = """
        Você é um consultor especializado em:
        - Contabilidade e tributação brasileira
        - Análises gerenciais e financeiras
        - Regimes tributários (Simples Nacional, Lucro Presumido, Lucro Real)
        - Obrigações fiscais e acessórias
        - Planejamento tributário estratégico
        - Análise de dados fiscais e financeiros
        
        Forneça orientações práticas, baseadas na legislação vigente, com linguagem clara e objetiva.
        Sempre que possível, inclua exemplos e sugestões de action.
        """
    
    def consultar_pergunta(self, pergunta: str, contexto_dados: str = "") -> Dict:
        """Faz consulta à API DeepSeek para dúvidas estratégicas"""
        try:
            if not self.api_key:
                return {
                    'sucesso': False,
                    'erro': 'API Key do DeepSeek não configurada',
                    'resposta': 'Configure a DEEPSEEK_API_KEY no arquivo .env'
                }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            prompt = f"""
            {self.contexto_especializado}
            
            CONTEXTO DOS DADOS DA EMPRESA:
            {contexto_dados}
            
            PERGUNTA DO USUÁRIO:
            {pergunta}
            
            Forneça uma resposta técnica e prática baseada na legislação brasileira atual.
            Inclua insights acionáveis e recomendações específicas quando aplicável.
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system", 
                        "content": self.contexto_especializado
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                resposta_completa = response.json()
                conteudo_resposta = resposta_completa['choices'][0]['message']['content']
                
                return {
                    'sucesso': True,
                    'resposta': conteudo_resposta,
                    'uso_tokens': resposta_completa.get('usage', {}),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                error_detail = response.text
                return {
                    'sucesso': False,
                    'erro': f"Erro na API: {response.status_code} - {error_detail}",
                    'resposta': "Não foi possível consultar o assistente no momento."
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'resposta': "Erro de conexão com o assistente inteligente."
            }

# =========================================================
#   SISTEMA GERENCIAL PRINCIPAL - COMPLETO E CORRIGIDO
# =========================================================

class SistemaGerencialNF:
    def __init__(self, gestor_bd=None):
        """
        Inicializa o sistema gerencial com conexão ao MySQL
        Se gestor_bd for fornecido, usa a mesma conexão do sistema fiscal
        """
        self.engine = None
        self.Session = None
        self.conexao_ativa = False
        
        # Inicializar assistente DeepSeek
        self.assistente = AssistenteConsultorDeepSeek(DEEPSEEK_API_KEY)
        
        try:
            if gestor_bd and hasattr(gestor_bd, 'engine') and gestor_bd.engine is not None:
                # Reutiliza a conexão existente do sistema fiscal
                self.engine = gestor_bd.engine
                self.Session = sessionmaker(bind=self.engine)
                self.conexao_ativa = True
                logger.info("✅ Sistema gerencial usando conexão compartilhada com sistema fiscal")
            else:
                # Conexão própria usando as MESMAS configurações
                try:
                    self.engine = create_engine(get_mysql_uri())
                    self.Session = sessionmaker(bind=self.engine)
                    self.conexao_ativa = True
                    logger.info("✅ Sistema gerencial com conexão própria ao MySQL")
                except Exception as e:
                    logger.error(f"❌ Erro ao conectar ao MySQL: {e}")
                    self.conexao_ativa = False
            
            self.setup_analysis()
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na inicialização: {e}")
            self.conexao_ativa = False
    
    def setup_analysis(self):
        """Configuração inicial para análises"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def testar_conexao(self):
        """Testa a conexão com o banco de dados"""
        try:
            if not self.conexao_ativa or not self.engine:
                return False
                
            session = self.Session()
            resultado = session.execute(text("SELECT 1")).fetchone()
            session.close()
            return resultado[0] == 1
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False

    # =========================================================
    #   MÉTODOS DE CONSULTA AO ASSISTENTE DEEPSEEK (APRIMORADOS)
    # =========================================================

    def consultar_assistente(self, pergunta: str, dados_contexto: Any = None) -> Dict:
        """Consulta o assistente especializado em contabilidade/tributação"""
        try:
            contexto_str = ""
            if dados_contexto is not None:
                if isinstance(dados_contexto, pd.DataFrame):
                    # Resumo estatístico para DataFrames
                    contexto_str = self._gerar_resumo_dataframe(dados_contexto)
                elif isinstance(dados_contexto, dict):
                    contexto_str = json.dumps(dados_contexto, indent=2, ensure_ascii=False)
                else:
                    contexto_str = str(dados_contexto)
            
            return self.assistente.consultar_pergunta(pergunta, contexto_str)
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f"Erro na consulta ao assistente: {str(e)}",
                'resposta': "Não foi possível processar a consulta."
            }

    def _gerar_resumo_dataframe(self, df: pd.DataFrame) -> str:
        """Gera resumo estatístico de DataFrame para o assistente"""
        if df.empty:
            return "Nenhum dado disponível para análise."
        
        resumo = {
            'total_registros': len(df),
            'periodo_analisado': f"{df['data_emissao'].min()} a {df['data_emissao'].max()}" if 'data_emissao' in df.columns else 'Período não disponível',
            'colunas_disponiveis': df.columns.tolist()
        }
        
        # Adicionar métricas financeiras se disponíveis
        if 'valor_total' in df.columns:
            resumo.update({
                'faturamento_total': float(df['valor_total'].sum()),
                'ticket_medio': float(df['valor_total'].mean()),
                'maior_nota': float(df['valor_total'].max()),
                'menor_nota': float(df['valor_total'].min())
            })
        
        # Adicionar informações geográficas se disponíveis
        if 'uf_emitente' in df.columns:
            resumo['distribuicao_uf'] = df['uf_emitente'].value_counts().head(5).to_dict()
        
        return json.dumps(resumo, indent=2, ensure_ascii=False)

    def analisar_dados_fiscais_inteligente(self, dados: pd.DataFrame) -> Dict:
        """Analisa dados fiscais usando o assistente inteligente"""
        if dados.empty:
            return {'sucesso': False, 'erro': 'Nenhum dado disponível para análise'}
        
        pergunta = """
        Analise estes dados fiscais e forneça insights estratégicos completos:
        
        1. Padrões de faturamento e sazonalidade
        2. Possíveis otimizações tributárias  
        3. Riscos fiscais identificáveis
        4. Recomendações estratégicas para crescimento
        5. Análise de eficiência operacional
        6. Sugestões de melhorias nos processos fiscais
        
        Forneça uma análise estruturada e insights acionáveis.
        """
        
        return self.consultar_assistente(pergunta, dados)

    # =========================================================
    #   RELATÓRIOS PERSONALIZADOS (COMPLETO) - VERSÃO CORRIGIDA
    # =========================================================

    def gerar_relatorio_setorial(self, setor: str, periodo: Dict) -> Dict:
        """Gera relatório personalizado por setor com informações internas e externas - VERSÃO CORRIGIDA"""
        try:
            # CORREÇÃO: Converter as datas do período para o formato correto
            data_inicio = periodo.get('inicio', '2024-01-01')
            data_fim = periodo.get('fim', '2024-12-31')
            
            # Recuperar dados do período
            dados = self.recuperar_dados({
                'data_inicio': data_inicio,
                'data_fim': data_fim
            })
            
            if dados.empty:
                return {
                    'sucesso': False, 
                    'erro': 'Nenhum dado encontrado para o período selecionado'
                }
            
            # Inicializar o relatório com metadados
            relatorio = {
                'metadata': {
                    'setor': setor,
                    'periodo': periodo,
                    'data_geracao': datetime.now().isoformat(),
                    'total_registros': len(dados)
                }
            }
            
            # CORREÇÃO: Garantir que todas as seções sejam geradas mesmo com dados limitados
            secoes = {
                'resumo_executivo': self._gerar_resumo_executivo(dados),
                'analise_estrategica': self._gerar_analise_estrategica(dados, setor),
                'indicadores_chave': self._calcular_indicadores_setoriais(dados, setor),
                'analise_tendencias': self._analisar_tendencias_avancada(dados),
                'benchmarking_setorial': self._gerar_benchmarking_setorial(setor),
                'recomendacoes_estrategicas': self._gerar_recomendacoes_estrategicas(dados, setor),
                'alertas_riscos': self._identificar_alertas_riscos(dados)
            }
            
            # Adicionar cada seção ao relatório, capturando erros individuais
            for nome_secao, conteudo_secao in secoes.items():
                try:
                    relatorio[nome_secao] = conteudo_secao
                except Exception as e:
                    logger.error(f"Erro ao gerar seção {nome_secao}: {e}")
                    relatorio[nome_secao] = {'erro': f'Erro ao gerar {nome_secao}', 'detalhes': str(e)}
            
            # CORREÇÃO: Adicionar análise do assistente IA apenas se houver dados suficientes
            try:
                if len(dados) > 0:
                    analise_ia = self.consultar_assistente(
                        f"Analise este relatório do setor {setor} e forneça insights adicionais baseados nestes dados fiscais",
                        relatorio
                    )
                    
                    if analise_ia['sucesso']:
                        relatorio['insights_ia'] = analise_ia['resposta']
                    else:
                        relatorio['insights_ia'] = "Análise IA indisponível"
                else:
                    relatorio['insights_ia'] = "Dados insuficientes para análise IA"
            except Exception as e:
                logger.error(f"Erro na análise IA: {e}")
                relatorio['insights_ia'] = "Análise IA indisponível no momento"
            
            return {'sucesso': True, 'relatorio': relatorio}
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório setorial: {str(e)}")
            return {'sucesso': False, 'erro': str(e)}

    def _gerar_resumo_executivo(self, dados: pd.DataFrame) -> Dict:
        """Gera resumo executivo completo - VERSÃO MAIS ROBUSTA"""
        try:
            if dados.empty:
                return {
                    'faturamento_total': 0.0,
                    'quantidade_notas': 0,
                    'ticket_medio': 0.0,
                    'periodo_analisado': 'Sem dados',
                    'principais_insights': ['Nenhum dado disponível para análise'],
                    'indicadores_desempenho': {
                        'crescimento_mensal': 0.0,
                        'eficiencia_operacional': 0.0
                    }
                }
            
            faturamento_total = float(dados['valor_total'].sum()) if 'valor_total' in dados.columns else 0.0
            quantidade_nf = len(dados)
            ticket_medio = float(faturamento_total / quantidade_nf) if quantidade_nf > 0 else 0.0
            
            # Análise temporal
            periodo_str = "Período não disponível"
            if 'data_emissao' in dados.columns:
                try:
                    dados_temp = dados.copy()
                    dados_temp['data_emissao'] = pd.to_datetime(dados_temp['data_emissao'], errors='coerce')
                    dados_temp = dados_temp.dropna(subset=['data_emissao'])
                    
                    if not dados_temp.empty:
                        min_date = dados_temp['data_emissao'].min()
                        max_date = dados_temp['data_emissao'].max()
                        periodo_str = f"{min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')}"
                except Exception as e:
                    logger.error(f"Erro ao processar datas: {e}")
                    periodo_str = "Erro no processamento de datas"
            
            return {
                'faturamento_total': faturamento_total,
                'quantidade_notas': quantidade_nf,
                'ticket_medio': ticket_medio,
                'periodo_analisado': periodo_str,
                'principais_insights': self._extrair_insights_rapidos(dados),
                'indicadores_desempenho': {
                    'crescimento_mensal': float(self._calcular_crescimento_mensal(dados)),
                    'eficiencia_operacional': float(self._calcular_eficiencia_operacional(dados))
                }
            }
        except Exception as e:
            logger.error(f"Erro crítico ao gerar resumo executivo: {e}")
            return {
                'faturamento_total': 0.0,
                'quantidade_notas': 0,
                'ticket_medio': 0.0,
                'periodo_analisado': 'Erro na análise',
                'principais_insights': ['Erro na geração de insights'],
                'indicadores_desempenho': {
                    'crescimento_mensal': 0.0,
                    'eficiencia_operacional': 0.0
                }
            }

    def _gerar_analise_estrategica(self, dados: pd.DataFrame, setor: str) -> Dict:
        """Gera análise estratégica do setor"""
        analise = {
            'posicionamento_mercado': self._analisar_posicionamento_mercado(dados, setor),
            'vantagens_competitivas': self._identificar_vantagens_competitivas(dados),
            'oportunidades_crescimento': self._identificar_oportunidades_crescimento(dados, setor),
            'ameacas_riscos': self._identificar_ameacas_riscos(setor)
        }
        return analise

    def _calcular_indicadores_setoriais(self, dados: pd.DataFrame, setor: str) -> Dict:
        """Calcula indicadores específicos do setor"""
        indicadores = {
            'faturamento_mensal': self._calcular_faturamento_mensal(dados),
            'clientes_ativos': dados['cnpj_destinatario'].nunique() if 'cnpj_destinatario' in dados.columns else 0,
            'evolucao_faturamento': self._calcular_evolucao_faturamento(dados),
            'concentracao_clientes': self._calcular_concentracao_clientes(dados),
            'saude_financeira': self._avaliar_saude_financeira(dados)
        }
        
        # Indicadores específicos por setor
        if setor == 'comercio':
            indicadores.update({
                'giro_estoque_estimado': self._estimar_giro_estoque(dados),
                'sazonalidade': self._analisar_sazonalidade(dados)
            })
        elif setor == 'industria':
            indicadores.update({
                'complexidade_produtiva': self._avaliar_complexidade_produtiva(dados),
                'valor_agregado': self._calcular_valor_agregado(dados)
            })
        elif setor == 'servicos':
            indicadores.update({
                'recorrencia_faturamento': self._avaliar_recorrencia_faturamento(dados),
                'valor_medio_servico': self._calcular_valor_medio_servico(dados)
            })
        
        return indicadores

    # =========================================================
    #   ANÁLISES PREDITIVAS E SIMULAÇÕES (APRIMORADAS)
    # =========================================================

    def prever_faturamento(self, dados: pd.DataFrame, meses_futuros: int = 6) -> Dict:
        """Preve faturamento futuro usando múltiplos modelos"""
        try:
            if dados.empty or len(dados) < 3:
                return {'sucesso': False, 'erro': 'Dados insuficientes para previsão'}
            
            # Preparar dados temporais
            dados_temp = dados.copy()
            dados_temp['data'] = pd.to_datetime(dados_temp['data_emissao'])
            dados_temp['mes'] = dados_temp['data'].dt.to_period('M')
            
            # Agrupar por mês
            faturamento_mensal = dados_temp.groupby('mes')['valor_total'].sum().reset_index()
            faturamento_mensal['periodo'] = range(len(faturamento_mensal))
            
            if len(faturamento_mensal) < 3:
                return {'sucesso': False, 'erro': 'Menos de 3 meses de dados para treinamento'}
            
            # Treinar múltiplos modelos
            X = faturamento_mensal[['periodo']]
            y = faturamento_mensal['valor_total']
            
            # Modelo Linear
            modelo_linear = LinearRegression()
            modelo_linear.fit(X, y)
            
            # Modelo Random Forest
            modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
            modelo_rf.fit(X, y)
            
            # Fazer previsões
            ultimo_periodo = faturamento_mensal['periodo'].max()
            periodos_futuros = list(range(ultimo_periodo + 1, ultimo_periodo + meses_futuros + 1))
            X_futuro = pd.DataFrame({'periodo': periodos_futuros})
            
            previsoes_linear = modelo_linear.predict(X_futuro)
            previsoes_rf = modelo_rf.predict(X_futuro)
            
            # Combinar previsões (média ponderada)
            previsoes_comb = (previsoes_linear * 0.3 + previsoes_rf * 0.7)
            
            # Calcular métricas de confiança
            score_linear = modelo_linear.score(X, y)
            score_rf = modelo_rf.score(X, y)
            confianca = max(0, min(100, (score_linear * 0.3 + score_rf * 0.7) * 100))
            
            # Gerar previsões formatadas
            previsoes_formatadas = []
            datas_futuras = self._gerar_datas_futuras(meses_futuros)
            
            for i, (data, previsao) in enumerate(zip(datas_futuras, previsoes_comb)):
                previsoes_formatadas.append({
                    'mes': data.strftime('%B %Y'),
                    'valor_previsto': float(previsao),
                    'confianca': float(confianca),
                    'intervalo_min': float(previsao * 0.9),  # -10%
                    'intervalo_max': float(previsao * 1.1)   # +10%
                })
            
            return {
                'sucesso': True,
                'previsoes': previsoes_formatadas,
                'metricas': {
                    'r2_score_linear': float(score_linear),
                    'r2_score_rf': float(score_rf),
                    'confianca_geral': float(confianca),
                    'tendencia': 'crescente' if previsoes_comb[-1] > previsoes_comb[0] else 'decrescente',
                    'crescimento_previsto': float(((previsoes_comb[-1] - previsoes_comb[0]) / previsoes_comb[0]) * 100) if previsoes_comb[0] > 0 else 0
                }
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': f"Erro na previsão: {str(e)}"}

    def simular_cenarios_tributarios(self, dados: pd.DataFrame, cenarios: List[str]) -> Dict:
        """Simula diferentes cenários tributários"""
        try:
            faturamento_anual = dados['valor_total'].sum() if not dados.empty else 0
            
            resultados = {}
            for cenario in cenarios:
                if cenario == 'simples_nacional':
                    resultados[cenario] = self._calcular_simples_nacional(faturamento_anual)
                elif cenario == 'lucro_presumido':
                    resultados[cenario] = self._calcular_lucro_presumido(faturamento_anual)
                elif cenario == 'lucro_real':
                    resultados[cenario] = self._calcular_lucro_real(faturamento_anual)
            
            return {
                'sucesso': True,
                'faturamento_anual': float(faturamento_anual),
                'cenarios': resultados,
                'recomendacao': self._recomendar_regime_tributario(resultados)
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

    # =========================================================
    #   MÉTODOS AUXILIARES PARA ANÁLISES
    # =========================================================

    def _gerar_datas_futuras(self, meses: int) -> List[datetime]:
        """Gera lista de datas futuras para previsões"""
        datas = []
        data_atual = datetime.now()
        for i in range(1, meses + 1):
            proxima_data = data_atual + timedelta(days=30 * i)
            datas.append(proxima_data)
        return datas

    def _calcular_simples_nacional(self, faturamento: float) -> Dict:
        """Calcula impostos no Simples Nacional (exemplo simplificado)"""
        # Valores fictícios para demonstração
        aliquota = 0.06  # 6%
        return {
            'regime': 'Simples Nacional',
            'imposto_total': faturamento * aliquota,
            'aliquota_efetiva': aliquota,
            'observacoes': 'Valores estimados - consultar contador'
        }

    def _calcular_lucro_presumido(self, faturamento: float) -> Dict:
        """Calcula impostos no Lucro Presumido (exemplo simplificado)"""
        # Valores fictícios para demonstração
        irpj = faturamento * 0.048
        csll = faturamento * 0.012
        pis = faturamento * 0.0065
        cofins = faturamento * 0.03
        total = irpj + csll + pis + cofins
        
        return {
            'regime': 'Lucro Presumido',
            'imposto_total': total,
            'aliquota_efetiva': total / faturamento if faturamento > 0 else 0,
            'detalhamento': {
                'IRPJ': irpj,
                'CSLL': csll,
                'PIS': pis,
                'COFINS': cofins
            }
        }

    def _calcular_lucro_real(self, faturamento: float) -> Dict:
        """Calcula impostos no Lucro Real (exemplo simplificado)"""
        # Valores fictícios para demonstração
        lucro_estimado = faturamento * 0.15  # Supondo 15% de lucro
        irpj = lucro_estimado * 0.15
        csll = lucro_estimado * 0.09
        pis = faturamento * 0.0065
        cofins = faturamento * 0.03
        total = irpj + csll + pis + cofins
        
        return {
            'regime': 'Lucro Real',
            'imposto_total': total,
            'aliquota_efetiva': total / faturamento if faturamento > 0 else 0,
            'detalhamento': {
                'IRPJ': irpj,
                'CSLL': csll,
                'PIS': pis,
                'COFINS': cofins
            }
        }

    def _recomendar_regime_tributario(self, cenarios: Dict) -> str:
        """Recomenda o melhor regime tributário baseado na simulação"""
        menor_imposto = float('inf')
        melhor_regime = ''
        
        for regime, dados in cenarios.items():
            if dados['imposto_total'] < menor_imposto:
                menor_imposto = dados['imposto_total']
                melhor_regime = regime
        
        return f"Recomendação: {melhor_regime.replace('_', ' ').title()} (menor carga tributária)"

    # =========================================================
    #   MÉTODOS DE ANÁLISE AVANÇADA
    # =========================================================

    def _analisar_tendencias_avancada(self, dados: pd.DataFrame) -> Dict:
        """Análise avançada de tendências"""
        try:
            if 'data_emissao' not in dados.columns or 'valor_total' not in dados.columns:
                return {'erro': 'Dados insuficientes para análise de tendências'}
            
            dados_temp = dados.copy()
            dados_temp['data_emissao'] = pd.to_datetime(dados_temp['data_emissao'])
            dados_mensais = dados_temp.groupby(dados_temp['data_emissao'].dt.to_period('M'))['valor_total'].sum()
            
            if len(dados_mensais) < 2:
                return {'erro': 'Dados insuficientes para análise temporal'}
            
            # Calcular métricas de tendência
            valores = dados_mensais.values
            crescimento_absoluto = valores[-1] - valores[0]
            crescimento_percentual = ((valores[-1] - valores[0]) / valores[0] * 100) if valores[0] > 0 else 0
            
            # Análise de volatilidade
            volatilidade = np.std(valores) / np.mean(valores) * 100 if len(valores) > 1 else 0
            
            return {
                'crescimento_absoluto': float(crescimento_absoluto),
                'crescimento_percentual': float(crescimento_percentual),
                'volatilidade': float(volatilidade),
                'tendencia_principal': 'crescente' if crescimento_percentual > 5 else 'estável' if crescimento_percentual >= -5 else 'decrescente',
                'previsao_proximo_mes': float(valores[-1] * 1.05)  # Simples projeção
            }
        except Exception as e:
            return {'erro': f"Erro na análise de tendências: {str(e)}"}

    def _gerar_benchmarking_setorial(self, setor: str) -> Dict:
        """Gera benchmarking com dados setoriais (dados simulados)"""
        benchmarks = {
            'comercio': {
                'ticket_medio_setor': 1500.00,
                'margem_media_setor': 0.25,
                'crescimento_setor': 0.08
            },
            'industria': {
                'ticket_medio_setor': 8500.00,
                'margem_media_setor': 0.18,
                'crescimento_setor': 0.12
            },
            'servicos': {
                'ticket_medio_setor': 3200.00,
                'margem_media_setor': 0.35,
                'crescimento_setor': 0.15
            }
        }
        
        return benchmarks.get(setor, {})

    def _identificar_alertas_riscos(self, dados: pd.DataFrame) -> List[Dict]:
        """Identifica alertas e riscos nos dados"""
        alertas = []
        
        try:
            # Verificar concentração de clientes
            if 'cnpj_destinatario' in dados.columns:
                top_clientes = dados['cnpj_destinatario'].value_counts().head(3)
                if len(top_clientes) > 0 and top_clientes.iloc[0] > len(dados) * 0.5:
                    alertas.append({
                        'tipo': 'CONCENTRACAO_CLIENTES',
                        'severidade': 'ALTA',
                        'descricao': 'Alta concentração em poucos clientes',
                        'recomendacao': 'Diversificar base de clientes'
                    })
            
            # Verificar sazonalidade excessiva
            if 'data_emissao' in dados.columns and 'valor_total' in dados.columns:
                dados_mensais = dados.groupby(pd.to_datetime(dados['data_emissao']).dt.month)['valor_total'].sum()
                if len(dados_mensais) > 1 and dados_mensais.std() / dados_mensais.mean() > 0.7:
                    alertas.append({
                        'tipo': 'SAZONALIDADE_EXCESSIVA',
                        'severidade': 'MEDIA',
                        'descricao': 'Alta sazonalidade no faturamento',
                        'recomendacao': 'Implementar estratégias para suavizar receita'
                    })
            
        except Exception as e:
            logger.error(f"Erro na identificação de alertas: {e}")
        
        return alertas

    # =========================================================
    #   MÉTODOS DE QUALIDADE DA INFORMAÇÃO (APRIMORADOS)
    # =========================================================

    def avaliar_qualidade_dados(self) -> Dict:
        """Avalia a qualidade dos dados no sistema"""
        try:
            dados = self.recuperar_dados(limite=1000)  # Amostra para análise
            
            if dados.empty:
                return {'sucesso': False, 'erro': 'Nenhum dado disponível para análise'}
            
            metricas = {
                'completude': self._calcular_completude(dados),
                'consistencia': self._verificar_consistencia(dados),
                'atualidade': self._verificar_atualidade(dados),
                'precisao': self._verificar_precisao(dados),
                'pontuacao_geral': 0
            }
            
            # Calcular pontuação geral ponderada
            metricas['pontuacao_geral'] = (
                metricas['completude'] * 0.3 + 
                metricas['consistencia'] * 0.25 + 
                metricas['atualidade'] * 0.25 +
                metricas['precisao'] * 0.2
            )
            
            return {
                'sucesso': True,
                'qualidade_dados': metricas,
                'recomendacoes_melhoria': self._gerar_recomendacoes_melhoria(metricas),
                'nivel_qualidade': self._classificar_nivel_qualidade(metricas['pontuacao_geral'])
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

    def _verificar_precisao(self, dados: pd.DataFrame) -> float:
        """Verifica precisão dos dados através de validações específicas"""
        try:
            validacoes = 0
            total_validacoes = 0
            
            # Validar CNPJ (formato básico)
            if 'cnpj_emitente' in dados.columns:
                cnpjs_validos = dados['cnpj_emitente'].apply(lambda x: len(str(x)) == 14)
                validacoes += cnpjs_validos.sum()
                total_validacoes += len(cnpjs_validos)
            
            # Validar valores positivos
            if 'valor_total' in dados.columns:
                valores_positivos = dados['valor_total'] > 0
                validacoes += valores_positivos.sum()
                total_validacoes += len(valores_positivos)
            
            return (validacoes / total_validacoes * 100) if total_validacoes > 0 else 100
        except:
            return 0

    def _classificar_nivel_qualidade(self, pontuacao: float) -> str:
        """Classifica o nível de qualidade dos dados"""
        if pontuacao >= 90:
            return "EXCELENTE"
        elif pontuacao >= 75:
            return "BOM"
        elif pontuacao >= 60:
            return "REGULAR"
        else:
            return "CRÍTICO"

    # =========================================================
    #   MÉTODOS ORIGINAIS MANTIDOS (COM CORREÇÕES)
    # =========================================================

    def recuperar_dados(self, filters=None, limite: int = None):
        """Recupera dados do banco de dados com filtros opcionais - VERSÃO CORRIGIDA"""
        if not self.testar_conexao():
            return pd.DataFrame()
            
        session = self.Session()
        try:
            query = """
            SELECT 
                nf.*,
                e.razao_social as razao_social_emitente,
                e.nome_fantasia as nome_fantasia_emitente,
                d.razao_social as razao_social_destinatario
            FROM notas_fiscais nf
            LEFT JOIN emitentes e ON nf.cnpj_emitente = e.cnpj
            LEFT JOIN destinatarios d ON nf.cnpj_destinatario = d.cnpj
            WHERE 1=1
            """
            
            params = {}
            
            if filters:
                if 'data_inicio' in filters:
                    query += " AND DATE(nf.data_emissao) >= :data_inicio"
                    params['data_inicio'] = filters['data_inicio']
                if 'data_fim' in filters:
                    query += " AND DATE(nf.data_emissao) <= :data_fim"
                    params['data_fim'] = filters['data_fim']
                if 'uf_emitente' in filters:
                    query += " AND nf.uf_emitente = :uf_emitente"
                    params['uf_emitente'] = filters['uf_emitente']
            
            query += " ORDER BY nf.data_emissao DESC"
            
            if limite:
                query += f" LIMIT {limite}"
            
            # CORREÇÃO: Usar connection.execute() em vez de pd.read_sql() para melhor compatibilidade
            result = session.execute(text(query), params)
            columns = result.keys()
            data = result.fetchall()
            
            if data:
                df = pd.DataFrame(data, columns=columns)
                
                # CORREÇÃO: Garantir que as colunas numéricas sejam do tipo correto
                if not df.empty:
                    numeric_columns = ['valor_total', 'valor_produtos', 'valor_desconto', 'valor_frete', 'valor_seguro', 
                                     'valor_despesas', 'valor_bc_icms', 'valor_icms', 'valor_bc_icms_st', 'valor_icms_st',
                                     'valor_ipi', 'valor_pis', 'valor_cofins']
                    
                    for col in numeric_columns:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Erro ao recuperar dados: {e}")
            return pd.DataFrame()
        finally:
            session.close()

    # =========================================================
    #   MÉTODOS DE SUPORTE PARA STREAMLIT
    # =========================================================

    def listar_abas_excel(self, arquivo):
        """Lista abas do Excel - método para Streamlit"""
        try:
            if hasattr(arquivo, 'read'):
                arquivo.seek(0)
                arquivo = BytesIO(arquivo.read())
            
            xls = pd.ExcelFile(arquivo)
            abas = xls.sheet_names
            return {'sucesso': True, 'abas': abas}
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

    def validar_estrutura_xls(self, arquivo, aba_nome):
        """Valida estrutura do Excel - método para Streamlit"""
        try:
            if hasattr(arquivo, 'read'):
                arquivo.seek(0)
                arquivo = BytesIO(arquivo.read())
            
            df = pd.read_excel(arquivo, sheet_name=aba_nome)
            
            # Validação básica
            colunas_encontradas = df.columns.tolist()
            colunas_minimas = ['numero', 'data_emissao', 'valor_total']
            
            colunas_presentes = [col for col in colunas_minimas if col in colunas_encontradas]
            
            return {
                'valido': len(colunas_presentes) >= 2,
                'total_registros': len(df),
                'colunas_encontradas': colunas_encontradas,
                'colunas_faltantes': [col for col in colunas_minimas if col not in colunas_encontradas]
            }
            
        except Exception as e:
            return {'valido': False, 'erro': str(e)}

    def processar_arquivo_xls(self, arquivo, aba_nome):
        """Processa arquivo Excel - método para Streamlit"""
        try:
            if hasattr(arquivo, 'read'):
                arquivo.seek(0)
                arquivo = BytesIO(arquivo.read())
            
            df = pd.read_excel(arquivo, sheet_name=aba_nome)
            
            # Simular processamento
            registros_validos = len(df.dropna())
            
            return {
                'sucesso': True,
                'registros_processados': len(df),
                'registros_validos': registros_validos,
                'mensagem': f'Processados {len(df)} registros com {registros_validos} válidos'
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}

    # =========================================================
    #   MÉTODOS AUXILIARES (IMPLEMENTAÇÕES FALTANTES) - CORRIGIDOS
    # =========================================================

    def _extrair_insights_rapidos(self, dados: pd.DataFrame) -> List[str]:
        """Extrai insights rápidos dos dados - VERSÃO CORRIGIDA"""
        insights = []
        
        try:
            if 'valor_total' in dados.columns:
                faturamento_total = dados['valor_total'].sum()
                insights.append(f"Faturamento total: R$ {faturamento_total:,.2f}")
                
                if len(dados) > 0:
                    ticket_medio = faturamento_total / len(dados)
                    insights.append(f"Ticket médio: R$ {ticket_medio:,.2f}")
            
            if 'data_emissao' in dados.columns:
                dados['data_emissao'] = pd.to_datetime(dados['data_emissao'])
                periodo = f"{dados['data_emissao'].min().strftime('%d/%m/%Y')} a {dados['data_emissao'].max().strftime('%d/%m/%Y')}"
                insights.append(f"Período analisado: {periodo}")
            
            if 'uf_emitente' in dados.columns:
                uf_mais_frequente = dados['uf_emitente'].mode()
                if len(uf_mais_frequente) > 0:
                    insights.append(f"Estado mais frequente: {uf_mais_frequente[0]}")
        
        except Exception as e:
            logger.error(f"Erro ao extrair insights: {e}")
            insights = ["Erro na extração de insights"]
        
        return insights

    def _calcular_crescimento_mensal(self, dados: pd.DataFrame) -> float:
        """Calcula crescimento mensal médio"""
        try:
            if 'data_emissao' not in dados.columns or 'valor_total' not in dados.columns:
                return 0.0
            
            dados_mensais = dados.groupby(pd.to_datetime(dados['data_emissao']).dt.to_period('M'))['valor_total'].sum()
            if len(dados_mensais) < 2:
                return 0.0
            
            crescimento = (dados_mensais.iloc[-1] - dados_mensais.iloc[0]) / dados_mensais.iloc[0] * 100
            return float(crescimento)
        except:
            return 0.0

    def _calcular_eficiencia_operacional(self, dados: pd.DataFrame) -> float:
        """Calcula indicador de eficiência operacional (simulado)"""
        try:
            if len(dados) == 0:
                return 0.0
            
            # Métrica simplificada - baseada na consistência temporal
            if 'data_emissao' in dados.columns:
                datas = pd.to_datetime(dados['data_emissao'])
                regularidade = 1 - (datas.diff().dt.days.std() / 30)  # Quanto menor a variação, melhor
                return max(0.0, min(1.0, float(regularidade))) * 100
            return 75.0  # Valor padrão
        except:
            return 50.0

    def _analisar_posicionamento_mercado(self, dados: pd.DataFrame, setor: str) -> str:
        """Analisa posicionamento no mercado"""
        try:
            if len(dados) == 0:
                return "Dados insuficientes para análise"
            
            ticket_medio = dados['valor_total'].mean() if 'valor_total' in dados.columns else 0
            volume = len(dados)
            
            if setor == 'comercio':
                if ticket_medio > 1000 and volume > 100:
                    return "Posicionamento: Premium - Alto ticket, boa volume"
                elif ticket_medio < 500:
                    return "Posicionamento: Massa - Baixo ticket, possível alto volume"
                else:
                    return "Posicionamento: Intermediário - Equilíbrio entre ticket e volume"
            else:
                return "Posicionamento: Especializado - Foco em valor agregado"
                
        except Exception as e:
            return f"Análise não disponível: {str(e)}"

    def _identificar_vantagens_competitivas(self, dados: pd.DataFrame) -> List[str]:
        """Identifica vantagens competitivas nos dados"""
        vantagens = []
        
        try:
            if 'valor_total' in dados.columns:
                variacao = dados['valor_total'].std() / dados['valor_total'].mean()
                if variacao < 0.3:
                    vantagens.append("Estabilidade nos valores praticados")
            
            if 'data_emissao' in dados.columns:
                frequencia = len(dados) / (pd.to_datetime(dados['data_emissao']).max() - pd.to_datetime(dados['data_emissao']).min()).days * 30
                if frequencia > 10:
                    vantagens.append("Alta frequência de transações")
        
        except Exception as e:
            logger.error(f"Erro ao identificar vantagens: {e}")
        
        return vantagens if vantagens else ["Vantagens competitivas em análise"]

    def _identificar_oportunidades_crescimento(self, dados: pd.DataFrame, setor: str) -> List[str]:
        """Identifica oportunidades de crescimento"""
        oportunidades = []
        
        try:
            if 'uf_emitente' in dados.columns:
                cobertura_uf = dados['uf_emitente'].nunique()
                if cobertura_uf < 5:
                    oportunidades.append("Expansão para novos estados")
            
            if setor == 'comercio':
                oportunidades.append("Diversificação de mix de produtos")
            elif setor == 'servicos':
                oportunidades.append("Expansão para serviços complementares")
        
        except Exception as e:
            logger.error(f"Erro ao identificar oportunidades: {e}")
        
        return oportunidades if oportunidades else ["Oportunidades em análise"]

    def _identificar_ameacas_riscos(self, setor: str) -> List[str]:
        """Identifica ameaças e riscos setoriais"""
        riscos = {
            'comercio': [
                "Sazonalidade nas vendas",
                "Concorrência de marketplaces",
                "Mudanças no comportamento do consumidor"
            ],
            'industria': [
                "Volatilidade nos custos de matéria-prima",
                "Dependência de fornecedores",
                "Regulamentações ambientais"
            ],
            'servicos': [
                "Dependência de profissionais-chave",
                "Sazonalidade na demanda",
                "Concorrência por preço"
            ]
        }
        
        return riscos.get(setor, ["Riscos setoriais em análise"])

    def _calcular_concentracao_clientes(self, dados: pd.DataFrame) -> float:
        """Calcula índice de concentração de clientes"""
        try:
            if 'cnpj_destinatario' not in dados.columns:
                return 0.0
            
            distribuicao = dados['cnpj_destinatario'].value_counts(normalize=True)
            # Índice Herfindahl (simplificado)
            indice = (distribuicao ** 2).sum()
            return float(indice * 100)  # Em percentual
        except:
            return 0.0

    def _avaliar_saude_financeira(self, dados: pd.DataFrame) -> str:
        """Avalia saúde financeira baseada nos dados"""
        try:
            if len(dados) == 0:
                return "INDEFINIDA"
            
            indicadores = []
            
            if 'valor_total' in dados.columns:
                # Crescimento
                if len(dados) > 1:
                    crescimento = self._calcular_crescimento_mensal(dados)
                    if crescimento > 10:
                        indicadores.append(2)
                    elif crescimento > 0:
                        indicadores.append(1)
                    else:
                        indicadores.append(0)
                
                # Estabilidade
                variacao = dados['valor_total'].std() / dados['valor_total'].mean()
                if variacao < 0.3:
                    indicadores.append(2)
                elif variacao < 0.6:
                    indicadores.append(1)
                else:
                    indicadores.append(0)
            
            if not indicadores:
                return "REGULAR"
            
            score = sum(indicadores) / len(indicadores)
            
            if score >= 1.5:
                return "EXCELENTE"
            elif score >= 1.0:
                return "BOA"
            elif score >= 0.5:
                return "REGULAR"
            else:
                return "ATENÇÃO"
                
        except:
            return "INDEFINIDA"

    # CORRIGIR também os métodos que retornam dicionários para garantir que valores numéricos sejam números, não strings
    def _calcular_faturamento_mensal(self, dados: pd.DataFrame) -> Dict:
        """Calcula faturamento mensal - VERSÃO CORRIGIDA"""
        try:
            if 'data_emissao' not in dados.columns or 'valor_total' not in dados.columns:
                return {}
                
            dados_temp = dados.copy()
            dados_temp['data_emissao'] = pd.to_datetime(dados_temp['data_emissao'])
            faturamento_mensal = dados_temp.groupby(dados_temp['data_emissao'].dt.to_period('M'))['valor_total'].sum()
            
            # Converter para float e string do período
            resultado = {}
            for periodo, valor in faturamento_mensal.items():
                resultado[str(periodo)] = float(valor)  # Garantir que é float, não string
                
            return resultado
        except Exception as e:
            logger.error(f"Erro ao calcular faturamento mensal: {e}")
            return {}

    def _calcular_evolucao_faturamento(self, dados: pd.DataFrame) -> Dict:
        try:
            evolucao = dados.groupby(pd.to_datetime(dados['data_emissao']).dt.to_period('M'))['valor_total'].sum()
            if len(evolucao) > 0:
                primeiro_mes = float(evolucao.iloc[0])
                ultimo_mes = float(evolucao.iloc[-1])
                variacao = ((ultimo_mes - primeiro_mes) / primeiro_mes * 100) if primeiro_mes > 0 else 0
                return {
                    'primeiro_mes': primeiro_mes,
                    'ultimo_mes': ultimo_mes,
                    'variacao_percentual': float(variacao)
                }
        except:
            pass
        return {'primeiro_mes': 0, 'ultimo_mes': 0, 'variacao_percentual': 0}

    def _analisar_sazonalidade(self, dados: pd.DataFrame) -> Dict:
        """Analisa sazonalidade - VERSÃO CORRIGIDA"""
        try:
            if 'data_emissao' not in dados.columns or 'valor_total' not in dados.columns:
                return {}
                
            dados_temp = dados.copy()
            dados_temp['mes'] = pd.to_datetime(dados_temp['data_emissao']).dt.month
            sazonalidade = dados_temp.groupby('mes')['valor_total'].mean()
            
            # Converter para int e float
            resultado = {}
            for mes, valor in sazonalidade.items():
                resultado[int(mes)] = float(valor)  # Garantir tipos corretos
                
            return resultado
        except Exception as e:
            logger.error(f"Erro ao analisar sazonalidade: {e}")
            return {}

    def _calcular_completude(self, dados: pd.DataFrame) -> float:
        try:
            total_celulas = dados.size
            celulas_nao_nulas = dados.count().sum()
            return (celulas_nao_nulas / total_celulas) * 100 if total_celulas > 0 else 0
        except:
            return 0

    def _verificar_consistencia(self, dados: pd.DataFrame) -> float:
        try:
            problemas = 0
            total_verificacoes = len(dados)
            
            if 'valor_total' in dados.columns:
                valores_negativos = len(dados[dados['valor_total'] < 0])
                problemas += valores_negativos
            
            return 100 - (problemas / total_verificacoes * 100) if total_verificacoes > 0 else 100
        except:
            return 0

    def _verificar_atualidade(self, dados: pd.DataFrame) -> float:
        try:
            if 'data_emissao' not in dados.columns:
                return 0
            
            data_mais_recente = pd.to_datetime(dados['data_emissao']).max()
            dias_desatualizado = (datetime.now() - data_mais_recente).days
            
            if dias_desatualizado <= 7:
                return 100
            elif dias_desatualizado <= 30:
                return 80
            elif dias_desatualizado <= 90:
                return 50
            else:
                return 20
        except:
            return 0

    def _gerar_recomendacoes_melhoria(self, metricas: Dict) -> List[str]:
        recomendacoes = []
        
        if metricas['completude'] < 90:
            recomendacoes.append("📊 Melhorar completude dos dados: Implementar validações obrigatórias")
        
        if metricas['consistencia'] < 95:
            recomendacoes.append("🔍 Aumentar consistência: Validar valores antes do armazenamento")
        
        if metricas['atualidade'] < 80:
            recomendacoes.append("⏰ Atualizar dados: Implementar processo de atualização regular")
        
        if metricas.get('precisao', 100) < 90:
            recomendacoes.append("🎯 Melhorar precisão: Implementar verificações de formato e consistência")
        
        return recomendacoes

    def _gerar_recomendacoes_estrategicas(self, dados: pd.DataFrame, setor: str) -> List[str]:
        """Gera recomendações estratégicas baseadas na análise"""
        recomendacoes = []
        
        try:
            # Análise básica para recomendações
            if 'valor_total' in dados.columns:
                faturamento_mensal = dados.groupby(pd.to_datetime(dados['data_emissao']).dt.to_period('M'))['valor_total'].sum()
                
                if len(faturamento_mensal) > 2 and faturamento_mensal.iloc[-1] < faturamento_mensal.iloc[-2]:
                    recomendacoes.append("📈 Desenvolver estratégias para reverter queda no faturamento")
                
                if dados['valor_total'].std() / dados['valor_total'].mean() > 0.5:
                    recomendacoes.append("🔄 Implementar segmentação de clientes para estabilizar receita")
            
            # Recomendações por setor
            if setor == 'comercio':
                recomendacoes.extend([
                    "🛍️ Implementar programa de fidelidade",
                    "📱 Desenvolver presença digital omnicanal"
                ])
            elif setor == 'industria':
                recomendacoes.extend([
                    "🏭 Otimizar cadeia de suprimentos",
                    "🔧 Implementar manutenção preventiva"
                ])
            elif setor == 'servicos':
                recomendacoes.extend([
                    "⭐ Focar em qualidade do serviço",
                    "🔄 Desenvolver serviços recorrentes"
                ])
        
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
        
        return recomendacoes if recomendacoes else [
            "📊 Coletar mais dados para análises específicas",
            "🔍 Realizar análise de mercado detalhada"
        ]

    # Métodos de simulação para setores específicos
    def _estimar_giro_estoque(self, dados: pd.DataFrame) -> float:
        """Estima giro de estoque (simulação)"""
        try:
            if len(dados) == 0:
                return 0.0
            return float(len(dados) / 6)  # Simulação: 6 meses
        except:
            return 0.0

    def _avaliar_complexidade_produtiva(self, dados: pd.DataFrame) -> str:
        """Avalia complexidade produtiva (simulação)"""
        try:
            if len(dados) == 0:
                return "BAIXA"
            
            variacao = dados['valor_total'].std() / dados['valor_total'].mean() if 'valor_total' in dados.columns else 0
            if variacao > 0.7:
                return "ALTA"
            elif variacao > 0.3:
                return "MÉDIA"
            else:
                return "BAIXA"
        except:
            return "INDEFINIDA"

    def _calcular_valor_agregado(self, dados: pd.DataFrame) -> float:
        """Calcula valor agregado (simulação)"""
        try:
            if len(dados) == 0:
                return 0.0
            return float(dados['valor_total'].mean() * 0.3)  # 30% como simulação
        except:
            return 0.0

    def _avaliar_recorrencia_faturamento(self, dados: pd.DataFrame) -> float:
        """Avalia recorrência do faturamento (simulação)"""
        try:
            if 'cnpj_destinatario' not in dados.columns:
                return 0.0
            
            clientes_unicos = dados['cnpj_destinatario'].nunique()
            total_transacoes = len(dados)
            
            if clientes_unicos == 0:
                return 0.0
            
            return float(total_transacoes / clientes_unicos)  # Transações por cliente
        except:
            return 0.0

    def _calcular_valor_medio_servico(self, dados: pd.DataFrame) -> float:
        """Calcula valor médio do serviço"""
        try:
            if 'valor_total' in dados.columns:
                return float(dados['valor_total'].mean())
            return 0.0
        except:
            return 0.0

    def testar_relatorio_json(self):
        """Testa se o relatório gera JSON válido"""
        relatorio = self.gerar_relatorio_setorial('comercio', {'inicio': '2024-01-01', 'fim': '2024-12-31'})
        
        if relatorio['sucesso']:
            try:
                import json
                # Tentar serializar para JSON
                json_str = json.dumps(relatorio['relatorio'], ensure_ascii=False, indent=2)
                print("✅ JSON válido gerado com sucesso!")
                return True
            except Exception as e:
                print(f"❌ Erro no JSON: {e}")
                return False
        return False

# =========================================================
#   FUNÇÃO DE CRIAÇÃO DO SISTEMA
# =========================================================

def criar_sistema_gerencial(gestor_bd=None):
    """Cria uma instância do sistema gerencial corrigido"""
    try:
        return SistemaGerencialNF(gestor_bd)
    except Exception as e:
        logger.error(f"Erro ao criar sistema gerencial: {e}")
        return None

# Teste do sistema
if __name__ == "__main__":
    sistema = criar_sistema_gerencial()
    if sistema and sistema.testar_conexao():
        print("✅ Sistema gerencial corrigido inicializado com sucesso!")
        
        # Testar assistente
        if DEEPSEEK_API_KEY:
            resposta = sistema.consultar_assistente("Quais são os regimes tributários disponíveis para uma empresa de comércio?")
            print("Resposta do assistente:", resposta.get('sucesso', False))
        
        # Testar relatório
        relatorio = sistema.gerar_relatorio_setorial('comercio', {'inicio': '2024-01-01', 'fim': '2024-12-31'})
        print("Relatório gerado:", relatorio.get('sucesso', False))
        
        # Testar JSON
        sistema.testar_relatorio_json()
    else:
        print("❌ Erro ao inicializar sistema gerencial")