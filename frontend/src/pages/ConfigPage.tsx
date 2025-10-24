import axios from 'axios';

import { useEffect, useRef } from 'react';
import { useServerContext } from '../context/serverContext/useServerContext';

interface ModelsSchema {
  groq: string[];
  google: string[];
}

function ConfigPage() {
  const MODELS = useRef<ModelsSchema | undefined>(undefined);
  const { isOnline, API_URL } = useServerContext();

  useEffect(() => {
    if (!isOnline || !API_URL) return;

    const getAvailableModels = async () => {
      const url = API_URL + '/models';
      const response = await axios.get(url);

      MODELS.current = response?.data;
    };

    getAvailableModels();
  }, [isOnline, API_URL]);

  return (
    <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex items-center justify-center">
      <h2 className="text-xl text-gray-500">Configurações de APIs e Agentes</h2>
      <div>
        <h3>Chaves de API</h3>
        <label>
          <input className="" type="text" />
        </label>
        )
      </div>
      <div>
        <h3>Configuração dos Agentes</h3>
      </div>
    </div>
  );
}

export default ConfigPage;
