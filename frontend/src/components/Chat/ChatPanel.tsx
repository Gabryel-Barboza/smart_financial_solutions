import type { Dispatch, ReactNode, SetStateAction } from 'react';

import { useRef, useEffect } from 'react';
import { FaSpinner } from 'react-icons/fa6';

import type { ChatInputSchema } from '../../schemas/PropsSchema';
import type { MessageSchema, MessageStyle, ResponseSchema } from '../../schemas/InputSchema';

import { useServerContext } from '../../context/serverContext/useServerContext';
import ChatMessages from './ChatMessages/ChatMessages';
import ChatHeader from './ChatHeader';

interface Props extends ChatInputSchema {
  isChatDisabled: boolean;
  messages: MessageSchema[];
  setMessages: Dispatch<SetStateAction<MessageSchema[]>>;
  createAgentMessages: (
    rawContent: ResponseSchema['response'],
    graphId: ResponseSchema['graph_id'],
    msgStyle: MessageStyle
  ) => void;
  handleSendMessage: () => void;
  chatInput: ReactNode;
}

const ChatPanel = ({ isChatDisabled, messages, chatInput }: Props) => {
  const { isProcessing, isOnline } = useServerContext();

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scrolla para a última mensagem
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

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

      {chatInput}
    </div>
  );
};

export default ChatPanel;
