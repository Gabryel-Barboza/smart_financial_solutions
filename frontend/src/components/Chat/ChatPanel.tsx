import type { Dispatch, SetStateAction } from 'react';

import { useRef, useEffect } from 'react';
import { FaSpinner } from 'react-icons/fa6';

import type { ChatInputSchema } from '../../schemas/PropsSchema';
import type { MessageSchema, ResponseSchema } from '../../schemas/InputSchema';

import { useServerContext } from '../../context/serverContext/useServerContext';
import useFileUpload from '../../hooks/useFileUpload';
import ChatMessages from './ChatMessages/ChatMessages';
import ChatInput from './ChatInput';
import ChatHeader from './ChatHeader';

interface Props extends ChatInputSchema {
  messages: MessageSchema[];
  setMessages: Dispatch<SetStateAction<MessageSchema[]>>;
  createAgentMessages: (
    rawContent: ResponseSchema['response'],
    graphId: ResponseSchema['graph_id']
  ) => void;
  handleSendMessage: () => void;
}

const ChatPanel = ({
  messages,
  setMessages,
  createAgentMessages,
  input,
  setInput,
  handleSendMessage,
}: Props) => {
  const { isProcessing, isOnline, sessionId, API_URL } = useServerContext();
  const { uploadFile } = useFileUpload(isOnline, sessionId);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scrolla para a última mensagem
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const isChatDisabled = isProcessing || !isOnline;

  /**
   * Função para realizar upload da imagem para o backend e renderizar as mensagens
   */
  const uploadImage = async (file: File, newMessage: MessageSchema) => {
    setMessages((prev) => [...prev, newMessage]);

    const url = API_URL + '/upload/image';
    const response = await uploadFile(file, url);
    const { response: content, graph_id: graphId } = response.data as ResponseSchema;

    createAgentMessages(content, graphId);
  };

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
        isChatDisabled={isChatDisabled}
        handleSendMessage={handleSendMessage}
        uploadImage={uploadImage}
      />
    </div>
  );
};

export default ChatPanel;
