import type { WorkflowCurrentStepSchema } from '../../schemas/PropsSchema';

const WorkflowPanel = ({ isProcessing }: WorkflowCurrentStepSchema) => {
  return (
    <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex flex-col">
      <h2 className="text-2xl font-extrabold text-gray-800 mb-6">Status do Processamento</h2>

      <div className="mt-auto pt-6 border-t border-gray-100">
        <p className="text-sm text-gray-700">
          Status Atual:{' '}
          <span className={`font-semibold ${isProcessing ? 'text-amber-500' : 'text-gray-500'}`}>
            {isProcessing ? 'Processando...' : 'Aguardando Arquivo'}
          </span>
        </p>
      </div>
    </div>
  );
};

export default WorkflowPanel;
