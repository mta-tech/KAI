import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from './tooltip';
import { Button } from './button';

const meta = {
  title: 'UI/Tooltip',
  component: TooltipContent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <TooltipProvider>
        <Story />
      </TooltipProvider>
    ),
  ],
} satisfies Meta<typeof TooltipContent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button variant="outline">Hover me</Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>This is a tooltip</p>
      </TooltipContent>
    </Tooltip>
  ),
};

export const SideAlignments: Story = {
  render: () => (
    <div className="flex gap-4">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline">Top</Button>
        </TooltipTrigger>
        <TooltipContent side="top">
          <p>Tooltip from top</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline">Right</Button>
        </TooltipTrigger>
        <TooltipContent side="right">
          <p>Tooltip from right</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline">Bottom</Button>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          <p>Tooltip from bottom</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline">Left</Button>
        </TooltipTrigger>
        <TooltipContent side="left">
          <p>Tooltip from left</p>
        </TooltipContent>
      </Tooltip>
    </div>
  ),
};

export const WithIcon: Story = {
  render: () => (
    <div className="flex gap-4">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon">ℹ️</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Information tooltip</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon">⚠️</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Warning message</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="ghost" size="icon">🔒</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>This field is locked</p>
        </TooltipContent>
      </Tooltip>
    </div>
  ),
};

export const OnText: Story = {
  render: () => (
    <p className="text-sm">
      This is a sentence with a{' '}
      <Tooltip>
        <TooltipTrigger className="underline decoration-dotted cursor-help">
          tooltip
        </TooltipTrigger>
        <TooltipContent>
          <p>Additional information about this word</p>
        </TooltipContent>
      </Tooltip>
      {' '}embedded in the text.
    </p>
  ),
};

export const LongContent: Story = {
  render: () => (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button>Hover for details</Button>
      </TooltipTrigger>
      <TooltipContent className="max-w-xs">
        <p>This is a longer tooltip with more detailed information that spans multiple lines.</p>
      </TooltipContent>
    </Tooltip>
  ),
};

export const WithDelay: Story = {
  render: () => (
    <div className="flex gap-4">
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <Button variant="outline">Instant</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Appears immediately</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip delayDuration={500}>
        <TooltipTrigger asChild>
          <Button variant="outline">Delayed</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Appears after 500ms</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip delayDuration={1000}>
        <TooltipTrigger asChild>
          <Button variant="outline">Slow</Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Appears after 1 second</p>
        </TooltipContent>
      </Tooltip>
    </div>
  ),
};
