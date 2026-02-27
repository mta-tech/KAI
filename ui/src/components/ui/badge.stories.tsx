import type { Meta, StoryObj } from '@storybook/react';
import { Badge, badgeVariants } from './badge';

const meta = {
  title: 'UI/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline'],
    },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Badge',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary',
  },
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
    children: 'Destructive',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Outline',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Badge>Default</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="destructive">Destructive</Badge>
      <Badge variant="outline">Outline</Badge>
    </div>
  ),
};

export const StatusBadges: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Badge variant="default">Active</Badge>
      <Badge variant="secondary">Inactive</Badge>
      <Badge variant="destructive">Error</Badge>
      <Badge variant="outline">Pending</Badge>
    </div>
  ),
};

export const WithText: Story = {
  render: () => (
    <div>
      <span className="text-sm">Status: </span>
      <Badge variant="default">Online</Badge>
    </div>
  ),
};

export const SmallText: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Badge>v1.0</Badge>
      <Badge variant="secondary">Beta</Badge>
      <Badge variant="outline">New</Badge>
      <Badge variant="destructive">!</Badge>
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Badge>🔥 Hot</Badge>
      <Badge variant="secondary">⭐ Featured</Badge>
      <Badge variant="outline">💡 Tip</Badge>
    </div>
  ),
};
