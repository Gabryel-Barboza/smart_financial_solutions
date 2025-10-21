import type { ChangeEvent } from 'react';
import { AiOutlineCloudUpload } from 'react-icons/ai';

import styles from './UploadPanel.module.css';

import type { CurrentNavSchema } from '../../schemas/PropsSchema';

interface Props {
  progressValue: number;
  handleUpload: (file: File) => Promise<void>;
  setSelectedNav: CurrentNavSchema['setSelectedNav'];
}

const UploadPanel = ({ progressValue, handleUpload, setSelectedNav }: Props) => {
  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      handleUpload(e.target.files[0]).catch((err) => console.log('Error em UploadPanel: ', err));
      e.target.value = '';
    }
  };

  return (
    <div className="p-8 bg-white shadow-xl rounded-2xl h-full flex flex-col items-center justify-center text-center">
      <h2 className="text-2xl font-extrabold text-gray-800 mb-4">Novo Lote Fiscal</h2>
      <p className="text-gray-600 mb-6 max-w-sm">
        Envie seu arquivo (.csv, .xlsx ou .zip) para popular os dados de análise do agente.
      </p>

      <div
        className="w-full max-w-xs p-6 border-2 border-dashed border-blue-400 rounded-xlm text-black bg-blue-50 hover:bg-blue-100 cursor-pointer transition-colors duration-200"
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <span className="block w-fit mx-auto font-bold text-4xl">
          <AiOutlineCloudUpload />
        </span>
        <p className="text-sm text-blue-700 font-medium">Clique para selecionar o arquivo</p>
        <input type="file" id="file-upload" className="hidden" onChange={handleFileUpload} />
      </div>
      <progress
        className={`${styles.progress} ${progressValue ? '' : 'hidden'}`}
        value={progressValue || 0}
        max="100"
      />

      <button
        onClick={() => setSelectedNav('Dashboard')}
        className="p-3 mt-6 rounded-sm text-sm font-medium text-blue-500 bg-gray-800 hover:text-black hover:bg-blue-700 transition-all duration-300"
      >
        Ver Status do Workflow
      </button>
    </div>
  );
};

export default UploadPanel;
