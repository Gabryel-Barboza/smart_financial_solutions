import WorkflowStep from './WorkflowStep';
import { workflowSteps } from '../../data/workflowData';

const WorkflowPanel = ({ currentStep, isProcessing }) => {
  return (
    <div className="p-6 bg-white shadow-xl rounded-2xl h-full flex flex-col">
      <h2 className="text-2xl font-extrabold text-gray-800 mb-6">
        Status do Processamento LangGraph
      </h2>

      {workflowSteps.map((step, index) => (
        <WorkflowStep
          key={step.key}
          step={step}
          index={index}
          currentStep={currentStep}
          isProcessing={isProcessing}
          workflowSteps={workflowSteps}
        />
      ))}

      <div className="mt-auto pt-6 border-t border-gray-100">
        <p className="text-sm text-gray-700">
          Status Atual:{' '}
          <span
            className={`font-semibold ${
              isProcessing
                ? 'text-amber-500'
                : currentStep === workflowSteps.length
                ? 'text-green-600'
                : 'text-gray-500'
            }`}
          >
            {isProcessing
              ? 'Processando...'
              : currentStep === workflowSteps.length
              ? 'Análise Liberada'
              : 'Aguardando Arquivo'}
          </span>
        </p>
      </div>
    </div>
  );
};

export default WorkflowPanel;
