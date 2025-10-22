import clsx from 'clsx';
import type { Ref } from 'react';
import type { Message } from '../../schemas/InputSchema';

interface Props {
  isProcessing: boolean;
  messages: Message[];
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

        return (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={messageContentClass}>
              <p className="text-sm">{msg.content}</p>
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
