import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { ScrollArea } from './scroll-area';
import { Badge } from './badge';

const meta = {
  title: 'UI/ScrollArea',
  component: ScrollArea,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof ScrollArea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <ScrollArea className="h-[200px] w-[350px] rounded-md border">
      <div className="p-4">
        <p className="font-medium">Scrollable Content</p>
        <p className="text-sm text-muted-foreground mt-2">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt
          ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation.
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat.
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt.
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          More content here to demonstrate scrolling...
        </p>
      </div>
    </ScrollArea>
  ),
};

export const WithList: Story = {
  render: () => (
    <ScrollArea className="h-[300px] w-[350px] rounded-md border">
      <div className="p-4">
        <h4 className="mb-4 text-sm font-medium leading-none">Notifications</h4>
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="mb-4 text-sm">
            <div className="font-medium">Notification {i + 1}</div>
            <div className="text-muted-foreground">This is a sample notification message</div>
          </div>
        ))}
      </div>
    </ScrollArea>
  ),
};

export const WithTags: Story = {
  render: () => (
    <ScrollArea className="h-[200px] w-[350px] rounded-md border">
      <div className="p-4">
        <h4 className="mb-4 text-sm font-medium">Popular Tags</h4>
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 30 }).map((_, i) => (
            <Badge key={i} variant="secondary">tag{i + 1}</Badge>
          ))}
        </div>
      </div>
    </ScrollArea>
  ),
};

export const WithCode: Story = {
  render: () => (
    <ScrollArea className="h-[200px] w-[500px] rounded-md border">
      <div className="p-4">
        <pre className="text-xs">
          {`function example() {
  // This is a long code block
  // that requires scrolling
  // to see all the content
  
  const data = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' },
    { id: 3, name: 'Item 3' },
    { id: 4, name: 'Item 4' },
    { id: 5, name: 'Item 5' },
    { id: 6, name: 'Item 6' },
    { id: 7, name: 'Item 7' },
    { id: 8, name: 'Item 8' },
    { id: 9, name: 'Item 9' },
    { id: 10, name: 'Item 10' },
  ];
  
  return data.map(item => item.name);
}`}
        </pre>
      </div>
    </ScrollArea>
  ),
};

export const HorizontalScroll: Story = {
  render: () => (
    <ScrollArea className="h-[150px] w-[400px] rounded-md border">
      <div className="flex gap-4 p-4">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="flex-shrink-0 w-[200px] rounded-md border p-4">
            <div className="font-medium">Card {i + 1}</div>
            <div className="text-sm text-muted-foreground">Content {i + 1}</div>
          </div>
        ))}
      </div>
    </ScrollArea>
  ),
};
