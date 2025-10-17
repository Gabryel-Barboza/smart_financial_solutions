import { useRef, useEffect } from 'react';

const ChatPanel = ({
  messages,
  input,
  setInput,
  handleSendMessage,
  isProcessing,
  workflowSteps,
  currentStep,
}) => {
  const chatEndRef = useRef(null);

  // Scrolla para a última mensagem
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isChatDisabled = currentStep < workflowSteps.length && isProcessing;

  return (
    <div
      className={`flex flex-col h-full bg-white shadow-xl rounded-2xl overflow-hidden ${
        isChatDisabled ? 'opacity-50 pointer-events-none' : ''
      }`}
    >
      {/* Chat Header */}
      <div className="p-4 bg-gray-100 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Agente Analista (LLM)</h2>
        <span className="text-sm text-green-600 flex items-center">
          <span className="relative flex h-3 w-3 mr-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          Online
        </span>
      </div>

      {/* Chat Messages Area */}
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

      {/* Chat Input Area */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={
              isProcessing
                ? 'Aguarde a conclusão do processamento...'
                : 'Pergunte ao Agente Analista...'
            }
            className="flex-1 p-3 border border-gray-300 rounded-l-xl focus:ring-blue-500 focus:border-blue-500 transition duration-150 disabled:bg-gray-100"
            disabled={isChatDisabled}
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isChatDisabled}
            className="p-3 bg-blue-600 text-white rounded-r-xl hover:bg-blue-700 transition duration-200 disabled:bg-blue-300 shadow-lg"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;
