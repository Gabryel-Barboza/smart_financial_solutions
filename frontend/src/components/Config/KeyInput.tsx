import axios from 'axios';
import { useState } from 'react';
import { useToastContext } from '../../context/toastContext/useToastContext';
import { useServerContext } from '../../context/serverContext/useServerContext';

interface Props {
  providers: string[];
}

const KeyInput = ({ providers }: Props) => {
  const { addToast } = useToastContext();
  const { API_URL, isOnline, sessionId } = useServerContext();
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [apiProvider, setApiProvider] = useState('groq');

  const handleSaveApiKey = async () => {
    if (!apiKeyInput.trim()) {
      addToast('Chave API não pode ser vazia.', 'error');
      return;
    }

    try {
      const url = API_URL + '/send-key';
      const data = { api_key: apiKeyInput, provider: apiProvider, session_id: sessionId };

      const response = await axios.post(url, data);
      const content = response.data;

      if (content.detail) addToast(content.detail, 'success');
    } catch (err) {
      console.log(err);
      addToast('Falha no envio da chave para o servidor, tente novamente', 'error');
    } finally {
      setApiKeyInput('');
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {providers ? (
        <>
          <div className="flex flex-col">
            <label htmlFor="api-key" className="font-medium text-gray-700 mb-1">
              Sua chave de API:
            </label>
            <input
              id="api-key"
              className="p-3 border border-blue-400 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              type="password"
              placeholder="Insira sua chave secreta aqui..."
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-between">
            <label htmlFor="provider-select" className="font-medium text-gray-700">
              Provedor:
            </label>
            <select
              id="provider-select"
              className="p-2 border border-gray-300 rounded-lg w-40 focus:ring-blue-500 focus:border-blue-500"
              value={apiProvider}
              onChange={(e) => setApiProvider(e.target.value)}
            >
              {providers.map((provider, idx) => {
                const capitalizedProvider = provider.charAt(0).toUpperCase() + provider.slice(1);

                return (
                  <option key={idx} value={provider}>
                    {capitalizedProvider}
                  </option>
                );
              })}
            </select>
          </div>

          <button
            type="button"
            onClick={handleSaveApiKey}
            className="mt-4 py-3 px-6 bg-blue-600 text-white font-bold rounded-lg shadow-lg hover:bg-blue-700 transition duration-150"
            disabled={!isOnline}
          >
            Salvar Chave
          </button>
        </>
      ) : (
        <p className="text-red-500 font-medium">
          Não foi possível carregar os provedores disponíveis, por favor recarregue a aba!
        </p>
      )}
    </div>
  );
};

export default KeyInput;
