import type { Dispatch, SetStateAction } from 'react';

interface CurrentNavSchema {
  selectedNav: string;
  setSelectedNav: Dispatch<SetStateAction<string>>;
}

interface ChatInputSchema {
  input: string;
  setInput: Dispatch<SetStateAction<string>>;
}

export type { CurrentNavSchema, ChatInputSchema };
