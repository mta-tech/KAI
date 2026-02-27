import type { Meta, StoryObj } from '@storybook/react';
import { Textarea } from './textarea';
import { Label } from './label';

const meta = {
  title: 'UI/Textarea',
  component: Textarea,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Textarea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: 'Type your message here...',
    rows: 4,
  },
};

export const WithValue: Story = {
  render: () => (
    <Textarea
      defaultValue="This is a textarea with some default content that the user can edit."
      rows={4}
    />
  ),
};

export const WithLabel: Story = {
  render: () => (
    <div className="grid w-full max-w-sm items-center gap-1.5">
      <Label htmlFor="message">Message</Label>
      <Textarea id="message" placeholder="Type your message here..." />
    </div>
  ),
};

export const Disabled: Story = {
  args: {
    placeholder: 'Disabled textarea',
    disabled: true,
    rows: 3,
  },
};

export const Large: Story = {
  render: () => (
    <Textarea
      placeholder="Enter your long-form content here..."
      rows={8}
      className="w-[500px]"
    />
  ),
};

export const FormExample: Story = {
  render: () => (
    <div className="space-y-4 w-[400px]">
      <div className="space-y-2">
        <Label htmlFor="subject">Subject</Label>
        <input id="subject" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3" placeholder="Email subject" />
      </div>
      <div className="space-y-2">
        <Label htmlFor="body">Message</Label>
        <Textarea id="body" placeholder="Type your message..." rows={6} />
      </div>
    </div>
  ),
};

export const WithCharacterCount: Story = {
  render: () => (
    <div className="w-[400px]">
      <Label htmlFor="bio">Bio</Label>
      <Textarea
        id="bio"
        placeholder="Tell us about yourself..."
        rows={4}
        maxLength={200}
      />
      <p className="text-xs text-muted-foreground mt-1">0/200 characters</p>
    </div>
  ),
};
