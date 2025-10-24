import './App.css';

import { ServerProvider } from './context/serverContext/ServerProvider';
import { ToastProvider } from './context/toastContext/ToastProvider';

import ToastContainer from './components/Toast/ToastContainer';
import AppPage from './AppContent';

/**
 * Componente principal da aplicação.
 */
const App = () => (
  <ServerProvider>
    <ToastProvider>
      <div className="relative">
        <AppPage />
        <ToastContainer />
      </div>
    </ToastProvider>
  </ServerProvider>
);

export default App;
