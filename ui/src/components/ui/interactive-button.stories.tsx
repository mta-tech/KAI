import type { Meta, StoryObj } from '@storybook/react';
import { InteractiveButton, IconButton } from '@/components/ui/interactive-button';
import { Search, Settings, Trash2, Check } from 'lucide-react';

const meta: Meta<typeof InteractiveButton> = {
  title: 'UI/Interactive Button',
  component: InteractiveButton,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof InteractiveButton>;

export const Default: Story = {
  render: () => <InteractiveButton>Click Me</InteractiveButton>,
};

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <InteractiveButton variant="default">Default</InteractiveButton>
      <InteractiveButton variant="secondary">Secondary</InteractiveButton>
      <InteractiveButton variant="destructive">Destructive</InteractiveButton>
      <InteractiveButton variant="outline">Outline</InteractiveButton>
      <InteractiveButton variant="ghost">Ghost</InteractiveButton>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <InteractiveButton size="sm">Small</InteractiveButton>
      <InteractiveButton size="default">Default</InteractiveButton>
      <InteractiveButton size="lg">Large</InteractiveButton>
    </div>
  ),
};

export const WithIcon: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <InteractiveButton icon={<Settings className="h-4 w-4" />}>
        Settings
      </InteractiveButton>
      <InteractiveButton icon={<Search className="h-4 w-4" />} variant="outline">
        Search
      </InteractiveButton>
      <InteractiveButton icon={<Trash2 className="h-4 w-4" />} variant="destructive">
        Delete
      </InteractiveButton>
    </div>
  ),
};

export const IconButtonOnly: Story = {
  render: () => (
    <div className="flex gap-4">
      <IconButton icon={<Settings className="h-4 w-4" />} label="Settings" />
      <IconButton icon={<Search className="h-4 w-4" />} label="Search" variant="outline" />
      <IconButton icon={<Check className="h-4 w-4" />} label="Check" variant="secondary" />
      <IconButton icon={<Trash2 className="h-4 w-4" />} label="Delete" variant="destructive" />
    </div>
  ),
};

export const NoRipple: Story = {
  render: () => <InteractiveButton ripple={false}>No Ripple</InteractiveButton>,
};

export const NoScale: Story = {
  render: () => <InteractiveButton scale={false}>No Scale</InteractiveButton>,
};

export const Disabled: Story = {
  render: () => <InteractiveButton disabled>Disabled</InteractiveButton>,
};

export const Mobile: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4">
        <InteractiveButton ripple scale>Full Features</InteractiveButton>
        <InteractiveButton variant="outline" ripple scale>Outline</InteractiveButton>
        <IconButton icon={<Settings className="h-4 w-4" />} label="Settings" />
      </div>
      <p className="text-sm text-muted-foreground">
        Touch and hold to see active states (on touch devices)
      </p>
    </div>
  ),
  parameters: {
    viewport: {
      defaultViewport: 'iphone12',
    },
  },
};

export const ReducedMotion: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <InteractiveButton>Hover Me</InteractiveButton>
      <InteractiveButton variant="outline">Outline</InteractiveButton>
      <IconButton icon={<Settings className="h-4 w-4" />} label="Settings" />
    </div>
  ),
  parameters: {
    prefersReducedMotion: 'reduce',
  },
};
