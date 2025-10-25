import { GoPaperclip } from 'react-icons/go';
import { useRef, type ChangeEvent } from 'react';

import type { ChatInputSchema } from '../../schemas/PropsSchema';
import { useToastContext } from '../../context/toastContext/useToastContext';
import { useServerContext } from '../../context/serverContext/useServerContext';
import type { MessageSchema, ImageContent } from '../../schemas/InputSchema';

interface Props extends ChatInputSchema {
  isChatDisabled: boolean;
  handleSendMessage: () => void;
  uploadImage: (file: File, newMessage: MessageSchema) => Promise<void>;
}

function ChatInput({ input, setInput, isChatDisabled, handleSendMessage, uploadImage }: Props) {
  const inputImageFile = useRef<HTMLInputElement | null>(null);
  const { addToast } = useToastContext();
  const { isProcessing, setIsProcessing } = useServerContext();

  const MAX_FILE_SIZE = 10 * 1024 * 1024;

  /**
   * Envia o evento click para o input de imagem
   */
  const openInput = () => {
    if (inputImageFile.current) inputImageFile.current.click();
  };

  /**
   * Função para tratar o arquivo recebido antes de realizar o upload
   */
  const handleImageUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    try {
      if (e.target.files?.length) {
        const supported_types = ['jpeg', 'png', 'tiff', 'bmp'];
        const file = e.target.files[0];
        const file_type = file.type.split('/')[1];

        // Restrições de arquivo
        if (file.size > MAX_FILE_SIZE)
          throw new Error(
            `Tamanho máximo de imagem atingido: ${Math.round(MAX_FILE_SIZE / 1048756)} mb`
          );

        if (!supported_types.includes(file_type))
          throw new Error(
            `Arquivo incompatível recebido, os formatos suportados são: .${supported_types.join(
              ' .'
            )}`
          );

        // Realizando leitura do arquivo em base64 e começando upload
        const reader = new FileReader();
        reader.onloadend = async () => {
          const fileUrl64 = reader.result as string;

          // Base64 para renderizar no frontend apenas.
          const imageContent: ImageContent = {
            type: 'Image',
            fileUrl: fileUrl64,
            altText: 'Imagem enviada pelo usuário',
          };

          const newMessage: MessageSchema = {
            id: crypto.randomUUID(),
            sender: 'User',
            content: imageContent,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          };

          await uploadImage(file, newMessage);
        };

        setIsProcessing(true);
        reader.readAsDataURL(file);
      }
    } catch (err) {
      console.log(err);

      if (err instanceof Error) addToast(err.message, 'error');
    } finally {
      setIsProcessing(false);
      e.target.value = '';
    }
  };

  return (
    <div className="p-4 bg-white border-t border-gray-200">
      <div className="flex items-center text-black relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyUp={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder={
            isProcessing
              ? 'Aguarde a conclusão do processamento...'
              : 'Pergunte ao Agente Analista...'
          }
          className="flex-1 p-3 pl-9 border border-gray-300 rounded-l-xl focus:ring-blue-500 focus:border-blue-500 transition duration-150 disabled:bg-gray-100"
          disabled={isChatDisabled}
        />
        <button
          className="inline-block absolute left-2 top-[15px] text-2xl cursor-pointer"
          type="button"
          title="Anexar imagem"
          onClick={openInput}
        >
          <GoPaperclip />
        </button>
        <button
          onClick={handleSendMessage}
          disabled={!input.trim() || isChatDisabled}
          className="p-3 bg-blue-600 text-white rounded-r-xl hover:bg-blue-700 transition duration-200 disabled:bg-blue-300 shadow-lg"
        >
          Enviar
        </button>
      </div>
      <input className="hidden" type="file" ref={inputImageFile} onChange={handleImageUpload} />
    </div>
  );
}

export default ChatInput;
