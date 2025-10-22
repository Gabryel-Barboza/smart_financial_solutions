import type { ChangeEvent } from 'react';
import type { CurrentNavSchema } from '../../schemas/PropsSchema';

import { useRef, useCallback, useState } from 'react';
import { AiOutlineCloudUpload } from 'react-icons/ai';

import styles from './UploadPanel.module.css';

interface Props {
  progressValue: number;
  setSelectedNav: CurrentNavSchema['setSelectedNav'];
  handleUpload: (file: File, separator: string) => Promise<void>;
}

const UploadPanel = ({ progressValue, handleUpload, setSelectedNav }: Props) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [separator, setSeparator] = useState(',');
  const buttonClass =
    'text-black px-4 mx-4 mb-4 py-2 border border-dashed border-blue-400 rounded-sm cursor-pointer hover:bg-blue-100';

  const handleContainerClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      handleUpload(e.target.files[0], separator).catch((err) =>
        console.log('Error em UploadPanel: ', err)
      );
      e.target.value = '';
    }
  };

  return (
    <div className="p-8 bg-white shadow-xl rounded-2xl h-full flex flex-col items-center justify-center text-center text-black">
      <h2 className="text-2xl font-extrabold text-gray-800 mb-4">Novo Lote Fiscal</h2>
      <p className="text-gray-600 mb-6 max-w-sm">
        Selecione o separador correto e envie seu arquivo (.csv, .xlsx ou .zip) para popular os
        dados de análise do agente.
      </p>
      <div>
        <button className={buttonClass} type="button" onClick={() => setSeparator(',')}>
          ,
        </button>
        <button className={buttonClass} type="button" onClick={() => setSeparator(';')}>
          ;
        </button>
        <button className={buttonClass} type="button" onClick={() => setSeparator('\\t')}>
          tab
        </button>
      </div>

      <div className="mb-5 text-center">
        Separador → <span className="inline-block text-center w-5 bg-blue-100">{separator}</span>{' '}
      </div>

      <div
        className="w-full max-w-xs p-6 border-2 border-dashed border-blue-400 rounded-xlm text-black bg-blue-50 hover:bg-blue-100 cursor-pointer transition-colors duration-200"
        onClick={handleContainerClick}
      >
        <span className="block w-fit mx-auto font-bold text-4xl">
          <AiOutlineCloudUpload />
        </span>
        <p className="text-sm text-blue-700 font-medium">Clique para selecionar o arquivo</p>
        <input
          type="file"
          ref={fileInputRef}
          id="file-upload"
          className="hidden"
          onChange={handleFileUpload}
        />
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
