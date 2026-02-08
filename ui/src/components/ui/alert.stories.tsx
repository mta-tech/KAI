import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { Alert, AlertDescription, AlertTitle } from './alert';
import { Button } from './button';

const meta = {
  title: 'UI/Alert',
  component: Alert,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive'],
    },
  },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Alert>
      <AlertTitle>Information</AlertTitle>
      <AlertDescription>
        This is an informational alert message for the user.
      </AlertDescription>
    </Alert>
  ),
};

export const Destructive: Story = {
  render: () => (
    <Alert variant="destructive">
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>
        Something went wrong. Please try again later.
      </AlertDescription>
    </Alert>
  ),
};

export const WithIcon: Story = {
  render: () => (
    <Alert>
      <AlertTitle>ℹ️ Information</AlertTitle>
      <AlertDescription>
        Your session will expire in 5 minutes. Please save your work.
      </AlertDescription>
    </Alert>
  ),
};

export const Simple: Story = {
  render: () => (
    <Alert>
      <AlertDescription>
        Your payment has been processed successfully.
      </AlertDescription>
    </Alert>
  ),
};

export const Warning: Story = {
  render: () => (
    <Alert variant="destructive">
      <AlertTitle>⚠️ Warning</AlertTitle>
      <AlertDescription>
        You have unsaved changes that will be lost if you leave this page.
      </AlertDescription>
    </Alert>
  ),
};

export const WithAction: Story = {
  render: () => (
    <Alert>
      <AlertTitle>New Update Available</AlertTitle>
      <AlertDescription className="mb-4">
        A new version of the application is available with bug fixes and improvements.
      </AlertDescription>
      <Button size="sm">Update Now</Button>
    </Alert>
  ),
};

export const MultipleAlerts: Story = {
  render: () => (
    <div className="space-y-4">
      <Alert>
        <AlertTitle>Success</AlertTitle>
        <AlertDescription>
          Your changes have been saved successfully.
        </AlertDescription>
      </Alert>
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to connect to the server. Please check your internet connection.
        </AlertDescription>
      </Alert>
    </div>
  ),
};
