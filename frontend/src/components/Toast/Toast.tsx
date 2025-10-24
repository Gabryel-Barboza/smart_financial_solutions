import clsx from 'clsx';

import type { ToastDataSchema } from '../../schemas/InputSchema';

import { useToastContext } from '../../context/toastContext/useToastContext';

function Toast({ id, type, message }: ToastDataSchema) {
  const { removeToast } = useToastContext();

  const toastDivClass = clsx(
    'p-4 mb-2 rounded border-l-4 shadow-lg text-white transition-opacity duration-300 ease-in-out',
    {
      'bg-green-500': type === 'success',
      'bg-blue-400': type === 'info',
      'bg-amber-300': type === 'warning',
      'bg-red-500': type === 'error',
    }
  );

  return (
    <div className={toastDivClass}>
      <div className="flex justify-between item-center">
        <span>{message}</span>
        <button
          className="ml-4 font-bold text-xl leading-none opacity-75 hover:opacity-100"
          type="button"
          onClick={() => removeToast(id)}
        >
          &times;
        </button>
      </div>
    </div>
  );
}

export default Toast;
