import { useRef, useEffect } from 'react';

import type { WorkflowCurrentStepSchema, ChatInputSchema } from '../../schemas/PropsSchema';
import type { Message } from '../../schemas/InputSchema';

import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import ChatHeader from './ChatHeader';

interface Props extends WorkflowCurrentStepSchema, ChatInputSchema {
  messages: Message[];
  isOnline: boolean;
  handleSendMessage: () => void;
}

const ChatPanel = ({ messages, input, setInput, handleSendMessage, isProcessing, isOnline }: Props) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scrolla para a última mensagem
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const isChatDisabled = isProcessing;

  return (
    <div
      className={`flex flex-col h-full bg-white shadow-xl rounded-2xl overflow-hidden ${
        isChatDisabled ? 'opacity-50 pointer-events-none' : ''
      }`}
    >
      <ChatHeader isOnline={isOnline} />

      <ChatMessages messages={messages} chatEndRef={chatEndRef} />

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
