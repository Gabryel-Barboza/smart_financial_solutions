import type { WorkflowCurrentStepSchema } from '../schemas/PropsSchema';

import WorkflowPanel from '../components/WorkflowPanel/WorkflowPanel';

const DashboardPage = ({ currentStep, isProcessing }: WorkflowCurrentStepSchema) => (
  <WorkflowPanel currentStep={currentStep} isProcessing={isProcessing} />
);

export default DashboardPage;
