import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from './popover';
import { Button } from './button';

const meta = {
  title: 'UI/Popover',
  component: PopoverContent,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof PopoverContent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline">Open Popover</Button>
      </PopoverTrigger>
      <PopoverContent>
        <div className="space-y-2">
          <h4 className="font-medium leading-none">Dimensions</h4>
          <p className="text-sm text-muted-foreground">
            Set the dimensions for the layer.
          </p>
        </div>
      </PopoverContent>
    </Popover>
  ),
};

export const WithForm: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button>Insert Data</Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-medium leading-none">Add New Item</h4>
            <p className="text-sm text-muted-foreground">
              Enter the details for the new item.
            </p>
          </div>
          <div className="grid gap-2">
            <div className="grid gap-1">
              <label htmlFor="name" className="text-sm">Name</label>
              <input id="name" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3" placeholder="Item name" />
            </div>
            <div className="grid gap-1">
              <label htmlFor="value" className="text-sm">Value</label>
              <input id="value" type="number" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3" placeholder="0" />
            </div>
          </div>
          <div className="flex justify-end">
            <Button size="sm">Add</Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  ),
};

export const SideAlignments: Story = {
  render: () => (
    <div className="flex gap-4">
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline">Top</Button>
        </PopoverTrigger>
        <PopoverContent side="top">
          <p className="text-sm">Popover from the top</p>
        </PopoverContent>
      </Popover>

      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline">Right</Button>
        </PopoverTrigger>
        <PopoverContent side="right">
          <p className="text-sm">Popover from the right</p>
        </PopoverContent>
      </Popover>

      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline">Bottom</Button>
        </PopoverTrigger>
        <PopoverContent side="bottom">
          <p className="text-sm">Popover from the bottom</p>
        </PopoverContent>
      </Popover>

      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline">Left</Button>
        </PopoverTrigger>
        <PopoverContent side="left">
          <p className="text-sm">Popover from the left</p>
        </PopoverContent>
      </Popover>
    </div>
  ),
};

export const WithRichContent: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="secondary">@mention</Button>
      </PopoverTrigger>
      <PopoverContent className="w-72">
        <div className="space-y-3">
          <div>
            <h4 className="font-medium">Team Members</h4>
            <p className="text-xs text-muted-foreground">
              Select a team member to mention
            </p>
          </div>
          <div className="space-y-2">
            {['Alice Johnson', 'Bob Smith', 'Carol Williams', 'David Brown'].map((name) => (
              <div key={name} className="flex items-center gap-2 p-2 rounded hover:bg-accent cursor-pointer">
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-medium">
                  {name.charAt(0)}
                </div>
                <span className="text-sm">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  ),
};
