import axios from 'axios';

import { useEffect, useMemo, useState } from 'react';

import { useServerContext } from '../context/serverContext/useServerContext';
import { useToastContext } from '../context/toastContext/useToastContext';

import type { AgentInfo, AvailableModels, DefaultModels } from '../schemas/ConfigSchema';

import ModelSelection from '../components/Config/ModelSelection';
import KeyInput from '../components/Config/KeyInput';

function ConfigPage() {
  const { isOnline, API_URL } = useServerContext();
  const { addToast } = useToastContext();

  const [agentInfo, setAgentInfo] = useState<AgentInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const isModelSelection = useMemo(() => {
    if (agentInfo) {
      const isAgentModels = Object.keys(agentInfo.availableModels).length > 0;
      const isTasks = agentInfo.tasks.length > 0;

      return isAgentModels && isTasks;
    }

    return false;
  }, [agentInfo]);

  useEffect(() => {
    if (!isOnline || !API_URL || agentInfo) {
      setLoading(false);
      return;
    }

    const getAgentInfo = async () => {
      try {
        const [modelsResponse, tasksResponse, defaultModelsResponse] = await Promise.all([
          axios.get<AvailableModels>(API_URL + '/agent-info'),
          axios.get<string[]>(API_URL + '/agent-info?tasks=true'),
          axios.get<DefaultModels>(API_URL + '/agent-info?defaults=true'),
        ]);

        setAgentInfo({
          availableModels: modelsResponse.data,
          tasks: tasksResponse.data,
          defaultModels: defaultModelsResponse.data,
        });
      } catch (error) {
        console.error('Erro ao buscar informações do agente:', error);
        addToast('Falha ao carregar as configurações disponíveis.', 'error');
      } finally {
        setLoading(false);
      }
    };

    setLoading(true);
    getAgentInfo();
  }, [isOnline, API_URL, agentInfo, addToast]);

  return (
    <div className="min-h-screen w-full text-black bg-gray-100 flex justify-center">
      <div className="w-full max-w-2xl bg-white shadow-2xl rounded-xl p-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-8 border-b pb-2">
          Configurações do Sistema
        </h1>

        <section className="mb-8 p-6 border border-blue-200 rounded-lg bg-blue-50 shadow-md">
          <h2 className="text-xl font-bold text-blue-800 mb-4 flex items-center gap-2">
            🔑 Chaves de API
          </h2>
          <KeyInput />
        </section>

        <section className="p-6 border border-indigo-200 rounded-lg bg-indigo-50 shadow-md">
          <h2 className="text-xl font-bold text-indigo-800 mb-4 flex items-center gap-2">
            🧠 Configuração de Modelos por Agente
          </h2>
          {loading && <p className="text-gray-600">Carregando modelos e tarefas disponíveis...</p>}{' '}
          {!isOnline && (
            <p className="text-red-500 font-medium">
              API Offline. Não é possível carregar ou alterar configurações dos agentes.
            </p>
          )}{' '}
          {agentInfo && isModelSelection ? (
            <ModelSelection
              models={agentInfo.availableModels}
              tasks={agentInfo.tasks}
              defaultModels={agentInfo.defaultModels}
            />
          ) : (
            <p className="text-orange-500">
              Configurações de agentes não recebidas, recarregue a página.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}

export default ConfigPage;
