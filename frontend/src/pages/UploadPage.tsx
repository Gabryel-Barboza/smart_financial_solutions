import { useState } from 'react';

import type { CurrentNavSchema } from '../schemas/PropsSchema';

import UploadPanel from '../components/Upload/UploadPanel';
import useFileUpload from '../hooks/useFileUpload';
import { useServerContext } from '../context/serverContext/useServerContext';
import { useToastContext } from '../context/toastContext/useToastContext';

interface Props {
  setSelectedNav: CurrentNavSchema['setSelectedNav'];
}

const UploadPage = ({ setSelectedNav }: Props) => {
  const [progress, setProgress] = useState(0);
  const { isOnline, sessionId, setIsProcessing } = useServerContext();
  const { addToast } = useToastContext();
  const { uploadFile } = useFileUpload(setProgress, isOnline, sessionId);

  const handleUpload = async (file: File, separator: string) => {
    try {
      setIsProcessing(true);
      await uploadFile(file, separator);

      setSelectedNav('Dashboard');
      addToast('Upload do arquivo concluído!', 'success');
    } catch (err) {
      console.log('Falha no upload de arquivos...', err);
      addToast('Não foi possível enviar o arquivo, tente novamente', 'error');
    } finally {
      setProgress(0);
      setIsProcessing(false);
    }
  };

  return (
    <UploadPanel
      progressValue={progress}
      handleUpload={handleUpload}
      setSelectedNav={setSelectedNav}
    />
  );
};

export default UploadPage;
