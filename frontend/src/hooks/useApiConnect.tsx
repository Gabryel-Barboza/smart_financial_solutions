import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

const useApiConnect = (timeout: number = 0) => {
  const API_URL = import.meta.env.VITE_FASTAPI_URL || 'http://localhost:8000/api';
  const [isOnline, setIsOnline] = useState(false);

  const checkStatus = useCallback(async () => {
    const url = API_URL + '/healthz';

    try {
      const response = (await axios.head(url)).status;

      if (response === 200) setIsOnline(true);
    } catch (err) {
      setIsOnline(false);
      console.log(err);
    }
  }, [API_URL]);

  useEffect(() => {
    checkStatus();

    if (timeout) {
      const interval = setInterval(checkStatus, timeout);
      return () => clearInterval(interval);
    }
  }, [timeout, checkStatus]);

  return { isOnline, setIsOnline, API_URL };
};

export default useApiConnect;
