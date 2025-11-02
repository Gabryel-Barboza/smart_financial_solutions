import { useServerContext } from '../../context/serverContext/useServerContext';

import WorkflowStep from './WorkflowStep';

const WorkflowPanel = () => {
  const { steps, currentStep, isProcessing } = useServerContext();
  const stepsLastIndex = steps.length - 1;

  return (
    <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex flex-col overflow-y-scroll">
      <h2 className="text-2xl font-extrabold text-gray-800 mb-6">Status do Processamento</h2>
      {currentStep && isProcessing && (
        <h3 className="bg-blue-600 text-white font-bold w-fit p-1 mb-4">
          Agente Atual: {currentStep.name}
        </h3>
      )}
      {
        <>
          {steps.map((step, index) => {
            const isLast = index === stepsLastIndex;

            return (
              <WorkflowStep key={step.key} step={step} currentStep={currentStep} isLast={isLast} />
            );
          })}
        </>
      }
      <div className="mt-auto pt-6 border-t border-gray-100">
        <p className="text-sm text-gray-700">
          Status Atual:{' '}
          <span className={`font-semibold ${isProcessing ? 'text-amber-500' : 'text-gray-500'}`}>
            {isProcessing ? 'Processando...' : 'Aguardando entrada do usuário'}
          </span>
        </p>
      </div>
    </div>
  );
};

export default WorkflowPanel;
