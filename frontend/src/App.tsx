import './App.css';

import { ServerProvider } from './context/serverContext/ServerProvider';

import AppPage from './AppContent';

/**
 * Componente principal da aplicação.
 */
const App = () => (
  <ServerProvider>
    <AppPage />
  </ServerProvider>
);

export default App;
