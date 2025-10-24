import { useRef, useEffect } from 'react';

import type { ChatInputSchema } from '../../schemas/PropsSchema';
import type { MessageSchema } from '../../schemas/InputSchema';

import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import ChatHeader from './ChatHeader';
import { FaSpinner } from 'react-icons/fa6';

interface Props extends ChatInputSchema {
  messages: MessageSchema[];
  isOnline: boolean;
  isProcessing: boolean;
  handleSendMessage: () => void;
}

const ChatPanel = ({
  messages,
  input,
  setInput,
  isProcessing,
  isOnline,
  handleSendMessage,
}: Props) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scrolla para a última mensagem
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const isChatDisabled = isProcessing || !isOnline;

  return (
    <div
      className={`flex flex-col h-full bg-white shadow-xl rounded-2xl overflow-hidden ${
        isChatDisabled ? 'opacity-50 pointer-events-none' : ''
      }`}
    >
      <ChatHeader isOnline={isOnline} />

      <ChatMessages messages={messages} chatEndRef={chatEndRef} isProcessing={isProcessing} />
      {isChatDisabled && (
        <div className="text-4xl text-blue-600 ml-8 mb-4 w-fit animate-spin">
          <FaSpinner />
        </div>
      )}

      <ChatInput
        input={input}
        setInput={setInput}
        isProcessing={isProcessing}
        isChatDisabled={isChatDisabled}
        handleSendMessage={handleSendMessage}
      />
    </div>
  );
};

export default ChatPanel;
