import axios from 'axios';
import { useState } from 'react';

import { useServerContext } from '../../context/serverContext/useServerContext';
import { useToastContext } from '../../context/toastContext/useToastContext';

const UserInput = () => {
  const { addToast } = useToastContext();
  const { API_URL, sessionId } = useServerContext();
  const [email, setEmail] = useState('');

  const handleInfoRegister = async () => {
    const url = API_URL + '/send-email';
    const data = { user_email: email, session_id: sessionId };

    try {
      await axios.post(url, data);

      addToast('Informações registradas com sucesso!', 'success');
    } catch (err) {
      console.log(err);
      addToast('Failed to save user information, please try again', 'error');
    } finally {
      setEmail('');
    }
  };

  return (
    <div className="flex flex-col">
      <label className="font-medium text-gray-700 mb-1" htmlFor="user_email_input">
        Email:{' '}
      </label>
      <input
        id="user_email_input"
        className="p-3 border border-blue-400 rounded-lg focus:ring-blue-500 focus:border-blue-500"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button
        className="mt-4 py-3 px-6 bg-blue-600 text-white font-bold rounded-lg shadow-lg hover:bg-blue-700 transition duration-150"
        type="button"
        onClick={handleInfoRegister}
      >
        Salvar
      </button>
    </div>
  );
};

export default UserInput;
