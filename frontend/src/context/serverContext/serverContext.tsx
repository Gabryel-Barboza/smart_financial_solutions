import { createContext } from 'react';

interface ServerContextType {
  isOnline: boolean;
}

export const ServerContext = createContext<ServerContextType | undefined>(undefined);