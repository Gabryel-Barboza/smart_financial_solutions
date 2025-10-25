import axios from 'axios';
import { useEffect, useState } from 'react';

import type { AvailableModels, DefaultModels } from '../../schemas/ConfigSchema';
import { useToastContext } from '../../context/toastContext/useToastContext';
import { useServerContext } from '../../context/serverContext/useServerContext';

// Interface para as informações do agente (simplificada)
interface Props {
  models: AvailableModels;
  tasks: string[];
  defaultModels: DefaultModels;
}

const ModelSelection = ({ models, tasks, defaultModels }: Props) => {
  const { addToast } = useToastContext();
  const { isOnline, API_URL, sessionId } = useServerContext();

  const [selectedTask, setSelectedTask] = useState<string>(tasks[0] || '');
  const [selectedModel, setSelectedModel] = useState<string>(models[0] || '');

  useEffect(() => {
    let defaultFound = false;

    for (const provider in defaultModels) {
      if (defaultModels[provider][selectedTask]) {
        // Encontrou o modelo padrão para a tarefa atual.
        setSelectedModel(defaultModels[provider][selectedTask]);
        defaultFound = true;
        break;
      }
    }

    const isModels = Object.keys(models).length > 0;

    // Se nenhum padrão for encontrado, define o primeiro modelo disponível como fallback
    if (!defaultFound && isModels) {
      setSelectedModel(Object.keys(models)[0]);
    }
  }, [selectedTask, defaultModels, models]);

  const handleSaveModel = async () => {
    try {
      const url = API_URL + '/change-model';
      const data = { agent_task: selectedTask, model_name: selectedModel, session_id: sessionId };

      const response = await axios.put(url, data);
      const content = response.data;

      if (content.detail) addToast(content.detail, 'success');
    } catch (err) {
      console.log(err);
      addToast(
        'Falha na alteração do modelo do agente. Verifique se você possui uma chave de API para o provedor do modelo',
        'error'
      );
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
        <label htmlFor="task-select" className="font-medium text-gray-700 w-1/3">
          Agente:
        </label>
        <select
          id="task-select"
          className="p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-2/3"
          value={selectedTask}
          onChange={(e) => setSelectedTask(e.target.value)}
        >
          {tasks.map((task) => (
            <option key={task} value={task}>
              {task.toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
        <label htmlFor="model-select" className="font-medium text-gray-700 w-1/3">
          Modelo:
        </label>
        <select
          id="model-select"
          className="p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-2/3"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          {Object.entries(models).map(([model, provider]) => (
            <option key={model} value={model}>
              {`${model} (${provider})`}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={handleSaveModel}
        className="mt-2 py-2 px-4 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition duration-150"
        disabled={!isOnline}
      >
        Salvar Configuração do Agente
      </button>
    </div>
  );
};

export default ModelSelection;
