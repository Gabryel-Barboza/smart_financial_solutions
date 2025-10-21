import type { ReactNode } from 'react';
import { useState, useMemo } from 'react';

import { ServerContext } from './serverContext';

import useApiConnect from '../../hooks/useApiConnect';

/**
 * Função geradora para identificador da sessão.
 * Retorna um UUID v4 como string.
 */
const getNewSessionId = () => {
  const sessionId = crypto.randomUUID();
  console.log(`New session created with id ${sessionId}`);
  return sessionId;
};

/**
 * Componente Provedor (Provider). Ele encapsula a lógica de estado e
 * fornece o valor do contexto para todos os seus filhos.
 */
export const ServerProvider = ({ children }: { children: ReactNode }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(getNewSessionId);
  const { isOnline } = useApiConnect(60000);

  const value = useMemo(
    () => ({
      isOnline,
      isProcessing,
      setIsProcessing,
      sessionId,
    }),
    [sessionId, isOnline, isProcessing]
  );

  return <ServerContext.Provider value={value}>{children}</ServerContext.Provider>;
};
