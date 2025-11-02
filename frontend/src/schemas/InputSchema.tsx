import type { JSX } from 'react';
import type { Data, Layout } from 'plotly.js';

interface ImageContent {
  type: 'Image';
  fileUrl: string;
  altText: string;
}

const MessageStyleEnum = {
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

type MessageStyle = (typeof MessageStyleEnum)[keyof typeof MessageStyleEnum];

interface MessageSchema {
  id: string;
  sender: 'Agent' | 'System' | 'User';
  content: string | JSX.Element | ImageContent;
  time: string;
  style: string;
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
  ToastDataSchema,
  MessageSchema,
  MessageStyle,
  PlotlyFigure,
  ImageContent,
  WorkflowStepSchema,
  NavItemSchema,
  ResponseSchema,
  ResponseGraphSchema,
};

export { MessageStyleEnum };
