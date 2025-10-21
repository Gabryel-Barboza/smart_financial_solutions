import { useContext } from 'react';

import { ServerContext } from './serverContext';

/**
 * Hook customizado para consumir o contexto.
 * Garante que o contexto não seja usado fora do seu Provedor.
 */
export const useServerContext = () => {
  const context = useContext(ServerContext);

  if (context === undefined) {
    throw new Error('useServerContext must be used within a ServerProvider');
  }
  return context;
};
