import type { JSX } from 'react';
import { useState } from 'react';

import './App.css';

import type { CurrentNavSchema } from './schemas/PropsSchema';

import { ServerProvider } from './context/serverContext/ServerProvider';

import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/NavBar';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import HistoryPage from './pages/HistoryPage';
import ConfigPage from './pages/ConfigPage';
import ChatPage from './pages/ChatPage';
import { useServerContext } from './context/serverContext/useServerContext';

/**
 * Componente principal da aplicação.
 * Orquestra o estado e o layout.
 */
const App = () => {
  // --- Estado do Aplicativo ---
  const [selectedNav, setSelectedNav] = useState('Dashboard');
  const currentStep = 0;

  // --- Roteamento e Renderização do Conteúdo Principal ---
  let MainContent;

  switch (selectedNav) {
    case 'Dashboard':
      MainContent = <DashboardPage currentStep={currentStep} isProcessing={false} />;
      break;
    case 'Novo Upload':
      MainContent = <UploadPage setSelectedNav={setSelectedNav} />;
      break;
    case 'Histórico':
      MainContent = <HistoryPage />;
      break;
    case 'Configurações':
      MainContent = <ConfigPage />;
      break;
    default:
      MainContent = <DashboardPage currentStep={currentStep} isProcessing={false} />;
  }

  return (
    <ServerProvider>
      <AppContent
        selectedNav={selectedNav}
        setSelectedNav={setSelectedNav}
        MainContent={MainContent}
      />
    </ServerProvider>
  );
};

interface Props extends CurrentNavSchema {
  MainContent: JSX.Element;
}

const AppContent = ({ selectedNav, setSelectedNav, MainContent }: Props) => {
  const { isProcessing } = useServerContext();

  // TODO: Adicionar tratamentos de erros para cenários inválidos.
  return (
    <div className="min-h-screen flex bg-gray-100 font-sans">
      <Sidebar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 lg:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* Coluna 1: Workflow */}
            <div className="lg:col-span-1 h-[40vh] lg:h-full min-h-[300px]">{MainContent}</div>

            {/* Coluna 2 e 3: Chat */}
            <div className="lg:col-span-2 h-[55vh] lg:h-full min-h-[500px] lg:min-h-[600px]">
              <ChatPage isProcessing={isProcessing} currentStep={0} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
