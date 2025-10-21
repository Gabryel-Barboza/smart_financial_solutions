import axios, { HttpStatusCode } from 'axios';
import { useState } from 'react';

import type { Message } from '../schemas/InputSchema';
import type { WorkflowCurrentStepSchema } from '../schemas/PropsSchema';

import { initialMessages } from '../data/workflowData';
import { useServerContext } from '../context/serverContext/useServerContext';
import ChatPanel from '../components/Chat/ChatPanel';

interface Props extends WorkflowCurrentStepSchema {
  sessionId: string;
}

function ChatPage({ isProcessing, currentStep, sessionId }: Props) {
  const API_URL = import.meta.env.VITE_FASTAPI_URL;

  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const { isOnline } = useServerContext();

  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing || !isOnline) return;

    const url = API_URL + '/prompt';

    const newMessage = {
      id: Date.now(),
      sender: 'User',
      text: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    } as Message;

    try {
      const data = { request: newMessage['text'], session_id: sessionId };
      const response = await axios.post(url, data);

      if (response.status !== HttpStatusCode.Accepted) return;

      // Se houve uma resposta do server, então adicionar mensagem ao histórico
      setMessages((prev) => [...prev, newMessage]);

      const agentMessage = {
        id: Date.now(),
        sender: 'Agent',
        text: response.data,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      } as Message;

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err) {
      console.log('Erro no envio da mensagem ao servidor: ', err);
    } finally {
      setInput('');
    }
  };

  return (
    <ChatPanel
      messages={messages}
      input={input}
      setInput={setInput}
      handleSendMessage={handleSendMessage}
      isProcessing={isProcessing}
      isOnline={isOnline}
      currentStep={currentStep}
    />
  );
}

export default ChatPage;
