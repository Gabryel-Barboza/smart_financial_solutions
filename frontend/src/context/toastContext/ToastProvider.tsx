import type { ReactNode } from 'react';
import { useCallback, useState } from 'react';

import { ToastContext } from './toastContext';
import type { ToastDataSchema } from '../../schemas/InputSchema';

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<ToastDataSchema[]>([]);

  const removeToast = useCallback((id: ToastDataSchema['id']) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (message: string, type: ToastDataSchema['type'], duration: number = 6000) => {
      const id = crypto.randomUUID();
      const newToast = { id, message, type } as ToastDataSchema;

      setToasts((prev) => [...prev, newToast]);

      if (duration > 0) {
        setTimeout(() => removeToast(id), duration);
      }
    },
    [removeToast]
  );

  const value = { addToast, removeToast, toasts };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
};
