import clsx from 'clsx';

import { useState, type JSX, type Ref } from 'react';

import styles from './ChatMessage.module.css';

import type { MessageSchema } from '../../../schemas/InputSchema';
import ChatModal from '../ChatModal/ChatModal';

interface Props {
  isProcessing: boolean;
  messages: MessageSchema[];
  chatEndRef: Ref<HTMLDivElement>;
}

interface ModalSchema {
  isOpen: boolean;
  content: string | JSX.Element | null;
}

function ChatMessages({ messages, chatEndRef }: Props) {
  const TABLE_REGEX = /<table[^>]*>[\s\S]*?<\/table>/gi;
  const [modalState, setModalState] = useState<ModalSchema>({ isOpen: false, content: null });

  const openModal = (content: ModalSchema['content']) => {
    setModalState({ isOpen: true, content: content });
  };

  const closeModal = () => {
    setModalState({ isOpen: false, content: null });
  };

  // Função para processar a string e substituir tabelas ou gráficos por botões
  const processMessageContent = (content: string): JSX.Element[] => {
    if (!content.includes('<table')) {
      // Se não houver tabelas, retorna o div original com o HTML completo
      return [<div key="full-html" dangerouslySetInnerHTML={{ __html: content }}></div>];
    }

    const parts: JSX.Element[] = [];
    let lastIndex = 0;

    // Acessa todas as correspondências da Regex
    let match;
    while ((match = TABLE_REGEX.exec(content)) !== null) {
      const tableHtml = match[0];
      const tableIndex = match.index;

      // Adiciona o texto que veio ANTES da tabela (se houver)
      if (tableIndex > lastIndex) {
        const textBefore = content.substring(lastIndex, tableIndex);
        // Usa dangerouslySetInnerHTML para o conteúdo que não é tabela
        parts.push(
          <div key={`text-${lastIndex}`} dangerouslySetInnerHTML={{ __html: textBefore }}></div>
        );
      }

      // Adiciona o BOTÃO no lugar da tabela
      parts.push(
        <button
          key={`table-btn-${tableIndex}`}
          onClick={() => openModal(tableHtml)}
          className="my-2 p-2 w-5/10 mx-[25%] bg-amber-500 text-white rounded shadow-md hover:bg-amber-600 transition duration-150 cursor-pointer"
        >
          Tabela de Dados (Expandir)
        </button>
      );

      // Atualiza o índice para o final da tabela
      lastIndex = TABLE_REGEX.lastIndex;
    }

    // Adiciona o texto que veio DEPOIS da última tabela (se houver)
    if (lastIndex < content.length) {
      const textAfter = content.substring(lastIndex);
      parts.push(
        <div key={`text-${lastIndex}-end`} dangerouslySetInnerHTML={{ __html: textAfter }}></div>
      );
    }

    return parts;
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      {messages.map((msg) => {
        const isUser = msg.sender === 'User';
        const isAgent = msg.sender === 'Agent';

        const messageContentClass = clsx(
          'max-w-xs sm:max-w-md lg:max-w-lg px-4 py-2 rounded-xl shadow-md text-sm',
          {
            'bg-blue-600 text-white rounded-br-none': isUser,
            'bg-gray-200 text-gray-800 rounded-tl-none': isAgent,
            'bg-amber-100 text-amber-900 text-sm rounded-lg': !isUser && !isAgent,
          }
        );
        const messageTimeClass = clsx('block text-xs mt-1 text-right', {
          'text-blue-200': isUser,
          'text-gray-500': isAgent,
          'text-amber-700': !isUser && !isAgent,
        });

        let element;

        // Lógica de inserção de conteúdo, se ImageContent -> string -> JSX
        if (
          typeof msg.content === 'object' &&
          'type' in msg.content &&
          'fileUrl' in msg.content &&
          'altText' in msg.content
        ) {
          element = <img src={msg.content.fileUrl} alt={msg.content.altText} />;
        } else if (typeof msg.content === 'string') {
          element = processMessageContent(msg.content);
        } else {
          element = (
            <button
              onClick={() => openModal(msg.content as JSX.Element)}
              className="my-2 p-2 w-full bg-amber-500 text-white rounded shadow-md hover:bg-amber-600 transition duration-150"
            >
              Visualização do Gráfico (Expandir)
            </button>
          );
        }

        return (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`${styles.messages} ${messageContentClass}`}>
              {element}
              <span className={messageTimeClass}>{msg.time}</span>
            </div>
          </div>
        );
      })}

      <ChatModal isOpen={modalState.isOpen} onClose={closeModal} title="Visualização Externa">
        {modalState.content && typeof modalState.content === 'string' ? (
          <div
            className="bg-gray-200 p-4 rounded-sm overflow-x-scroll shadow-black/30 shadow-md"
            dangerouslySetInnerHTML={{ __html: modalState.content }}
          />
        ) : (
          <div className="bg-gray-200 p-4 rounded-sm overflow-x-scroll shadow-black/30 shadow-md">
            {modalState.content}
          </div>
        )}
      </ChatModal>
      <div ref={chatEndRef} />
    </div>
  );
}

export default ChatMessages;
