import axios, { HttpStatusCode } from 'axios';
import { useState } from 'react';

import type { Message, Response } from '../schemas/InputSchema';

import { initialMessages } from '../data/workflowData';
import { useServerContext } from '../context/serverContext/useServerContext';
import ChatPanel from '../components/Chat/ChatPanel';
import ChatPlot from '../components/Chat/ChatPlot';

function ChatPage() {
  const { isOnline, API_URL, sessionId, isProcessing, setIsProcessing } = useServerContext();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const currentStep = 0;

  const sendMessage = async (url: string, data: unknown) => {
    try {
      const response = await axios.post(url, data);

      if (response.status !== HttpStatusCode.Accepted) return;

      return response;
    } catch (err) {
      console.log(err);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing || !isOnline) return;

    const newMessage = {
      id: crypto.randomUUID(),
      sender: 'User',
      content: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    } as Message;

    setMessages((prev) => [...prev, newMessage]);

    setIsProcessing(true);

    try {
      const url = API_URL + '/prompt';
      const data = { request: newMessage.content, session_id: sessionId };

      const response = await sendMessage(url, data);
      const payload = response?.data as Response;

      // Se houve uma resposta do server, então adicionar mensagem ao histórico
      const agentMessages = [
        {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: payload.response,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ] as Message[];

      // Se na resposta existir um campo para renderizar gráfico.
      if (payload.graph_id) {
        const plot = <ChatPlot graphId={payload.graph_id} />;
        const plotMessage = {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: plot,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        } as Message;

        agentMessages.push(plotMessage);
      }

      console.log(agentMessages);
      setMessages((prev) => [...prev, ...agentMessages]);
    } catch (err) {
      console.log('Erro no envio da mensagem ao servidor: ', err);
    } finally {
      setInput('');
      setIsProcessing(false);
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
