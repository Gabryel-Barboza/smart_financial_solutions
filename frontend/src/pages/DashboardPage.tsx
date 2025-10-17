import WorkflowPanel from '../components/WorkflowPanel/WorkflowPanel';

const DashboardPage = ({ currentStep, isProcessing }) => (
  <WorkflowPanel currentStep={currentStep} isProcessing={isProcessing} />
);

export default DashboardPage;
