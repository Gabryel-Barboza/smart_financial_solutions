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

export type { Message, WorkflowStep, NavItem, Response };
