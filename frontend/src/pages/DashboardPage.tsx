import WorkflowPanel from '../components/WorkflowPanel/WorkflowPanel';
import { useServerContext } from '../context/serverContext/useServerContext';

const DashboardPage = () => {
  const { isProcessing } = useServerContext();
  const currentStep = 0;

  return <WorkflowPanel currentStep={currentStep} isProcessing={isProcessing} />;
};

export default DashboardPage;
