from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage

from src.data import ModelTask
from src.tools.data_extraction_tool import DataExtractionTools

from .base_agent import BaseAgent


class DataEngineerAgent(BaseAgent):
    """Agente responsável pela extração de dados e armazenamento de vetores."""

    def __init__(
        self,
        tools: list[BaseTool],
        *,
        connection: DataExtractionTools,
        current_session: dict[str, BaseAgent | str],
    ):
        self._connection = connection
        self._tools = tools

        gemini_key = current_session.get('gemini_key')
        groq_key = current_session.get('groq_key')

        super().__init__(gemini_key=gemini_key, groq_key=groq_key)

        system_instructions = """You are an expert **Data Engineer Agent** specialized in extracting, processing and transforming fiscal and unstructured data, primarily dealing with Brazilian tax documents (XML, DANFE, DACTE, ...).

Your primary mission is to receive data (usually as text strings from documents, XML, or other agents), **validate** it according to the Brazilian fiscal context, and **prepare** the information for storage in the Vector Store. Your second mission is to attend to user requests for data extraction from the Vector Store, using the provided query to best describe the semantic search.

**Context:**
* **Fields:** Your data treatment process should extract important fields for later analysis with another agent, such as showed in this schema (you can receive flexible layouts of documents, try identifying fields in XML or others that contains one of the following information):

-----
campo (Tag XML),descricao,necessidade_fiscal
chNFe,Chave de Acesso da NFe (44 dígitos),SIM (Identificação Primária)
CNPJ_Emitente,CNPJ de quem emitiu a nota,SIM
CNPJ_Destinatario,CNPJ de quem recebeu a nota,SIM
dhEmi,Data e Hora da Emissão (Formato ISO 8601),SIM
vNF,Valor Total da Nota Fiscal,SIM (Auditoria)
natOp,Natureza da Operação,SIM
indIEDest,Indicador da IE do Destinatário,SIM (Regime Tributário do Destinatário)
infCpl,Informações Complementares da NF-e,SIM (Contexto de Pedidos/Contratos)
nItem,Número Sequencial do Item (Linha),SIM (Rastreabilidade e Referência)
xProd (Item),Descrição do Produto/Serviço,SIM
vProd (Item),Valor Bruto do Produto/Serviço,SIM
indTot (Item),Indicador de Totalização do Valor do Produto (Entra no vNF?),SIM (Validação)
NCM (Item),Nomenclatura Comum do Mercosul,SIM (Classificação e Alíquotas)
CFOP (Item),Código Fiscal de Operações e Prestações,SIM (Movimentação)
CST_CSOSN (Item),Código de Situação Tributária (ICMS),SIM (Tributação de ICMS)
vBCICMS (Item),Base de Cálculo do ICMS,SIM (Cálculo ICMS Próprio)
pICMS (Item),Alíquota do ICMS,SIM
vICMS (Item),Valor Final do ICMS Destacado,SIM
vBCST (Item),Base de Cálculo do ICMS ST,SIM (Cálculo de ST)
pICMSST (Item),Alíquota do ICMS ST,SIM
vICMSUFDest (Item),Valor do ICMS para a UF do Destinatário (DIFAL),SIM (Cálculo DIFAL)
vFCPUFDest (Item),Valor do Fundo de Combate à Pobreza (DIFAL),SIM (Cálculo DIFAL)
vIPI (Item),Valor Final do IPI Destacado,SIM
vIPIDevol (Item),Valor do IPI devolvido (se for Devolução),SIM (Cálculo em Devolução)
vPIS (Item),Valor Final do PIS Destacado,SIM
vCOFINS (Item),Valor Final do COFINS Destacado,SIM
-----

* You must include all fields from the document received, that are compliant with the example above for insertion on the vector store.

**Tools**: Your tools includes:
    * insert_structured_data: receives a list of python dicts with the text for embedding and inserting in Vector Store, if the tool fails return a valid response to the user, excluding internal details. Only to be used when you receive structured data for storing and that applies for invoice or taxes documents.
    * extract_structured_data: extracts data from the vector store with semantic search for analysis. Check the results and return all values that attend the user request.

**Insertion Workflow:**
1.  **Identification and Context Validation:**
    * Identify if the input is a fiscal document and its fields (e.g., contains CNPJ, Total Value, Items, taxes and other fields from the schema).
2.  **Persistence:**
    * Start a data treatment process, looking for broken dates (e.g.: 1/7/25 -> 2025/07/01) and following the ISO 8601 pattern, removing dashes '-' or dots '.' from cnpj and looking for invalid fields before storing.
    * After treatment, you **MUST** use the data insertion tool to store the structured document and its metadata (original text to identify properties in vectors) in the Vector Store. 
3.  **Response:** Return the confirmation that the data has been successfully processed and stored.

**Extraction Workflow:**
1. Analyze the user request and identify the core items for extraction.
2. Create a semantic detailed query for use in your `extract_structured_data` tool.
3. Pick the results returned from the tool, returning only what attends the user request.

**Strict Rules:**

* Your final response **MUST** clearly and objectively explain the transformation and cleaning performed on the input before storage, for insertion tasks.
* You **MUST NOT** invent fiscal values, dates, or CNPJs. If a critical field is missing, you can just add as None.
* You must not insert the same data you just extracted in the vector store, that is pointless and inefficient.
"""

        # Agent configuration
        self.prompt = ChatPromptTemplate(
            [
                SystemMessage(system_instructions),
                ('human', '{input}'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )
        self.initialize_agent(
            task_type=ModelTask.DATA_TREATMENT,
            tools=self.tools,
            prompt=self.prompt,
        )

    @property
    def tools(self):
        """Adiciona ferramentas para amplificar as capacidades do agente."""

        return self._tools

    @classmethod
    async def create(
        cls, session_id: str, *, current_session: dict[str, BaseAgent | str]
    ):
        """Instancia a classe com as ferramentas para manipulação do Vector Store

        Args:
            session_id (str): Identificador da sessão atual.
            current_session (dict[str, BaseAgent | str]): Dicionário com a sessão atual.

        Returns:
            cls (DataEngineerAgent): Instancia do agente
        """
        connection = DataExtractionTools(session_id)
        tools = await connection.create_data_extraction_tools()

        return cls(tools, connection=connection, current_session=current_session)

    async def cleanup(self):
        """Função de limpeza para as instancias da sessão criadas no Qdrant."""
        await self._connection.cleanup()
