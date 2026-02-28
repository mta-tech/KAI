import type { Meta, StoryObj } from '@storybook/react';
import { ScanWizard } from './scan-wizard';
import { useState } from 'react';

const mockConnection = {
  id: 'conn-123',
  alias: 'Test Database',
  dialect: 'postgresql',
  created_at: new Date().toISOString(),
};

const meta: Meta<typeof ScanWizard> = {
  title: 'Schema/ScanWizard',
  component: ScanWizard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    open: {
      control: 'boolean',
      description: 'Controls whether the wizard is open',
    },
    onOpenChange: {
      action: 'onOpenChange',
      description: 'Callback when wizard open state changes',
    },
    connection: {
      control: 'object',
      description: 'The database connection to scan',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ScanWizard>;

export const Default: Story = {
  args: {
    open: true,
    connection: mockConnection,
  },
};

export const WithoutConnection: Story = {
  args: {
    open: true,
    connection: null,
  },
};

export const WithDemoState = () => {
  const [open, setOpen] = useState(true);
  const [step, setStep] = useState<'welcome' | 'options' | 'tables' | 'ai-config' | 'progress' | 'complete'>('welcome');

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setStep('welcome')}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Welcome
        </button>
        <button
          onClick={() => setStep('options')}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Options
        </button>
        <button
          onClick={() => setStep('ai-config')}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          AI Config
        </button>
        <button
          onClick={() => setStep('progress')}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Progress
        </button>
        <button
          onClick={() => setStep('complete')}
          className="px-3 py-1 bg-gray-200 rounded"
        >
          Complete
        </button>
      </div>
      <ScanWizard
        open={open}
        onOpenChange={setOpen}
        connection={mockConnection}
      />
    </div>
  );
};

WithDemoState.parameters = {
  docs: {
    description: {
      story: 'Demo with manual step navigation for testing different wizard states',
    },
  },
};