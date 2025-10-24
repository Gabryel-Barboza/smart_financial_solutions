import { useToastContext } from '../../context/toastContext/useToastContext';
import Toast from './Toast';

function ToastContainer() {
  const { toasts } = useToastContext();

  return (
    <div className="fixed top-4 right-2 z-10 w-full h-fit max-w-xs">
      {toasts.map((toast) => (
        <Toast key={toast.id} id={toast.id} type={toast.type} message={toast.message} />
      ))}
    </div>
  );
}

export default ToastContainer;
