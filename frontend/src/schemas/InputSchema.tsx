interface Message {
  id: number;
  sender: 'Agent' | 'System' | 'User';
  text: string;
  time: string;
}

interface WorkflowStep {
  key: string;
  name: string;
  desc: string;
  status: 'pending' | 'in-progress' | 'complete' | 'error';
}

interface NavItem {
  name: string;
  icon: string;
  current: boolean;
}

export type { Message, WorkflowStep, NavItem };
