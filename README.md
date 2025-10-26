# 🚀 Smart Financial Solutions: Sistema de Análise Financeira com Agentes de IA

O **Smart Financial Solutions** é uma aplicação completa de análise de dados financeiros, projetada como um sistema de **Orquestração de Agentes de Linguagem (LLMs)**. Ele utiliza uma arquitetura robusta com **FastAPI** (backend de IA) e **React/TypeScript** (frontend de chat), empacotada com **Docker Compose** para um *setup* rápido e confiável.

## 🧭 Índice (Table of Contents)

1.  [✨ Tecnologias Principais]()
2.  [📦 Instalação e Inicialização com Docker]()
3.  [🧠 Arquitetura do Backend (FastAPI / LangChain)]()
4.  [🖥️ Frontend Interativo (React / Vite)]()
5.  [⚙️ Controllers e Serviços]()
6.  [📂 Estrutura do Projeto (N-layers)]()
7.  [🔗 Endpoints Principais da API]()

-----

## ✨ Tecnologias Principais

| Componente | Tecnologias Principais | Foco Principal |
| :--- | :--- | :--- |
| **Backend** | **FastAPI**, **LangChain**, **Plotly**, **Pandas**, **TesseractOCR**, **SQLite** (com **SQLAlchemy**) | Alto desempenho, concorrência, orquestração de Agentes (LLMs), análise de dados, persistência de gráficos e gerenciamento de I/O de bloqueio. |
| **Frontend** | **React**, **TypeScript**, **Vite**, **Plotly.js** | Interface de chat intuitiva, gerenciamento de estado global, **renderização dinâmica de gráficos Plotly** e *handler* de upload. |
| **Infraestrutura**| **Docker** e **Docker Compose** | Empacotamento e orquestração de todos os serviços (Backend e Frontend). |

-----

## 📦 Instalação e Inicialização com Docker

Toda a aplicação é empacotada e executada através do **Docker Compose**, garantindo um *setup* rápido e confiável.

### Pré-requisitos

Para executar este projeto, você só precisa ter o **Docker** e o **Docker Compose** instalados na sua máquina. É recomendado ter no mínimo 3 GB de armazenamento livre.

### Configuração do Ambiente

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/smart-financial-solutions.git
    cd smart-financial-solutions
    ```

2.  **Configurar variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` e renomeie-o para `.env`. Preencha-o com suas credenciais, adicione uma chave de API do LangSmith para serviço de tracing dos agentes. Os valores padrões são o suficiente para o projeto funcionar.

    ```bash
    cp .env.example .env
    ```

    O arquivo `.env`, no mínimo:

    ```env
    # Rotas para o FastAPI
    N8N_WEBHOOK = "http://n8n:5678/webhook/report-agent"
    
    # Configurações da conexão com banco de dados
    DATABASE_URI="sqlite:///databases/db.sqlite"

    # Configurações do Langsmith para rastreamento das LLMs
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY="api_key"
    LANGSMITH_PROJECT="smart_financial_solutions"

    ```

### Inicialização da Aplicação

Para subir todos os serviços (Frontend, Backend FastAPI e o banco de dados), execute o seguinte comando no diretório raiz:

```bash
docker compose up --build
```

O argumento opcional `--build` garante que quaisquer atualizações no código sejam incorporadas nos containers.

| Serviço | URL |
| :--- | :--- |
| **Frontend (React)** | `http://localhost:8080` |
| **API Docs (FastAPI - Swagger UI)** | `http://localhost:8000/api/docs` |

> Se executado manualmente, fora do container Docker, a rota do frontend padrão é `http://localhost:5173`
-----

## 🧠 Arquitetura do Backend (FastAPI / LangChain)

O backend é assíncrono e foi construído para lidar com sessões concorrentes, com separação em Threads para descarregar operações síncronas de I/O (Pandas, OCR, SQLite).

### Fluxo de Análise e Visualização

A arquitetura de agentes é especializada para EDA:

1.  **Supervisor Agent (Orquestrador):** Recebe o *prompt* do usuário via `/api/prompt`. Decide se a pergunta é de dados (chama o `Data Analyst Agent` via `use_agent_tool`) ou se é de comunicação/geração de relatório.
2.  **Data Analyst Agent (Especialista):** Usa ferramentas especializadas (`data_analysis_tool`, `python_tool`) que acessam o DataFrame internamente, geram a figura **Plotly** e salvam seu JSON no banco de dados via `db_services`.
3.  **Eficiência de Tokens:** O Agente retorna apenas o **`graph_id`** e um **`metadata`** (resumo textual da análise) para o Supervisor. O metadata é usado para o comentário do gráfico, **otimizando o consumo de tokens**.

-----

## 🖥️ Frontend Interativo (React / Vite)

O frontend é um *single-page application* (SPA) interativo que provê a experiência conversacional e de upload.

| Funcionalidade | Detalhe Técnico |
| :--- | :--- |
| **Interface Conversacional** | Chatbot que responde perguntas, aceita upload de arquivos e gerencia o histórico de mensagens. |
| **Gerenciamento de Estado** | Utiliza Context API e `ServerContext` para gerenciar o estado da aplicação. |
| **Renderização de Gráficos** | O frontend recebe o `graph_id` do backend, requisita o JSON do Plotly via `/api/graphs/{graph_id}` e renderiza o gráfico de forma dinâmica com **Plotly.js**. |
| **Upload Assíncrono** | Gerencia o upload de arquivos de dados (CSV/XLSX/ZIP) e imagens (JPEG, PNG, TIFF, BMP), utilizando o canal **WebSocket** para mostrar o status de processamento em tempo real. |
| **Configuração Dinâmica** | A `ConfigPage` permite o mapeamento e alteração dos modelos LLM (ex: `llama3-8b`) para tarefas/agentes específicas (`SUPERVISOR`, `DATA ANALYST`), enviando a configuração via `/api/change-model`. |

-----

## ⚙️ Controllers e Serviços

### Camada de Controllers

| Controller | Responsabilidade Principal |
| :--- | :--- |
| **`agent_controller`** | Trata todas as requisições relacionadas à lógica do Agente (Upload, Prompt, Configurações). |
| **`db_controller`** | Gerencia as rotas de acesso ao banco de dados para recursos persistidos, como a busca do JSON de gráficos (`/api/graphs`). |
| **`websocket_controller`** | Gerencia a conexão WebSocket (`/api/websocket/session_id`) para enviar atualizações de status em tempo real, isoladas por sessão. |

### Camada de Services

| Service | Responsabilidade Principal |
| :--- | :--- |
| **`data_processing`** | Gerencia o upload, I/O síncrono descarregado, processamento Pandas e extração via TesseractOCR. |
| **`chat_model`** | Gerencia o **Pool de Agentes**, sessões isoladas, chaves de API por sessão, o fluxo de mensagens ao Supervisor e a limpeza de objetos por inatividade (TTL). |
| **`dn_services`** | Responsável pela inicialização do DB (`init`) e todas as operações de manipulação de dados, incluindo a persistência de JSONs de gráficos gerados. |

### Ferramentas (Tools) do Agente

As ferramentas são o mecanismo principal para a execução de ações especializadas e para o roteamento do fluxo de trabalho:

| Tool | Agente(s) de Uso | Função Principal |
| :--- | :--- | :--- |
| **`data_analisys_tool`** | Data Analyst Agent | Executa análises, gera figuras Plotly e salva o JSON do gráfico via `db_services`. |
| **`report_gen_tool`** | Report Generation Agent | Cria relatórios em formato PDF e gerencia o envio via e-mail. |
| **`use_agent_tool`** | Supervisor Agent | É o mecanismo de roteamento, usado para chamar e iniciar a execução de outros sub-agentes (Engineer, Analyst, Report Gen). |
| **`python_tool`** | Data Analyst Agent | Permite a execução segura de blocos de código Python gerados pela LLM para manipulações avançadas de dados. |
| **`utils_tool`** | Todos os Agentes | Funções auxiliares de propósito geral (ex: `get_current_datetime`). |

-----

## 📂 Estrutura do Projeto (N-layers)

```
.
├── .env.example              # Exemplo de arquivo com as variáveis de ambiente
├── compose.yml               # Orquestração dos serviços Docker (Backend, Frontend, DB)
├── Dockerfile                # Dockerfile para o backend (FastAPI)
├── Dockerfile.frontend       # Dockerfile para o frontend (React)
├── src/                      # Código Fonte do Backend
│   ├── main.py                     # Instância do FastAPI e montagem das rotas
│   ├── data/                       # Configurações estáticas (Status, ModelTask)
│   ├── agents/                     # Definição e lógica de todos os Agentes
│   │   ├── base_agent.py           # Classe Base e inicialização de modelos LLM
│   │   └── supervisor_agent.py     # Lógica de Roteamento
│   ├── services/                   # Lógica de negócio (Chat, Data Processing, DB)
│   │   └── ... (chat_model_service.py, data_processing_service.py, db_services.py, session_manager.py)
│   ├── controllers/                # Camadas de comunicação (Rotas API e WebSockets)
│   │   └── ... (agent_controller.py, db_controller.py, websocket_controller.py)
│   ├── schemas/                    # Modelos Pydantic (validação de I/O)
│   └── tools/                      # Ferramentas Assíncronas (Tools) dos Agentes
│       └── ... (data_analisys_tool.py, report_gen_tool.py, use_agent_tool.py, python_tool.py, utils_tool.py)
└── README.md
```

-----

## 🔗 Endpoints Principais da API

| Método | Endpoint | Controller | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | **`/api/agent-info`** | `AgentController` | Recebe informações sobre os **modelos disponíveis** e as **tarefas de agente**. |
| `POST` | **`/api/upload`** | `AgentController` | Faz o upload e processa arquivos de dados estruturados (**CSV, XLSX, ZIP**). |
| `POST` | **`/api/upload/image`** | `AgentController` | Envia imagem/PDF para processamento via **OCR** (JPEG, PNG, TIFF, BMP). |
| `POST` | **`/api/prompt`** | `AgentController` | Envia a mensagem do usuário (`prompt`) para o **SupervisorAgent**. |
| `POST` | **`/api/send-key`** | `AgentController` | Registra a chave de API na sessão do usuário. |
| `GET` | **`/api/graphs/{graph_id}`** | `DBController` | Busca a estrutura **JSON de um gráfico** (Plotly) persistido. |
| `PUT` | **`/api/change-model`** | `AgentController` | Altera o modelo LLM ativo para a tarefa/agente especificada. |
| `GET` | `/ws/v1/status/{session_id}` | `WebSocketController` | Conexão WebSocket para atualizações de status em tempo real. |
