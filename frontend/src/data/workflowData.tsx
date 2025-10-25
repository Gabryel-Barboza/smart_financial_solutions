import type { MessageSchema } from '../schemas/InputSchema';

export const initialMessages: MessageSchema[] = [
  {
    id: '83e95645-52e5-4fe6-97eb-0f9a0f09423d',
    sender: 'Agent',
    content:
      '<p>Olá! Sou o Smartie 🧠, seu Agente Analista Fiscal!</p> <p>Que tal começar com uma pergunta sobre minhas capacidades? Você também pode fazer o upload de arquivos na aba "Novo Upload" antes de começar ✅.</p>',
    time: new Date().toLocaleString([], { hour: '2-digit', minute: '2-digit' }),
  },
];
