import type { Meta, StoryObj } from '@storybook/react';
import { ToolCallBlock } from './index';
import type { AgentEvent } from '@/lib/api/types';

const sqlStartEvent: AgentEvent = {
  type: 'tool_start',
  tool: 'sql_execute',
  input: { query: 'SELECT id, name, email, amount FROM customers ORDER BY amount DESC LIMIT 10' },
};

const sqlEndEvent: AgentEvent = {
  type: 'tool_end',
  tool: 'sql_execute',
  output: JSON.stringify({
    results: [
      { id: 1, name: 'Alice Johnson', email: 'alice@example.com', amount: 15000 },
      { id: 2, name: 'Bob Smith', email: 'bob@example.com', amount: 12500 },
      { id: 3, name: 'Carol White', email: 'carol@example.com', amount: 9800 },
    ],
    columns: ['id', 'name', 'email', 'amount'],
    row_count: 3,
    execution_time: 180,
  }),
};

const searchStartEvent: AgentEvent = {
  type: 'tool_start',
  tool: 'search',
  input: { query: 'quarterly revenue by product category' },
};

const searchEndEvent: AgentEvent = {
  type: 'tool_end',
  tool: 'search',
  output: JSON.stringify({
    results: [
      { title: 'Q4 Revenue Report', content: 'Electronics: $2.4M, Clothing: $1.8M, Food: $950K' },
      { title: 'Product Category Analysis', content: 'Year-over-year growth in Electronics: 23%' },
    ],
    count: 2,
  }),
};

const genericStartEvent: AgentEvent = {
  type: 'tool_start',
  tool: 'fetch_metrics',
  input: { metric: 'conversion_rate', period: 'last_30_days' },
};

const genericEndEvent: AgentEvent = {
  type: 'tool_end',
  tool: 'fetch_metrics',
  output: { conversion_rate: 3.2, change: '+0.4%', period: '2024-01-01 to 2024-01-30' },
};

const meta: Meta<typeof ToolCallBlock> = {
  title: 'Chat/ToolCallBlock',
  component: ToolCallBlock,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    event: {
      control: 'object',
      description: 'The tool_start event',
    },
    result: {
      control: 'object',
      description: 'The tool_end event (optional, absent when streaming)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ToolCallBlock>;

export const SqlExecuteCompleted: Story = {
  args: {
    event: sqlStartEvent,
    result: sqlEndEvent,
  },
};

export const SqlExecuteStreaming: Story = {
  args: {
    event: sqlStartEvent,
  },
};

export const SearchCompleted: Story = {
  args: {
    event: searchStartEvent,
    result: searchEndEvent,
  },
};

export const SearchStreaming: Story = {
  args: {
    event: searchStartEvent,
  },
};

export const GenericToolCompleted: Story = {
  args: {
    event: genericStartEvent,
    result: genericEndEvent,
  },
};

export const GenericToolStreaming: Story = {
  args: {
    event: genericStartEvent,
  },
};
