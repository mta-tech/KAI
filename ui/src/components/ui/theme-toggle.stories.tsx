import type { Meta, StoryObj } from '@storybook/react';
import { ThemeToggle } from './theme-toggle';
import { useTheme } from '@/lib/stores/theme-store';

const meta = {
  title: 'UI/ThemeToggle',
  component: ThemeToggle,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  decorators: [
    (Story, context) => {
      // Set theme based on story globals
      const theme = context.globals.theme || 'light';
      const backgroundColor = theme === 'dark' ? '#09090b' : '#ffffff';
      
      return (
        <div style={{ backgroundColor, padding: '2rem', borderRadius: '0.5rem' }}>
          <Story />
        </div>
      );
    },
  ],
} satisfies Meta<typeof ThemeToggle>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <ThemeToggle />,
};

export const InHeader: Story = {
  render: () => (
    <div className="flex items-center justify-between w-[300px] border rounded-md p-3 bg-background">
      <span className="text-sm font-medium">Settings</span>
      <ThemeToggle />
    </div>
  ),
};

export const WithMultipleButtons: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <button className="px-3 py-2 text-sm rounded-md border bg-background hover:bg-accent">
        Cancel
      </button>
      <button className="px-3 py-2 text-sm rounded-md bg-primary text-primary-foreground">
        Save
      </button>
      <ThemeToggle />
    </div>
  ),
};

export const DarkModePreview: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="p-4 rounded-lg border bg-card text-card-foreground">
        <h3 className="font-semibold mb-2">Card Example</h3>
        <p className="text-sm text-muted-foreground mb-4">
          This component adapts to the current theme automatically.
        </p>
        <ThemeToggle />
      </div>
    </div>
  ),
  globals: {
    theme: 'dark',
  },
};

export const LightModePreview: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="p-4 rounded-lg border bg-card text-card-foreground">
        <h3 className="font-semibold mb-2">Card Example</h3>
        <p className="text-sm text-muted-foreground mb-4">
          This component adapts to the current theme automatically.
        </p>
        <ThemeToggle />
      </div>
    </div>
  ),
  globals: {
    theme: 'light',
  },
};
