import DOMPurify from 'dompurify';
import axios, { HttpStatusCode } from 'axios';
import { useState } from 'react';

import type { MessageSchema, ResponseSchema } from '../schemas/InputSchema';

import { initialMessages } from '../data/workflowData';
import { useServerContext } from '../context/serverContext/useServerContext';
import ChatPanel from '../components/Chat/ChatPanel';
import ChatPlot from '../components/Chat/ChatPlot';
import { useToastContext } from '../context/toastContext/useToastContext';

function ChatPage() {
  const { isOnline, API_URL, sessionId, isProcessing, setIsProcessing } = useServerContext();
  const { addToast } = useToastContext();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<MessageSchema[]>(initialMessages);

  // Handlers para envio de mensagem
  const sendMessage = async (url: string, data: unknown) => {
    try {
      const response = await axios.post(url, data);

      if (response.status !== HttpStatusCode.Created)
        throw new Error('Error in API response for chat message.');

      return response;
    } catch (err) {
      console.log(err);
      addToast('Ocorreu uma falha ao receber a resposta do servidor', 'error');
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing || !isOnline) return;

    const newMessage = {
      id: crypto.randomUUID(),
      sender: 'User',
      content: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    } as MessageSchema;

    setMessages((prev) => [...prev, newMessage]);

    setIsProcessing(true);

    // Enviar mensagem e renderizar resposta
    try {
      const url = API_URL + '/prompt';
      const data = { request: newMessage.content, session_id: sessionId };

      const response = await sendMessage(url, data);
      const payload = response?.data as ResponseSchema;

      payload.response = DOMPurify.sanitize(payload.response);

      // Se houve uma resposta do server, então adicionar mensagem ao histórico
      const agentMessages = [
        {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: payload.response,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ] as MessageSchema[];

      // Se na resposta existir um campo para renderizar gráfico.
      if (payload.graph_id) {
        const plot = <ChatPlot graphId={payload.graph_id} />;
        const plotMessage = {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: plot,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        } as MessageSchema;

        agentMessages.push(plotMessage);
      }

      setMessages((prev) => [...prev, ...agentMessages]);
    } catch (err) {
      console.error('Erro no envio da mensagem ao servidor: ', err);
      addToast(
        'Ocorreu uma falha na comunicação com o servidor, por favor tente novamente',
        'error'
      );
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
    />
  );
}

export default ChatPage;
