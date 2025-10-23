import { useEffect, useState } from 'react';

import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/NavBar';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import HistoryPage from './pages/HistoryPage';
import ConfigPage from './pages/ConfigPage';
import ChatPage from './pages/ChatPage';

import { useServerContext } from './context/serverContext/useServerContext';
import useWebSocket from './hooks/useWebSocket';

/**
 * Componente wrapper para utilizar o contexto da aplicação e orquestrar layout
 */
function AppPage() {
  // --- Estado do Aplicativo ---
  const [selectedNav, setSelectedNav] = useState('Dashboard');
  const { API_URL, sessionId, isOnline, isProcessing, setCurrentStep, setSteps } =
    useServerContext();
  const { websocket } = useWebSocket(API_URL, sessionId);

  // Reset de workflow
  useEffect(() => {
    if (isProcessing) {
      setSteps([]);
      setCurrentStep(undefined);
    }
  }, [isProcessing, setCurrentStep, setSteps]);

  // Conexão WebSocket para receber atualizações.
  useEffect(() => {
    if (!websocket || !isOnline) return;

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const newStep = { key: crypto.randomUUID(), ...data };

        setSteps((prev) => {
          const updatedSteps = [...prev, newStep];

          return updatedSteps;
        });

        setCurrentStep(newStep);
      } catch (err) {
        console.error('Failed to process WebSocket event update: ', err);
      }
    };

    return () => {
      websocket.onmessage = null;
    };
  }, [websocket, isOnline, setCurrentStep, setSteps]);

  // --- Roteamento e Renderização do Conteúdo Principal ---
  let MainContent;

  switch (selectedNav) {
    case 'Dashboard':
      MainContent = DashboardPage;
      break;
    case 'Novo Upload':
      MainContent = UploadPage;
      break;
    case 'Histórico':
      MainContent = HistoryPage;
      break;
    case 'Configurações':
      MainContent = ConfigPage;
      break;
    default:
      MainContent = DashboardPage;
  }

  // TODO: Adicionar tratamentos de erros para cenários inválidos.
  return (
    <div className="h-screen flex bg-gray-100 font-sans relative">
      <Sidebar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 lg:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:h-full">
            {/* Coluna 1: Workflow */}
            <div className="lg:col-span-1 lg:h-full min-h-[300px]">
              {<MainContent setSelectedNav={setSelectedNav} />}
            </div>

            {/* Coluna 2 e 3: Chat */}
            <div className="lg:col-span-2 lg:h-full min-h-[500px] lg:min-h-[600px]">
              <ChatPage />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default AppPage;
