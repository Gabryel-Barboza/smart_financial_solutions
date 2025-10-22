import { useState } from 'react';

import './App.css';

import { ServerProvider } from './context/serverContext/ServerProvider';

import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/NavBar';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import HistoryPage from './pages/HistoryPage';
import ConfigPage from './pages/ConfigPage';
import ChatPage from './pages/ChatPage';

/**
 * Componente principal da aplicação.
 * Orquestra o estado e o layout.
 */
const App = () => {
  // --- Estado do Aplicativo ---
  const [selectedNav, setSelectedNav] = useState('Dashboard');

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
    <ServerProvider>
      <div className="h-screen flex bg-gray-100 font-sans relative">
        <Sidebar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />

        <div className="flex-1 flex flex-col overflow-hidden">
          <Navbar selectedNav={selectedNav} setSelectedNav={setSelectedNav} />
          <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 lg:p-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
              {/* Coluna 1: Workflow */}
              <div className="lg:col-span-1 h-[40vh] lg:h-full min-h-[300px]">
                {<MainContent setSelectedNav={setSelectedNav} />}
              </div>

              {/* Coluna 2 e 3: Chat */}
              <div className="lg:col-span-2 h-[55vh] lg:h-full min-h-[500px] lg:min-h-[600px]">
                <ChatPage />
              </div>
            </div>
          </main>
        </div>
      </div>
    </ServerProvider>
  );
};

export default App;
