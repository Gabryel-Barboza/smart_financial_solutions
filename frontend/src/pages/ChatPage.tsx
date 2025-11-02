import DOMPurify from 'dompurify';
import axios from 'axios';
import { useState } from 'react';

import type { MessageSchema, ResponseSchema, MessageStyle } from '../schemas/InputSchema';

import { useServerContext } from '../context/serverContext/useServerContext';
import { initialMessages } from '../data/workflowData';

import useFileUpload from '../hooks/useFileUpload';

import ChatPanel from '../components/Chat/ChatPanel';
import ChatPlot from '../components/Chat/ChatPlot';
import ChatInput from '../components/Chat/ChatInput';

const ChatPage = () => {
  const { isOnline, API_URL, sessionId, isProcessing, setIsProcessing, setSelectedNav } =
    useServerContext();
  const { uploadFile } = useFileUpload(isOnline, sessionId);

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<MessageSchema[]>(initialMessages);

  const isChatDisabled = isProcessing || !isOnline;

  // Handlers para criação da mensagem do agente
  const createAgentMessages = (
    rawContent: ResponseSchema['response'],
    graphId: ResponseSchema['graph_id'],
    msgStyle: MessageStyle
  ) => {
    const content = DOMPurify.sanitize(rawContent);

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    // Se houve uma resposta do server, então adicionar mensagem ao histórico
    const agentMessages: MessageSchema[] = [
      {
        id: crypto.randomUUID(),
        sender: 'Agent',
        content: content,
        time: time,
        style: msgStyle,
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
          style: msgStyle,
        }));

        agentMessages.push(...plotMessages);
      } else {
        const plotMessage: MessageSchema = {
          id: crypto.randomUUID(),
          sender: 'Agent',
          content: <ChatPlot graphId={graphId} />,
          time: time,
          style: msgStyle,
        };

        agentMessages.push(plotMessage);
      }
    }

    setMessages((prev) => [...prev, ...agentMessages]);
  };

  // Enviar mensagem ao servidor
  const sendMessage = async (url: string, data: unknown) => {
    const response = await axios.post(url, data);

    const payload = response?.data as ResponseSchema;
    const { response: rawContent, graph_id: graphId } = payload;

    return { rawContent, graphId };
  };

  // Handler de envio de mensagem
  const handleSendMessage = async () => {
    if (!input.trim() || isProcessing || !isOnline) return;

    const newMessage: MessageSchema = {
      id: crypto.randomUUID(),
      sender: 'User',
      content: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      style: 'success',
    };

    setMessages((prev) => [...prev, newMessage]);

    setIsProcessing(true);
    setSelectedNav('Dashboard');

    // Enviar mensagem e renderizar resposta
    try {
      const url = API_URL + '/prompt';
      const data = { request: newMessage.content, session_id: sessionId };

      const { rawContent, graphId } = await sendMessage(url, data);

      createAgentMessages(rawContent, graphId, 'success');
    } catch (err) {
      console.log(err);

      let errMsg;

      // Adicionar toast e mensagem de erro
      if (axios.isAxiosError(err) && err.response) {
        if (typeof err.response.data == 'string') errMsg = err.response.data;
        else
          errMsg =
            'O servidor falhou para retornar uma resposta do agente, tenha certeza de que sua chave de API é válida ou envie uma novamente.';
      } else {
        errMsg =
          'O servidor falhou para retornar uma resposta do agente, tenha certeza de que sua chave de API é válida ou envie uma novamente.';
      }

      createAgentMessages(errMsg, '', 'error');
    } finally {
      setInput('');
      setIsProcessing(false);
    }
  };

  /**
   * Função para realizar upload da imagem para o backend e renderizar as mensagens
   */
  const uploadImage = async (file: File, newMessage: MessageSchema) => {
    setMessages((prev) => [...prev, newMessage]);

    const url = API_URL + '/upload/image';
    const response = await uploadFile(file, url);
    const { response: content, graph_id: graphId } = response.data as ResponseSchema;

    createAgentMessages(content, graphId, 'success');
  };

  return (
    <ChatPanel
      isChatDisabled={isChatDisabled}
      messages={messages}
      setMessages={setMessages}
      createAgentMessages={createAgentMessages}
      input={input}
      setInput={setInput}
      handleSendMessage={handleSendMessage}
      // ChatInput Composition
      chatInput={
        <ChatInput
          input={input}
          setInput={setInput}
          isChatDisabled={isChatDisabled}
          handleSendMessage={handleSendMessage}
          createAgentMessages={createAgentMessages}
          uploadImage={uploadImage}
        />
      }
    />
  );
};

export default ChatPage;
