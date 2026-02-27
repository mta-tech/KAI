import type { Meta, StoryObj } from '@storybook/react';
import { ModelSelector } from './model-selector';
import { DEFAULT_MODEL } from '@/lib/llm-providers';

const meta: Meta<typeof ModelSelector> = {
  title: 'Chat/ModelSelector',
  component: ModelSelector,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    value: {
      control: 'text',
      description: 'Currently selected model ID',
    },
    onChange: {
      action: 'onChange',
      description: 'Called with new model ID when selection changes',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable the selector (e.g. during streaming)',
    },
  },
  args: {
    onChange: (model: string) => console.log('Model changed:', model),
  },
};

export default meta;
type Story = StoryObj<typeof ModelSelector>;

export const Default: Story = {
  args: {
    value: DEFAULT_MODEL,
  },
};

export const GPT4o: Story = {
  args: {
    value: 'gpt-4o',
  },
};

export const Disabled: Story = {
  args: {
    value: DEFAULT_MODEL,
    disabled: true,
  },
};

export const CustomModel: Story = {
  args: {
    value: 'claude-3-5-sonnet',
  },
};
