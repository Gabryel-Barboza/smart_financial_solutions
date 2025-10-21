import type { Ref } from 'react';
import type { Message } from '../../schemas/InputSchema';

interface Props {
  messages: Message[];
  chatEndRef: Ref<HTMLDivElement>;
}

function ChatMessages({ messages, chatEndRef }: Props) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-xs sm:max-w-md lg:max-w-lg px-4 py-2 rounded-xl shadow-md ${
              msg.sender === 'User'
                ? 'bg-blue-600 text-white rounded-br-none'
                : msg.sender === 'Agent'
                ? 'bg-gray-200 text-gray-800 rounded-tl-none'
                : 'bg-amber-100 text-amber-900 text-sm rounded-lg'
            }`}
          >
            <p className="text-sm">{msg.text}</p>
            <span
              className={`block text-xs mt-1 ${
                msg.sender === 'User'
                  ? 'text-blue-200'
                  : msg.sender === 'Agent'
                  ? 'text-gray-500'
                  : 'text-amber-700'
              } text-right`}
            >
              {msg.time}
            </span>
          </div>
        </div>
      ))}
      <div ref={chatEndRef} />
    </div>
  );
}

export default ChatMessages;
