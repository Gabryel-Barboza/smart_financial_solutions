interface Props {
  isOnline: boolean;
}

function ChatHeader({ isOnline }: Props) {
  return (
    <div className="p-4 bg-gray-100 border-b border-gray-200 flex items-center justify-between">
      <h2 className="text-xl font-bold text-gray-800">Converse com o Agente </h2>
      <span
        className={`text-sm flex items-center ${isOnline ? 'text-green-600' : 'text-gray-500'}`}
      >
        <span className="relative flex h-3 w-3 mr-2">
          <span
            className={`${
              isOnline ? 'animate-ping bg-green-400' : ''
            } absolute inline-flex h-full w-full rounded-full opacity-75`}
          ></span>
          <span
            className={`relative inline-flex rounded-full h-3 w-3 ${
              isOnline ? 'bg-green-500' : 'bg-gray-300'
            }`}
          ></span>
        </span>
        {isOnline ? 'Online' : 'Offline'}
      </span>
    </div>
  );
}

export default ChatHeader;
