import { useState } from 'react';

import type { CurrentNavSchema } from '../schemas/PropsSchema';

import UploadPanel from '../components/Upload/UploadPanel';
import useFileUpload from '../hooks/useFileUpload';
import { useServerContext } from '../context/serverContext/useServerContext';

interface Props {
  setSelectedNav: CurrentNavSchema['setSelectedNav'];
}

const UploadPage = ({ setSelectedNav }: Props) => {
  const [progress, setProgress] = useState(0);
  const { isOnline } = useServerContext();
  const { uploadFile } = useFileUpload(setProgress, isOnline);

  const handleUpload = async (file: File, separator: string) => {
    try {
      await uploadFile(file, separator);

      setSelectedNav('Dashboard');
    } catch (err) {
      console.log('Falha no upload de arquivos...', err);
    } finally {
      setProgress(0);
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
