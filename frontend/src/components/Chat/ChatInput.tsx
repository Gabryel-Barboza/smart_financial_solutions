import type { ChatInputSchema } from '../../schemas/PropsSchema';

interface Props extends ChatInputSchema {
  isProcessing: boolean;
  isChatDisabled: boolean;
  handleSendMessage: () => void;
}

function ChatInput({ input, setInput, isProcessing, isChatDisabled, handleSendMessage }: Props) {
  return (
    <div className="p-4 bg-white border-t border-gray-200">
      <div className="flex items-center text-black">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyUp={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder={
            isProcessing
              ? 'Aguarde a conclusão do processamento...'
              : 'Pergunte ao Agente Analista...'
          }
          className="flex-1 p-3 border border-gray-300 rounded-l-xl focus:ring-blue-500 focus:border-blue-500 transition duration-150 disabled:bg-gray-100"
          disabled={isChatDisabled}
        />
        <button
          onClick={handleSendMessage}
          disabled={!input.trim() || isChatDisabled}
          className="p-3 bg-blue-600 text-white rounded-r-xl hover:bg-blue-700 transition duration-200 disabled:bg-blue-300 shadow-lg"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}

export default ChatInput;
