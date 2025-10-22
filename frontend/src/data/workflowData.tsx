import type { Message } from '../schemas/InputSchema';

export const initialMessages: Message[] = [
  {
    id: '83e95645-52e5-4fe6-97eb-0f9a0f09423d',
    sender: 'Agent',
    content:
      'Olá! Sou o Smartie 🧠, seu Agente Analista Fiscal. Para uma melhor resposta, realize o upload de um arquivo que gostaria de analisar ✅.',
    time: new Date().toLocaleString([], { hour: '2-digit', minute: '2-digit' }),
  },
];
