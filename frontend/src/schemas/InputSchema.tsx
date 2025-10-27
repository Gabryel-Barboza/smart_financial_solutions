import type { JSX } from 'react';
import type { Data, Layout } from 'plotly.js';

interface ImageContent {
  type: 'Image';
  fileUrl: string;
  altText: string;
}

interface MessageSchema {
  id: string;
  sender: 'Agent' | 'System' | 'User';
  content: string | JSX.Element | ImageContent;
  time: string;
}

interface ResponseSchema {
  response: string;
  graph_id?: string | string[];
}

interface ResponseGraphSchema {
  graph: string;
}

interface PlotlyFigure {
  data: Data[];
  layout: Partial<Layout>;
}

interface WorkflowStepSchema {
  key: string;
  name: string;
  desc: string;
  workflowStatus: 'pending' | 'in-progress' | 'complete' | 'error';
}

interface ToastDataSchema {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  message: string;
}

interface NavItemSchema {
  name: string;
  icon: string;
  current: boolean;
}

export type {
  MessageSchema,
  WorkflowStepSchema,
  NavItemSchema,
  ResponseSchema,
  ToastDataSchema,
  ImageContent,
  ResponseGraphSchema,
  PlotlyFigure,
};
