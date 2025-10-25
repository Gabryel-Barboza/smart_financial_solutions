import axios from 'axios';
import type { Dispatch, SetStateAction } from 'react';

const useFileUpload = (
  isOnline: boolean,
  sessionId: string,
  setProgress?: Dispatch<SetStateAction<number>>
) => {
  const uploadFile = async (file: File, url: string) => {
    if (!isOnline) {
      console.log('Server offline, aborting operation...');
      return Promise.reject(new Error('Server offline'));
    }

    const formData = new FormData();
    const headers = { 'content-type': 'multipart/form-data' };

    formData.append('file', file, file.name);
    formData.append('session_id', sessionId);

    const res = await axios.post(url, formData, {
      headers: headers,
      onUploadProgress: (progressEvent_1) => {
        if (progressEvent_1.total && setProgress) {
          const percentCompleted = Math.round(
            (progressEvent_1.loaded * 100) / progressEvent_1.total
          );

          setProgress(percentCompleted);
        }
      },
    });

    return res;
  };

  return { uploadFile };
};

export default useFileUpload;
