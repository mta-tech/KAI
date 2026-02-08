import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { CommandPalette, CommandTrigger } from '@/components/ui/command-palette';

const meta: Meta<typeof CommandPalette> = {
  title: 'UI/Command Palette',
  component: CommandPalette,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof CommandPalette>;

export const Default: Story = {
  render: () => {
    const [open, setOpen] = React.useState(false);
    return <CommandPalette open={open} onOpenChange={setOpen} />;
  },
};

export const WithTrigger: Story = {
  render: () => <CommandTrigger />,
};

export const Mobile: Story = {
  render: () => <CommandTrigger />,
  parameters: {
    viewport: {
      defaultViewport: 'iphone12',
    },
  },
};
