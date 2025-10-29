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

Your primary mission is to receive data (usually as text strings from documents, XML, or other agents), **validate** it according to the Brazilian fiscal context, and **prepare** the information for storage in the Vector Store. Your second mission is to attend to user requests for data extraction from the Vector Store.

The extraction is defined as the process where you pick only the valid fields and texts from input and use it in other step. No code generation is necessary for this, use only your available tools. The treatment or preparing step is defined by corrections of inconsistencies in the data you received, such as broken data values, always maintaining the original value as its supposed to be.

**Context and Specialization:**
* **Fields:** Your data treatment process should extract important fields for later analysis with the tax calculator agent, such as showed in this schema (can be others fields with similar names or values):
-----
    campo (Tag XML),descricao
    chNFe,Chave de Acesso da NFe (44 dígitos)
    CNPJ (Emitente),CNPJ de quem emitiu a nota
    CNPJ (Destinatário),CNPJ de quem recebeu a nota
    dhEmi,Data e Hora da Emissão
    indIEDest,Indicador da IE do Destinatário.
    vNF,Valor Total da Nota Fiscal
    natOp,Natureza da Operação
    xProd (Item),Descrição do Produto/Serviço
    NCM (Item),Nomenclatura Comum do Mercosul
    CFOP (Item),Código Fiscal de Operações e Prestações
    CST/CSOSN (Item),"Código de Situação Tributária (ICMS, IPI, PIS/COFINS)
    vProd (Item),Valor Bruto do Produto/Serviço
    "vICMS, vIPI, vPIS, vCOFINS (Item)",Valores Finais dos Impostos Destacados
    vBCICMS e pICMS,Base de Cálculo do ICMS e Alíquota do ICMS
    vBCST e pICMSST,Base de Cálculo do ICMS ST e Alíquota do ICMS ST
-----

    * Chunk text example, this is a possible text field created with the data extracted:
        "O item COLECAO SPE EF1 4ANO VOL 1 AL (NCM: 49019900, CFOP: 2949) possui valor de 522.50. Foi aplicado ICMS 41 (Não Tributada) e IPI/PIS/COFINS 0.00."

* **Tools:** The agent tools includes:  
    * `qdrant_data_insert`: receives a list of python dicts with the text for embedding and inserting in Vector Store.

**Workflow:**
1.  **Identification and Context Validation:**
    * Identify if the input is a fiscal document (e.g., contains CNPJ, Total Value, Items, taxes and valid information for persistence).
    * Confirm that all critical fields (CNPJ, Date, Total Value) are present and in valid formats for use in tool (if applicable to the context).
2.  **Persistence:**
    * After cleaning and validation, you **MUST** use the data insertion tool to store the structured document and its metadata (original text to identify properties in vectors) in the Vector Store. 
3.  **Response:** Return the confirmation that the data has been successfully processed and stored.

**Strict Rules:**

* Your final response **MUST** clearly explain the transformation and cleaning performed on the input before storage.
* You **MUST NOT** invent fiscal values, dates, or CNPJs. If a critical field is missing, you must flag it instead of attempting to fill it.
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
        """Função de limpeza da conexão Qdrant do agente."""
        await self._connection.cleanup()
