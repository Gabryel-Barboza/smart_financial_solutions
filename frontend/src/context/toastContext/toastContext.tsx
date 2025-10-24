import type { ToastDataSchema } from '../../schemas/InputSchema';
import { createContext } from 'react';

interface ToastContextType {
  toasts: ToastDataSchema[];
  addToast: (message: string, type: ToastDataSchema['type'], duration?: number) => void;
  removeToast: (id: ToastDataSchema['id']) => void;
}

export const ToastContext = createContext<ToastContextType | undefined>(undefined);
