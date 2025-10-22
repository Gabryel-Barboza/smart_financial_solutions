import { createContext, type Dispatch, type SetStateAction } from 'react';

interface ServerContextType {
  isOnline: boolean;
  isProcessing: boolean;
  setIsProcessing: Dispatch<SetStateAction<boolean>>;
  sessionId: string;
  API_URL: string;
}

export const ServerContext = createContext<ServerContextType | undefined>(undefined);
