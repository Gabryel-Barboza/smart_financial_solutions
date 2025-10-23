import type { JSX } from 'react';

interface Message {
  id: string;
  sender: 'Agent' | 'System' | 'User';
  content: string | JSX.Element;
  time: string;
}

interface Response {
  response: string;
  graph_id?: string;
}

interface WorkflowStepSchema {
  key: string;
  name: string;
  desc: string;
  workflowStatus: 'pending' | 'in-progress' | 'complete' | 'error';
}

interface NavItem {
  name: string;
  icon: string;
  current: boolean;
}

export type { Message, WorkflowStepSchema, NavItem, Response };
