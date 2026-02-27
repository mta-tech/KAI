import type { Meta, StoryObj } from '@storybook/react';
import * as React from 'react';
import { ErrorDisplay } from './error-display';

const meta = {
  title: 'Components/ErrorDisplay',
  component: ErrorDisplay,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof ErrorDisplay>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NetworkError: Story = {
  args: {
    error: new Error('Failed to fetch'),
    onRetry: () => console.log('Retry clicked'),
  },
  render: ({ error, onRetry }) => (
    <div className="w-[400px]">
      <ErrorDisplay
        error={error}
        onRetry={onRetry}
      />
    </div>
  ),
};

export const ServerError: Story = {
  args: {
    error: new Error('500 Internal Server Error'),
    title: 'Server Error',
    description: 'Something went wrong on our end. Please try again.',
    onRetry: () => console.log('Retry clicked'),
  },
  render: ({ error, title, description, onRetry }) => (
    <div className="w-[400px]">
      <ErrorDisplay
        error={error}
        title={title}
        description={description}
        onRetry={onRetry}
      />
    </div>
  ),
};

export const ValidationError: Story = {
  args: {
    error: new Error('422 Validation Error: Invalid input data'),
    onRetry: () => console.log('Retry clicked'),
  },
  render: ({ error, onRetry }) => (
    <div className="w-[400px]">
      <ErrorDisplay
        error={error}
        onRetry={onRetry}
      />
    </div>
  ),
};

export const WithoutRetry: Story = {
  args: {
    error: new Error('404 Not Found'),
    showRetry: false,
  },
  render: ({ error, showRetry }) => (
    <div className="w-[400px]">
      <ErrorDisplay
        error={error}
        showRetry={showRetry}
      />
    </div>
  ),
};

export const WithRetryLoading: Story = {
  args: {
    error: new Error('503 Service Unavailable'),
    isRetrying: true,
  },
  render: ({ error, isRetrying }) => (
    <div className="w-[400px]">
      <ErrorDisplay
        error={error}
        onRetry={() => console.log('Retrying...')}
        isRetrying={isRetrying}
      />
    </div>
  ),
};

export const InForm: Story = {
  args: {
    error: new Error('Failed to submit form'),
  },
  render: ({ error }) => {
    const [hasError, setHasError] = React.useState(true);

    if (!hasError) {
      return (
        <div className="w-[400px] p-4 border rounded-lg bg-card">
          <p className="text-sm text-muted-foreground">Form submitted successfully!</p>
        </div>
      );
    }

    return (
      <div className="w-[400px] space-y-4 p-4 border rounded-lg bg-card">
        <div className="space-y-2">
          <label htmlFor="name" className="text-sm font-medium">Name</label>
          <input id="name" className="flex h-9 w-full rounded-md border border-input bg-transparent px-3" placeholder="Enter name" />
        </div>
        <ErrorDisplay
          error={error}
          onRetry={() => setHasError(false)}
        />
      </div>
    );
  },
};
