# 🚀 Smart Financial Solutions: Sistema de Análise Financeira com Agentes de IA

O **Smart Financial Solutions** é uma aplicação completa de análise de dados financeiros, projetada como um sistema de **Orquestração de Agentes de Linguagem (LLMs)**. Ele utiliza uma arquitetura robusta com **FastAPI** (backend de IA) e **React/TypeScript** (frontend de chat), empacotada com **Docker Compose** para um *setup* rápido e confiável.

<img width="1349" height="650" alt="interface_frontend" src="https://github.com/user-attachments/assets/797038d4-d823-455f-82af-b7484fd25593" />


## 🧭 Índice (Table of Contents)

1.  [✨ Tecnologias Principais](#-tecnologias-principais)
2.  [📦 Instalação e Inicialização](#-instala%C3%A7%C3%A3o-e-inicializa%C3%A7%C3%A3o)
    * [Pré-requisitos](#pr%C3%A9-requisitos)
    * [Inicialização Manual](#inicializa%C3%A7%C3%A3o-da-aplica%C3%A7%C3%A3o-manual)
    * [Inicialização com Docker](#inicializa%C3%A7%C3%A3o-da-aplica%C3%A7%C3%A3o-com-docker)
3.  [🧠 Arquitetura do Backend (FastAPI / LangChain)](#-arquitetura-do-backend-fastapi--langchain)
4.  [🖥️ Frontend Interativo (React / Vite)](#%EF%B8%8F-frontend-interativo-react--vite)
5.  [⚙️ n8n (Workflow Automation)](#%EF%B8%8F-n8n-workflow-automation)
6.  [⚙️ Controllers e Serviços](#%EF%B8%8F-controllers-e-servi%C3%A7os)
7.  [📂 Estrutura do Projeto (N-layers)](#-estrutura-do-projeto-n-layers)
8.  [🔗 Endpoints Principais da API](#-endpoints-principais-da-api)
9.  [Licensing](#-licensing)

-----

## ✨ Tecnologias Principais

| Componente | Tecnologias Principais | Foco Principal |
| :--- | :--- | :--- |
| **Backend** | **FastAPI**, **LangChain**, **Plotly**, **Pandas**, **TesseractOCR**, **SQLite** (com **SQLAlchemy**) | Alto desempenho, concorrência, orquestração de Agentes (LLMs), análise de dados, persistência de dados e gerenciamento de I/O. |
| **Frontend** | **React**, **TypeScript**, **Vite**, **Plotly.js** | Interface de chat intuitiva, gerenciamento de estado global, **renderização dinâmica de gráficos Plotly** e *handler* de upload. |
| **Automação de mensagens** | **Python** | Fluxo de envio dos relatórios em PDF gerados durante o uso dos agentes.
| **Infraestrutura**| **Docker** e **Docker Compose** | Empacotamento e orquestração de todos os serviços (Backend e Frontend). |

-----

## 📦 Instalação e Inicialização

Toda a aplicação é empacotada e executada através do **Docker Compose**, garantindo um *setup* rápido e confiável. Porém, o usuário tem a opção  de clonar o projeto e inserir os comandos manualmente para colocar o projeto em execução.

### Pré-requisitos

Para executar este projeto, você só precisa ter o [**Docker**](https://www.docker.com/products/docker-desktop/) instalados na sua máquina e ter no mínimo 4 GB de armazenamento livre para a aplicação.

> **Considerações Importantes**: na primeira execução do projeto, todas as imagens e dependências serão baixadas para o seu funcionamento. Esse processo, a depender da conexão do usuário, pode levar um tempo médio de 10 - 20 min. Em execuções posteriores, as dependências já foram cacheadas e a execução é mais rápida.

### Configuração do Ambiente

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/smart-financial-solutions.git
    cd smart-financial-solutions
    ```
    > Uma alternativa mais simples é clicar em `<> Code` e baixar o o ZIP do projeto, com a desvantagem de não sincronizar com o repositório remoto.

2.  **Configurar variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` e renomeie-o para `.env`. Preencha-o com suas credenciais, adicione uma chave de API do LangSmith para serviço de tracing dos agentes. Os valores padrões são o suficiente para o projeto funcionar.

    ```bash
    cp .env.example .env
    ```

    O arquivo `.env`, no mínimo:

    ```env
    # Credenciais para servidor de email
    SENDER_EMAIL="seu_email@gmail.com"
    SENDER_PASSWORD="sua_credencial_de_app"
   
    # Configurações do Qdrant
    QDRANT_URL="http://qdrant:6333" # <-- Trocar a URL para usar o serviço do Qdrant, se não for via Docker
    
    # Configurações da conexão com banco de dados
    DATABASE_URI="sqlite:///databases/db.sqlite"

    # Configurações do Langsmith para rastreamento das LLMs
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY="api_key"
    LANGSMITH_PROJECT="smart_financial_solutions"

    ```

### Inicialização da Aplicação Manual
Se optar pela inicialização manual, o projeto será executado em modo de desenvolvimento. A conexão com Qdrant Vector Store deve ser modificada para a sua instancia, provavelmente no Qdrant Cloud. 

Você precisará ter o [Node.js-20](https://nodejs.org/pt) e o [Python-3.12](https://www.python.org/) instalados. Para começar acesse o diretório raiz do projeto e abra terminais nos diretórios `frontend` e `backend`.

* **Windows**: Abra um terminal pesquisando por CMD na barra de endereço (`C:\user\`) na pasta do projeto e pressionando `ENTER` ou pesquisando por CMD no menu Windows e navegando até o projeto com `cd pasta1\pasta2\pasta3`.
* **Linux**: Abra um terminal de preferência e navegue com o comando `cd diretorio1/diretorio2/diretorio3`.

Insira o seguinte comando no diretório `frontend`:

```bash
npm run dev
```

No diretório `backend`, insira os comandos a seguir no terminal

```bash
# crie um ambiente virtual com:
python -m venv .venv
# ou outro gerenciador de ambientes virtuais e ative-o com:
.venv/Scripts/activate  # Windows
source .venv/bin/activate   # Linux

# Faça a instalação das dependẽncias com:
pip install -r requirements.txt
# ou com um gerenciador de pacotes de sua preferência.

# Execute o projeto com
`fastapi dev src/main.py`
```

Acesse os serviços nas rotas retornadas pelo terminal.

### Inicialização da Aplicação com Docker

Para subir todos os serviços (Frontend, Backend FastAPI e o n8n), execute o comando adiante no diretório raiz. Tenha certeza de estar no diretório que contém o arquivo `compose.yml`:

```bash
docker compose up --build
```

O argumento opcional `--build` garante que quaisquer atualizações no código sejam incorporadas nos containers, necessário quando houver mudanças no projeto.

| Serviço | URL |
| :--- | :--- |
| **Frontend (React)** | `http://localhost:8080` |
| **API Docs (FastAPI - Swagger UI)** | `http://localhost:8000/api/docs` |
| **n8n** | `http://localhost:5678` |

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

## ⚙️ n8n (Workflow Automation)

O projeto utiliza um serviço de automação de workflow n8n para gerenciar a etapa de comunicação e envio de relatórios.

### Fluxo do Relatório PDF

* O Report Generation Agent usa a ferramenta de criação de relatórios `report_gen_tool` para criar um arquivo PDF.

* Após a criação do PDF, o Agente envia o arquivo e os metadados (incluindo o endereço de e-mail do destinatário) para um webhook do serviço n8n.

* O n8n atua como uma camada de middleware de comunicação, orquestrando o envio do relatório PDF por e-mail, de forma assíncrona.

O serviço n8n é integrado ao projeto via Docker Compose, garantindo que ele suba junto com o Backend e o Frontend, e que o Backend possa se comunicar com seu endpoint interno (`http://n8n:5678/webhook/report-gen`).

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
| **`db_services`** | Responsável pela inicialização do DB (`init`) e todas as operações de manipulação de dados, incluindo a persistência de JSONs de gráficos gerados. |

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

```bash
.
├── .env.example              # Exemplo de arquivo com as variáveis de ambiente
├── compose.yml               # Orquestração dos serviços Docker (Backend, Frontend, DB)
├── Dockerfile                # Dockerfile para o backend (FastAPI)
├── Dockerfile.frontend       # Dockerfile para o frontend (React)
├── backend/                  # Código Fonte do Backend
│   ├── src/
│       ├── main.py                   # Ponto de inicío do App
│       ├── data/                     # Configurações estáticas (Status, ModelTask)
│       ├── agents/                   # Definição e lógica de todos os Agentes
│       │   └── ...                   
│       ├── services/                 # Lógica de negócio (Chat, Data Processing, DB)
│       │   └── ...                   
│       ├── controllers/              # Camadas de comunicação (Rotas API e WebSockets)
│       │   └── ...
│       ├── schemas/                  # Modelos Pydantic (validação de I/O)
│       └── tools/                    # Ferramentas Assíncronas (Tools) dos Agentes
│           └── ...
│ 
├── frontend/                 # Código Fonte do Frontend (React / TypeScript / Vite)
│   ├── public/               # Arquivos estáticos servidos diretamente
│   └── src/                  
│       ├── assets/           # Recursos estáticos (imagens, ícones)
│       ├── components/       # Componentes reutilizáveis da UI
│       ├── context/          # Gerenciamento de Estado Global (Context API)
│       ├── data/             # Dados estáticos ou configurações do cliente
│       ├── hooks/            # Funções de lógica reutilizáveis (Custom Hooks)
│       ├── pages/            # Componentes de Rotas/Telas Principais
│       ├── schemas/          # Tipagem (Interfaces TS) e validação de dados
│       ├── App.css
│       ├── App.tsx
│       ├── AppContent.tsx
│       ├── index.css
│       └── main.tsx
│   ├── .eslintrc.config.js
│   ├── index.html
│   ├── package.json
│   ├── README.md
│   ├── tsconfig.json
│   └── vite.config.ts
└── README.md                 # README principal do projeto
```

-----

## 🔗 Endpoints Principais da API

| Método | Endpoint | Controller | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | **`/api/agent-info`** | `agent_controller` | Recebe informações sobre os **modelos disponíveis** e as **tarefas de agente**. |
| `POST` | **`/api/upload`** | `agent_controller` | Faz o upload e processa arquivos de dados estruturados (**CSV, XLSX, ZIP**). |
| `POST` | **`/api/upload/image`** | `agent_controller` | Envia imagem para processamento via **OCR** (JPEG, PNG, TIFF, BMP). |
| `POST` | **`/api/prompt`** | `agent_controller` | Envia a mensagem do usuário (`prompt`) para o **SupervisorAgent**. |
| `POST` | **`/api/send-key`** | `agent_controller` | Registra a chave de API na sessão do usuário. |
| `GET` | **`/api/graphs/{graph_id}`** | `db_controller` | Busca a estrutura **JSON de um gráfico** (Plotly) persistido. |
| `PUT` | **`/api/change-model`** | `agent_controller` | Altera o modelo LLM ativo para a tarefa/agente especificada. |
| `GET` | `/api/websocket/{session_id}` | `websocket_controller` | Conexão WebSocket para atualizações de status em tempo real. |

## Licensing

* Esse projeto utiliza modelos de embeddings `jina-embeddings-v3` (via FastEmbed), licenciado sob a Creative Commons Atribuição-Não Comercial 4.0 Internacional (CC BY-NC 4.0). Crédito: [Jina AI](https://jina.ai/models) e [Licença CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.pt_BR).
