interface AvailableModels {
  [modelName: string]: string;
}

interface DefaultModels {
  [provider: string]: {
    [task: string]: string;
  };
}

interface AgentInfo {
  availableModels: AvailableModels;
  defaultModels: DefaultModels;
  tasks: string[];
}

export type { AgentInfo, AvailableModels, DefaultModels };
