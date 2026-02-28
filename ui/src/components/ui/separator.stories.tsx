import type { Meta, StoryObj } from '@storybook/react';
import { Separator } from './separator';
import { Button } from './button';

const meta = {
  title: 'UI/Separator',
  component: Separator,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    orientation: {
      control: 'select',
      options: ['horizontal', 'vertical'],
    },
  },
} satisfies Meta<typeof Separator>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Horizontal: Story = {
  render: () => (
    <div className="w-[400px]">
      <div className="text-sm">
        <h4 className="font-medium mb-2">Section 1</h4>
        <p className="text-muted-foreground">Content for section 1</p>
      </div>
      <Separator className="my-4" />
      <div className="text-sm">
        <h4 className="font-medium mb-2">Section 2</h4>
        <p className="text-muted-foreground">Content for section 2</p>
      </div>
    </div>
  ),
};

export const Vertical: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button variant="outline">Cancel</Button>
      <Separator orientation="vertical" className="h-8" />
      <Button>Submit</Button>
    </div>
  ),
};

export const BetweenButtons: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Button variant="ghost" size="sm">Prev</Button>
      <Separator orientation="vertical" className="h-6" />
      <Button variant="ghost" size="sm">Next</Button>
    </div>
  ),
};

export const WithText: Story = {
  render: () => (
    <div className="w-[400px] space-y-4">
      <div>
        <h4 className="font-medium">Step 1</h4>
        <p className="text-sm text-muted-foreground">Complete your profile</p>
      </div>
      <Separator />
      <div>
        <h4 className="font-medium">Step 2</h4>
        <p className="text-sm text-muted-foreground">Connect your accounts</p>
      </div>
      <Separator />
      <div>
        <h4 className="font-medium">Step 3</h4>
        <p className="text-sm text-muted-foreground">Start exploring</p>
      </div>
    </div>
  ),
};

export const MultipleVertical: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <div className="text-sm">Item 1</div>
      <Separator orientation="vertical" className="h-6" />
      <div className="text-sm">Item 2</div>
      <Separator orientation="vertical" className="h-6" />
      <div className="text-sm">Item 3</div>
      <Separator orientation="vertical" className="h-6" />
      <div className="text-sm">Item 4</div>
    </div>
  ),
};
