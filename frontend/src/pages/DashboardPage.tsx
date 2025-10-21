import WorkflowPanel from '../components/WorkflowPanel/WorkflowPanel';
import type { WorkflowCurrentStepSchema } from '../schemas/PropsSchema';

const DashboardPage = ({ currentStep, isProcessing }: WorkflowCurrentStepSchema) => (
  <WorkflowPanel currentStep={currentStep} isProcessing={isProcessing} />
);

export default DashboardPage;
