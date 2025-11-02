import clsx from 'clsx';
import type { WorkflowStepSchema } from '../../schemas/InputSchema';

interface Props {
  step: WorkflowStepSchema;
  currentStep?: WorkflowStepSchema;
  isLast: boolean;
}

const WorkflowStep = ({ step, currentStep, isLast }: Props) => {
  const isComplete = step.workflowStatus === 'complete';
  const isActive = step.key === currentStep?.key;

  const stepIconClass = clsx('w-4 h-4 p-2 border-8 border-gray-400 rounded-full', {
    'bg-gray-600': step.workflowStatus === 'pending' && isActive,
    'bg-amber-300': step.workflowStatus === 'in-progress' && isActive,
    'bg-green-500': isComplete || !isActive,
    'animate-pulse': isActive && !isLast,
  });

  const arrowClass = clsx('w-0.5 h-full max-h-10 ml-[15px]', {
    'bg-green-500': !isActive,
    'bg-black': isActive,
  });

  return (
    <>
      <div className="flex justify-start gap-2 text-gray-800 relative">
        <div className={stepIconClass}></div>
        <p className="absolute top-1 left-10">{step.desc}</p>
      </div>
      {!isLast && <div className={arrowClass}></div>}
    </>
  );
};

export default WorkflowStep;
