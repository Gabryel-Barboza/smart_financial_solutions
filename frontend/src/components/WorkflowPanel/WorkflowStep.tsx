import type { WorkflowCurrentStepSchema } from '../../schemas/PropsSchema';

interface Props extends WorkflowCurrentStepSchema {}

const WorkflowStep = ({ step, index, currentStep, workflowSteps, isProcessing }: Props) => {
  const isActive = index === currentStep && isProcessing;
  const isCompleted =
    index < currentStep ||
    (!isProcessing && index < workflowSteps.length - 1 && currentStep === workflowSteps.length);
  const statusColor = isCompleted ? 'text-green-600' : isActive ? 'text-blue-500' : 'text-gray-400';
  const ringColor = isCompleted ? 'ring-green-300' : isActive ? 'ring-blue-300' : 'ring-gray-200';

  return (
    <div className="flex items-start mb-6 last:mb-0 relative">
      {/* Linha de Conexão */}
      {index < workflowSteps.length - 1 && (
        <div
          className={`absolute top-4 left-[10px] w-0.5 h-full ${
            isCompleted ? 'bg-green-500' : 'bg-gray-200'
          }`}
        ></div>
      )}

      {/* Ícone de Status */}
      <div
        className={`z-10 w-5 h-5 flex items-center justify-center rounded-full ring-4 ${ringColor} ${
          isCompleted ? 'bg-green-500' : isActive ? 'bg-blue-500' : 'bg-gray-100'
        } mr-4 transition-all duration-300`}
      >
        {isCompleted ? (
          <svg
            className="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            ></path>
          </svg>
        ) : (
          <div
            className={`w-2 h-2 rounded-full ${
              isActive ? 'bg-white animate-pulse' : 'bg-gray-400'
            }`}
          ></div>
        )}
      </div>

      {/* Conteúdo do Passo */}
      <div
        className={`flex-1 ${statusColor} ${
          isProcessing ? 'font-medium' : 'font-normal'
        } transition-colors duration-300`}
      >
        <h3 className="text-lg leading-tight">{step.name}</h3>
        <p className="text-sm text-gray-500 mt-1">{step.desc}</p>
      </div>
    </div>
  );
};

export default WorkflowStep;
