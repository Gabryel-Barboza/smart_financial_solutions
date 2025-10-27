import styles from './ChatModal.module.css';

interface Props {
  isOpen: boolean;
  children: React.ReactNode;
  title: string;
  onClose: () => void;
}

const ChatModal = ({ isOpen, onClose, children, title }: Props) => {
  if (!isOpen) return null;

  return (
    // Backdrop
    <div
      className={`${styles.modal} fixed inset-0 z-50 flex items-center justify-center h-screen bg-black/40`}
      onClick={onClose}
    >
      {/* Container do Modal */}
      <div
        className="text-black bg-white p-6 rounded-lg shadow-xl max-w-4xl w-full overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-xl font-bold mb-4">{title}</h3>
        {children}
        <button
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          onClick={onClose}
        >
          Fechar
        </button>
      </div>
    </div>
  );
};

export default ChatModal;
