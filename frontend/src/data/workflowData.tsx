import type { MessageSchema } from '../schemas/InputSchema';

export const initialMessages: MessageSchema[] = [
  {
    id: '83e95645-52e5-4fe6-97eb-0f9a0f09423d',
    sender: 'Agent',
    content: `<p>Olá! Sou o <strong>Smartie 🧠</strong>, seu Agente Analista Fiscal! Quer saber minhas funcionalidades?</p> 
      <ul>
        <li>Antes de começar, você precisa adicionar uma chave de API do seu provedor preferido em ⚙️ <strong>Configurações!</strong></li>
        <li>Depois, você pode alterar o modelo do agente se quiser, por padrão os modelos recomendados foram selecionados.</li>
        <li>Agora é só enviar uma mensagem no chat abaixo e você já estará conversando comigo!</li>
        <li>Para enviar arquivos, use a aba 📁 Novo Upload. Se quiser que eu analise imagens, clique no botão 📎 para anexar ao chat.</li>
      </ul> 
      <p>Que tal começar com uma pergunta sobre minhas capacidades? Você também pode fazer o upload de arquivos na aba "Novo Upload" antes de começar ✅.</p>`,
    time: new Date().toLocaleString([], { hour: '2-digit', minute: '2-digit' }),
  },
];
