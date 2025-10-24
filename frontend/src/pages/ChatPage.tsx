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
    const response = await axios.post(url, data);

    if (response.status !== HttpStatusCode.Created)
      throw new Error('Error in API response for chat message.');

    const payload = response?.data as ResponseSchema;
    const { response: rawContent, graph_id: graphId } = payload;

    return { rawContent, graphId };
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing || !isOnline) return;

    const newMessage: MessageSchema = {
      id: crypto.randomUUID(),
      sender: 'User',
      content: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, newMessage]);

    setIsProcessing(true);

    // Enviar mensagem e renderizar resposta
    try {
      const url = API_URL + '/prompt';
      const data = { request: newMessage.content, session_id: sessionId };

      const { rawContent, graphId } = await sendMessage(url, data);

      const content = DOMPurify.sanitize(rawContent);

      const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      // Se houve uma resposta do server, então adicionar mensagem ao histórico
      const agentMessages: MessageSchema[] = [
        {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: content,
          time: time,
        },
      ];

      // Se na resposta existir um campo para renderizar gráfico.
      if (graphId) {
        // Renderizar vetor de gráficos
        if (Array.isArray(graphId)) {
          const plotMessages: MessageSchema[] = graphId.map((id) => ({
            id: crypto.randomUUID(),
            sender: 'Agent',
            content: <ChatPlot graphId={id} />,
            time: time,
          }));

          agentMessages.push(...plotMessages);
        } else {
          const plotMessage: MessageSchema = {
            id: crypto.randomUUID(),
            sender: 'Agent',
            content: <ChatPlot graphId={graphId} />,
            time: time,
          };

          agentMessages.push(plotMessage);
        }
      }

      setMessages((prev) => [...prev, ...agentMessages]);
    } catch (err) {
      console.log(err);
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
