import axios from 'axios';
import type { Dispatch, SetStateAction } from 'react';

const useFileUpload = (setProgress: Dispatch<SetStateAction<number>>, isOnline: boolean) => {
  const API_URL = import.meta.env.VITE_FASTAPI_URL || 'http://localhost:8000/api';

  const uploadFile = async (file: File, separator: string) => {
    if (!isOnline) {
      console.log('Server offline, aborting operation...');
      return Promise.reject(new Error('Server offline'));
    }

    const formData = new FormData();
    const url = API_URL + `/upload?separator=${separator}`;
    const headers = { 'content-type': 'multipart/form-data' };

    formData.append('file', file, file.name);

    const res = await axios.post(url, formData, {
      headers: headers,
      onUploadProgress: (progressEvent_1) => {
        if (progressEvent_1.total) {
          const percentCompleted = Math.round(
            (progressEvent_1.loaded * 100) / progressEvent_1.total
          );
          setProgress(percentCompleted);
        }
      },
    });
    return res.data;
  };

  return { uploadFile };
};

export default useFileUpload;
