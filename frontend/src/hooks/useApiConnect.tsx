import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_FASTAPI_URL;

const useApiConnect = (timeout: number = 0) => {
  const [isOnline, setIsOnline] = useState(false);

  const checkStatus = useCallback(async () => {
    const url = API_URL + '/healthz';

    try {
      const response = (await axios.head(url)).status;

      if (response === 200) setIsOnline(true);
    } catch (err) {
      console.log(err);
    }
  }, []);

  useEffect(() => {
    checkStatus();

    if (timeout) {
      const interval = setInterval(checkStatus, timeout);
      return () => clearInterval(interval);
    }
  }, [timeout, checkStatus]);

  return { isOnline, setIsOnline, checkStatus };
};

export default useApiConnect;
