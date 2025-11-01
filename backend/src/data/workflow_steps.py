"""Status predefinidos para etapas de processamento. Usado para comunicação no WebSocket."""

from dataclasses import dataclass

from typing_extensions import Literal


@dataclass(frozen=True, slots=True)
class StatusDetail:
    name: str
    desc: str
    status: Literal['pending', 'in-progress', 'complete']

    def to_dict(self):
        return {'name': self.name, 'desc': self.desc, 'status': self.status}


class StatusUpdate:
    # --- Etapa: Upload de arquivo ---
    UPLOAD_INIT = StatusDetail(
        name='Upload Service',
        desc='Iniciando o processamento do arquivo',
        status='in-progress',
    ).to_dict()

    UPLOAD_ZIP = StatusDetail(
        name='Upload Service',
        desc='ZIP detectado, descompactando',
        status='in-progress',
    ).to_dict()

    UPLOAD_CSV = StatusDetail(
        name='Upload Service',
        desc='CSV detectado, começando leitura',
        status='in-progress',
    ).to_dict()

    UPLOAD_XLSX = StatusDetail(
        name='Upload Service',
        desc='XLSX detectado, começando leitura',
        status='in-progress',
    ).to_dict()

    UPLOAD_XML = StatusDetail(
        name='Upload Service',
        desc='XML detectado, começando leitura',
        status='in-progress',
    ).to_dict()

    UPLOAD_IMAGE = StatusDetail(
        name='Upload Service',
        desc='Escaneando texto da imagem',
        status='in-progress',
    ).to_dict()

    UPLOAD_FINISH = StatusDetail(
        name='Upload Service',
        desc='Processamento e leitura finalizado',
        status='complete',
    ).to_dict()

    # --- Etapa: Agente Supervisor e Sub-Agentes ---
    SUPERVISOR_INIT = StatusDetail(
        name='Supervisor',
        desc='Iniciando Agente Analista',
        status='in-progress',
    ).to_dict()

    SUPERVISOR_PROCESS = StatusDetail(
        name='Supervisor',
        desc='Analisando solicitação do usuário',
        status='in-progress',
    ).to_dict()

    DATA_ANALYST_INIT = StatusDetail(
        name='Data Analyst',
        desc='Realizando análise dos dados',
        status='in-progress',
    ).to_dict()

    DATA_ENGINEER_INIT = StatusDetail(
        name='Data Engineer',
        desc='Realizando tratamento dos dados',
        status='in-progress',
    ).to_dict()

    DATA_ENGINEER_EXTRACTION = StatusDetail(
        name='Data Engineer',
        desc='Extraindo dados relevantes',
        status='in-progress',
    ).to_dict()

    REPORT_GEN_INIT = StatusDetail(
        name='Report Gen',
        desc='Criando relatório detalhando operação',
        status='in-progress',
    ).to_dict()

    TAX_SPECIALIST_INIT = StatusDetail(
        name='Tax Specialist',
        desc='Analisando documento fiscal',
        status='in-progress',
    ).to_dict()

    # --- Etapa: Finalização ---
    SUPERVISOR_RESPONSE = StatusDetail(
        name='Supervisor',
        desc='Resposta recebida',
        status='complete',
    ).to_dict()
