import axios from 'axios';
import type { Dispatch, SetStateAction } from 'react';

const useFileUpload = (setProgress: Dispatch<SetStateAction<number>>, isOnline: boolean) => {
  const API_URL = import.meta.env.VITE_FASTAPI_URL;

  const uploadFile = (file: File) => {
    if (!isOnline) {
      console.log('Server offline, aborting operation...');
      return Promise.reject(new Error('Server offline'));
    }

    const formData = new FormData();
    const url = API_URL + '/upload';

    formData.append('file', file, file.name);

    const response = axios
      .post(url, formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percentCompleted);
          }
        },
      })
      .then((res) => res.data);

    return response;
  };

  return { uploadFile };
};

export default useFileUpload;
