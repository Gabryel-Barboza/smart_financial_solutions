import { useContext } from 'react';
import { ToastContext } from './toastContext';

export const useToastContext = () => {
  const context = useContext(ToastContext);

  if (context === undefined) {
    throw new Error('useToastContext should be used within a ToastProvider');
  }

  return context;
};
