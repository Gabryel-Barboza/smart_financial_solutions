import './App.css';

import { ServerProvider } from './context/serverContext/ServerProvider';
import { ToastProvider } from './context/toastContext/ToastProvider';

import ToastContainer from './components/Toast/ToastContainer';
import AppPage from './AppContent';

/**
 * Componente principal da aplicação.
 */
const App = () => (
  <ToastProvider>
    <ServerProvider>
      <AppPage />
      <ToastContainer />
    </ServerProvider>
  </ToastProvider>
);

export default App;
