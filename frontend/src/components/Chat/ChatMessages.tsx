import clsx from 'clsx';
import type { JSX, Ref } from 'react';
import type { MessageSchema } from '../../schemas/InputSchema';

interface Props {
  isProcessing: boolean;
  messages: MessageSchema[];
  chatEndRef: Ref<HTMLDivElement>;
}

function ChatMessages({ messages, chatEndRef }: Props) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      {messages.map((msg) => {
        const isUser = msg.sender === 'User';
        const isAgent = msg.sender === 'Agent';

        const messageContentClass = clsx(
          'max-w-xs sm:max-w-md lg:max-w-lg px-4 py-2 rounded-xl shadow-md',
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
          element = <p className="text-sm" dangerouslySetInnerHTML={{ __html: msg.content }}></p>;
        } else {
          element = <p className="text-sm">{msg.content as JSX.Element}</p>;
        }

        return (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={messageContentClass}>
              {element}
              <span className={messageTimeClass}>{msg.time}</span>
            </div>
          </div>
        );
      })}

      <div ref={chatEndRef} />
    </div>
  );
}

export default ChatMessages;
