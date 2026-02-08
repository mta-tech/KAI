import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs';
import { Card } from './card';

const meta = {
  title: 'UI/Tabs',
  component: Tabs,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Tabs>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="account">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="account">Account</TabsTrigger>
        <TabsTrigger value="password">Password</TabsTrigger>
      </TabsList>
      <TabsContent value="account">
        <Card className="p-4">
          <p className="text-sm">Make changes to your account here.</p>
        </Card>
      </TabsContent>
      <TabsContent value="password">
        <Card className="p-4">
          <p className="text-sm">Change your password here.</p>
        </Card>
      </TabsContent>
    </Tabs>
  ),
};

export const ThreeTabs: Story = {
  render: () => (
    <Tabs defaultValue="tab1">
      <TabsList>
        <TabsTrigger value="tab1">Overview</TabsTrigger>
        <TabsTrigger value="tab2">Settings</TabsTrigger>
        <TabsTrigger value="tab3">Advanced</TabsTrigger>
      </TabsList>
      <TabsContent value="tab1" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Overview content</p>
        </Card>
      </TabsContent>
      <TabsContent value="tab2" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Settings content</p>
        </Card>
      </TabsContent>
      <TabsContent value="tab3" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Advanced options</p>
        </Card>
      </TabsContent>
    </Tabs>
  ),
};

export const Vertical: Story = {
  render: () => (
    <div className="flex gap-4">
      <Tabs defaultValue="tab1" orientation="vertical">
        <TabsList className="grid w-full h-fit gap-2">
          <TabsTrigger value="tab1" className="w-full justify-start">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2" className="w-full justify-start">Tab 2</TabsTrigger>
          <TabsTrigger value="tab3" className="w-full justify-start">Tab 3</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1" className="mt-0">
          <Card className="p-4 w-[200px]">
            <p className="text-sm">Content 1</p>
          </Card>
        </TabsContent>
        <TabsContent value="tab2" className="mt-0">
          <Card className="p-4 w-[200px]">
            <p className="text-sm">Content 2</p>
          </Card>
        </TabsContent>
        <TabsContent value="tab3" className="mt-0">
          <Card className="p-4 w-[200px]">
            <p className="text-sm">Content 3</p>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  ),
};

export const WithIcons: Story = {
  render: () => (
    <Tabs defaultValue="preview">
      <TabsList>
        <TabsTrigger value="preview">👁️ Preview</TabsTrigger>
        <TabsTrigger value="code">💻 Code</TabsTrigger>
        <TabsTrigger value="docs">📚 Docs</TabsTrigger>
      </TabsList>
      <TabsContent value="preview" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Preview content</p>
        </Card>
      </TabsContent>
      <TabsContent value="code" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Code content</p>
        </Card>
      </TabsContent>
      <TabsContent value="docs" className="mt-2">
        <Card className="p-4">
          <p className="text-sm">Documentation content</p>
        </Card>
      </TabsContent>
    </Tabs>
  ),
};
