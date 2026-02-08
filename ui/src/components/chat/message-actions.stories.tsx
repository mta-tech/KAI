import type { Meta, StoryObj } from '@storybook/react';
import { MessageActions, MessageQuickActions } from './message-actions';
import type { ChatMessage } from '@/stores/chat-store';

const mockUserMessage: ChatMessage = {
  id: 'msg-user-1',
  role: 'user',
  content: 'Show me the sales data for last quarter',
  timestamp: new Date('2024-01-15T10:30:00'),
};

const mockAssistantMessage: ChatMessage = {
  id: 'msg-assistant-1',
  role: 'assistant',
  content: 'I can help you analyze the sales data. Here\'s what I found for the last quarter.',
  timestamp: new Date('2024-01-15T10:30:15'),
  structured: {
    sql: 'SELECT SUM(amount) as total_sales FROM sales WHERE date >= NOW() - INTERVAL 3 MONTH',
    summary: 'Total sales increased by 15% compared to the previous quarter',
  },
};

const mockStreamingMessage: ChatMessage = {
  id: 'msg-streaming-1',
  role: 'assistant',
  content: 'Let me fetch that data for you...',
  timestamp: new Date('2024-01-15T10:31:00'),
  isStreaming: true,
};

const meta: Meta<typeof MessageActions> = {
  title: 'Chat/MessageActions',
  component: MessageActions,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    message: {
      control: 'object',
      description: 'The chat message to attach actions to',
    },
    onRegenerate: {
      action: 'onRegenerate',
      description: 'Callback when regenerate is clicked',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable all actions',
    },
  },
};

export default meta;
type Story = StoryObj<typeof MessageActions>;

export const UserMessage: Story = {
  args: {
    message: mockUserMessage,
  },
};

export const AssistantMessage: Story = {
  args: {
    message: mockAssistantMessage,
  },
};

export const AssistantMessageWithSQL: Story = {
  args: {
    message: mockAssistantMessage,
  },
};

export const StreamingMessage: Story = {
  args: {
    message: mockStreamingMessage,
  },
};

export const Disabled: Story = {
  args: {
    message: mockAssistantMessage,
    disabled: true,
  },
};

// Stories for Quick Actions
const quickActionsMeta: Meta<typeof MessageQuickActions> = {
  title: 'Chat/MessageQuickActions',
  component: MessageQuickActions,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export { quickActionsMeta as QuickActionsMeta };
type QuickActionsStory = StoryObj<typeof MessageQuickActions>;

export const QuickActionsUser: QuickActionsStory = {
  args: {
    message: mockUserMessage,
  },
};

export const QuickActionsAssistant: QuickActionsStory = {
  args: {
    message: mockAssistantMessage,
  },
};

export const QuickActionsStreaming: QuickActionsStory = {
  args: {
    message: mockStreamingMessage,
  },
};