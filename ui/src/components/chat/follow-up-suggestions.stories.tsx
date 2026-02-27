import type { Meta, StoryObj } from '@storybook/react';
import { FollowUpSuggestions } from './follow-up-suggestions';

const meta: Meta<typeof FollowUpSuggestions> = {
  title: 'Chat/FollowUpSuggestions',
  component: FollowUpSuggestions,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    suggestions: {
      control: 'object',
      description: 'List of follow-up suggestion strings',
    },
    onSelect: {
      action: 'onSelect',
      description: 'Called when user clicks a suggestion',
    },
  },
  args: {
    onSelect: (suggestion: string) => console.log('Selected:', suggestion),
  },
};

export default meta;
type Story = StoryObj<typeof FollowUpSuggestions>;

export const Default: Story = {
  args: {
    suggestions: [
      'Show me the top 10 customers by revenue',
      'What is the month-over-month growth trend?',
      'Break down sales by region',
    ],
  },
};

export const SingleSuggestion: Story = {
  args: {
    suggestions: ['Show me more details about this data'],
  },
};

export const LongSuggestions: Story = {
  args: {
    suggestions: [
      'Can you provide a detailed breakdown of all transactions grouped by customer segment, product category, and geographic region for the last fiscal year?',
      'Show me which products have the highest return rate and what are the most common reasons customers are returning them?',
      'Compare this quarter performance against the same quarter last year and highlight any statistically significant anomalies',
    ],
  },
};

export const Empty: Story = {
  args: {
    suggestions: [],
  },
};

export const ManySuggestions: Story = {
  args: {
    suggestions: [
      'Show revenue trend',
      'Breakdown by category',
      'Compare with last year',
      'Filter by region',
      'Export data as CSV',
    ],
  },
};
