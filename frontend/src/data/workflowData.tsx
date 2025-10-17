// src/data/workflowData.js

export const initialMessages = [
  {
    id: 1,
    sender: 'Agent',
    text: 'Olá! Sou o Agente Analista Fiscal. Para começar, por favor, utilize a seção "Novo Upload" para enviar seus dados.',
    time: '10:00',
  },
  { id: 2, sender: 'System', text: 'Upload do arquivo "NF_Janeiro.csv" iniciado.', time: '10:01' },
];

export const workflowSteps = [
  {
    key: 'upload',
    name: '1. Ingestão de Dados',
    desc: 'Arquivo recebido via FastAPI.',
    status: 'pending',
  },
  {
    key: 'cleaning',
    name: '2. Pré-processamento',
    desc: 'Agente de Tratamento limpando e padronizando o dataset (Pandas/Polars).',
    status: 'pending',
  },
  {
    key: 'validation',
    name: '3. Validação Fiscal',
    desc: 'Agente Validador cruzando dados com a Base Fiscal Externa.',
    status: 'pending',
  },
  {
    key: 'analysis',
    name: '4. Análise e Geração de Insights',
    desc: 'Agente Analista pronto para executar comandos e gerar relatórios.',
    status: 'pending',
  },
];
