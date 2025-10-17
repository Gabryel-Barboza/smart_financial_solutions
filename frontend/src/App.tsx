import { useState } from 'react';

import './App.css';

import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/NavBar';
import ChatPanel from './components/ChatPanel';

import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';

import { initialMessages, workflowSteps } from './data/workflowData';

import useAgentWorkflow from './hooks/useAgentWorkflow';

/**
 * Componente principal da aplicação.
 * Orquestra o estado e o layout.
 */
const App = () => {
  // --- Estado do Aplicativo ---
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [selectedNav, setSelectedNav] = useState('Dashboard');

  // --- Lógica de Workflow (Custom Hook) ---
  const { currentStep, isProcessing, handleUpload: startWorkflow } = useAgentWorkflow(setMessages);

  // --- Funções de Handler ---

  // Simula o upload, inicia o workflow e navega para o Dashboard
  const handleUpload = (fileName) => {
    startWorkflow(fileName);
    setSelectedNav('Dashboard'); // Navega para o Dashboard após iniciar o workflow
  };

  // Envia a mensagem no chat (função completa)
  const handleSendMessage = () => {
    if (!input.trim() || isProcessing) return;

    const newMessage = {
      id: Date.now(),
      sender: 'User',
      text: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, newMessage]);
    setInput('');

    // Simula a resposta do Agente (LLM)
    setTimeout(() => {
      const agentResponse = {
        id: Date.now() + 1,
        sender: 'Agent',
        text: `Compreendido. Executando a análise: "${newMessage.text}". Gerando resposta/gráfico... (Mock de resposta do LLM via API)`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, agentResponse]);
    }, 1500);
  };

  // --- Roteamento e Renderização do Conteúdo Principal ---
  let MainContent;
  switch (selectedNav) {
    case 'Novo Upload':
      MainContent = <UploadPage handleUpload={handleUpload} setSelectedNav={setSelectedNav} />;
      break;
    case 'Dashboard':
      MainContent = <DashboardPage currentStep={currentStep} isProcessing={isProcessing} />;
      break;
    case 'Histórico':
      MainContent = (
        <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex items-center justify-center">
          <p className="text-xl text-gray-500">Histórico de Análises (em desenvolvimento)</p>
        </div>
      );
      break;
    case 'Configurações':
      MainContent = (
        <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex items-center justify-center">
          <p className="text-xl text-gray-500">
            Configurações de APIs e Agentes (em desenvolvimento)
          </p>
        </div>
      );
      break;
    default:
      MainContent = <DashboardPage currentStep={currentStep} isProcessing={isProcessing} />;
  }

  return (
    <div className="min-h-screen flex bg-gray-100 font-sans">
      <Sidebar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 lg:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Coluna 1: Workflow/Upload */}
            <div className="lg:col-span-1 h-[40vh] lg:h-full min-h-[300px]">{MainContent}</div>

            {/* Coluna 2 e 3: Chat/Análise */}
            <div className="lg:col-span-2 h-[55vh] lg:h-full min-h-[500px] lg:min-h-[600px]">
              <ChatPanel
                messages={messages}
                input={input}
                setInput={setInput}
                handleSendMessage={handleSendMessage}
                isProcessing={isProcessing}
                workflowSteps={workflowSteps}
                currentStep={currentStep}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
