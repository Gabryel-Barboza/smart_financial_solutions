import type { ReactNode } from 'react';
import { useState, useMemo } from 'react';

import { ServerContext } from './serverContext';

import useApiConnect from '../../hooks/useApiConnect';
import type { WorkflowStepSchema } from '../../schemas/InputSchema';

/**
 * Função geradora para identificador de sessão.
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
  const [selectedNav, setSelectedNav] = useState('Dashboard');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<WorkflowStepSchema>();
  const [steps, setSteps] = useState<WorkflowStepSchema[]>([]);
  const [sessionId] = useState(getNewSessionId);
  const { isOnline, API_URL } = useApiConnect(60000);

  const value = useMemo(
    () => ({
      isOnline,
      selectedNav,
      setSelectedNav,
      isProcessing,
      setIsProcessing,
      sessionId,
      API_URL,
      steps,
      setSteps,
      currentStep,
      setCurrentStep,
    }),
    [sessionId, isOnline, selectedNav, isProcessing, API_URL, steps, currentStep]
  );

  return <ServerContext.Provider value={value}>{children}</ServerContext.Provider>;
};
