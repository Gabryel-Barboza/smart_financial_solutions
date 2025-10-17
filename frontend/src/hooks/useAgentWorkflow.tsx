import { useState, useEffect } from 'react';
import { workflowSteps } from '../data/workflowData';

const useAgentWorkflow = (setMessages) => {
  const [currentStep, setCurrentStep] = useState(0); // 0 a 3
  const [isProcessing, setIsProcessing] = useState(false);

  // Efeito para simular o fluxo de processamento
  useEffect(() => {
    if (isProcessing && currentStep < workflowSteps.length) {
      const timer = setTimeout(() => {
        const nextStep = currentStep + 1;
        setCurrentStep(nextStep);

        // Quando chega na etapa de Análise, o chat é liberado
        if (nextStep === workflowSteps.length) {
          setIsProcessing(false);
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now() + 1,
              sender: 'Agent',
              text: 'Processamento de dados concluído com sucesso! Agora você pode interagir comigo no chat. Tente: "Quais são as 5 maiores divergências de ICMS?"',
              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        } else {
          // Continua o loop do processamento
          setIsProcessing(true);
        }
      }, 2500); // Simula o tempo de processamento de cada etapa

      return () => clearTimeout(timer);
    }
  }, [isProcessing, currentStep, setMessages]); // Adicionado setMessages para evitar warning, embora seja estável

  // Simula o upload e inicia o workflow
  const handleUpload = (fileName) => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        sender: 'System',
        text: `Iniciando o processamento do arquivo: "${fileName}".`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setCurrentStep(0); // Reseta para o primeiro passo
    setIsProcessing(true); // Inicia a simulação do workflow
  };

  return { currentStep, isProcessing, handleUpload };
};

export default useAgentWorkflow;
