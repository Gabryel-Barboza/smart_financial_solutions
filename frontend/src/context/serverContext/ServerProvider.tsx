import type { ReactNode } from 'react';
import { ServerContext } from './serverContext';

import useApiConnect from '../../hooks/useApiConnect';

/**
 * Componente Provedor (Provider). Ele encapsula a lógica de estado e
 * fornece o valor do contexto para todos os seus filhos.
 */
export const ServerProvider = ({ children }: { children: ReactNode }) => {
  const { isOnline } = useApiConnect(60000); // Lógica de estado centralizada aqui

  const value = { isOnline };

  return <ServerContext.Provider value={value}>{children}</ServerContext.Provider>;
};
