import type { Meta, StoryObj } from '@storybook/react';
import { ChatSearch } from './chat-search';
import type { ChatMessage } from '@/stores/chat-store';

const mockMessages: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'user',
    content: 'Show me the sales data for last month',
    timestamp: new Date('2024-01-15T10:30:00'),
  },
  {
    id: 'msg-2',
    role: 'assistant',
    content: 'I can help you analyze the sales data. Let me query the database.',
    timestamp: new Date('2024-01-15T10:30:15'),
    structured: {
      sql: 'SELECT * FROM sales WHERE date >= NOW() - INTERVAL 1 MONTH',
      summary: 'This query retrieves all sales transactions from the past month.',
    },
  },
  {
    id: 'msg-3',
    role: 'assistant',
    content: 'Here are the insights from the sales data:',
    timestamp: new Date('2024-01-15T10:31:00'),
    structured: {
      insights: '• Total sales increased by 15% compared to previous month\n• Top performing product category was Electronics\n• Customer satisfaction scores improved',
    },
    todos: [
      { content: 'Analyze sales trends', status: 'completed' },
      { content: 'Generate visualizations', status: 'in_progress' },
    ],
  },
  {
    id: 'msg-4',
    role: 'user',
    content: 'What about customer data?',
    timestamp: new Date('2024-01-16T14:20:00'),
  },
  {
    id: 'msg-5',
    role: 'assistant',
    content: 'Let me fetch the customer information for you.',
    timestamp: new Date('2024-01-16T14:20:30'),
  },
];

const meta: Meta<typeof ChatSearch> = {
  title: 'Chat/ChatSearch',
  component: ChatSearch,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    messages: {
      control: 'object',
      description: 'Array of chat messages to search through',
    },
    sessions: {
      control: 'object',
      description: 'Array of chat sessions',
    },
    onResultsFound: {
      action: 'onResultsFound',
      description: 'Callback when search results change',
    },
    onResultClick: {
      action: 'onResultClick',
      description: 'Callback when a search result is clicked',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ChatSearch>;

export const Default: Story = {
  args: {
    messages: mockMessages,
    sessions: [],
  },
};

export const EmptyState: Story = {
  args: {
    messages: [],
    sessions: [],
  },
};

export const WithManyMessages: Story = {
  args: {
    messages: Array.from({ length: 50 }, (_, i) => ({
      id: `msg-${i}`,
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Sample message ${i} with some content to search through`,
      timestamp: new Date(Date.now() - i * 3600000),
      structured: i % 3 === 0 ? {
        sql: `SELECT * FROM table_${i}`,
        summary: `This is a summary for message ${i}`,
      } : undefined,
    })),
    sessions: [],
  },
};