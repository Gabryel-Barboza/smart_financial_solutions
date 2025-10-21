import type { Message } from '../schemas/InputSchema';

export const initialMessages: Message[] = [
  {
    id: 1,
    sender: 'Agent',
    text: 'Olá! Sou o Smartie, seu Agente Analista Fiscal. Para uma melhor resposta, realize o upload de um arquivo que gostaria de analisar.',
    time: new Date().toLocaleString([], { hour: '2-digit', minute: '2-digit' }),
  },
];
