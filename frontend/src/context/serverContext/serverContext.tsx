import { createContext, type Dispatch, type SetStateAction } from 'react';
import type { WorkflowStepSchema } from '../../schemas/InputSchema';

interface ServerContextType {
  isOnline: boolean;
  isProcessing: boolean;
  selectedNav: string;
  setSelectedNav: Dispatch<SetStateAction<string>>;
  setIsProcessing: Dispatch<SetStateAction<boolean>>;
  sessionId: string;
  API_URL: string;
  steps: WorkflowStepSchema[];
  setSteps: Dispatch<SetStateAction<WorkflowStepSchema[]>>;
  currentStep: WorkflowStepSchema | undefined;
  setCurrentStep: Dispatch<SetStateAction<WorkflowStepSchema | undefined>>;
}

export const ServerContext = createContext<ServerContextType | undefined>(undefined);
