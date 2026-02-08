import type { Meta, StoryObj } from '@storybook/react';
import { SqlResultsTable } from './sql-results-table';

const mockResults = {
  columns: ['id', 'name', 'email', 'status', 'created_at', 'amount'],
  rows: [
    { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', created_at: '2024-01-15', amount: 1500.00 },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'pending', created_at: '2024-01-16', amount: 2300.50 },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'active', created_at: '2024-01-17', amount: 950.25 },
    { id: 4, name: 'Alice Williams', email: 'alice@example.com', status: 'inactive', created_at: '2024-01-18', amount: 3200.00 },
    { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', status: 'active', created_at: '2024-01-19', amount: 1750.75 },
    { id: 6, name: 'Diana Prince', email: 'diana@example.com', status: 'pending', created_at: '2024-01-20', amount: 2800.00 },
    { id: 7, name: 'Eve Davis', email: 'eve@example.com', status: 'active', created_at: '2024-01-21', amount: 1950.50 },
    { id: 8, name: 'Frank Miller', email: 'frank@example.com', status: 'inactive', created_at: '2024-01-22', amount: 1100.25 },
  ],
  rowCount: 8,
  executionTime: 245,
};

const largeResults = {
  columns: ['id', 'product_name', 'category', 'price', 'stock', 'rating'],
  rows: Array.from({ length: 100 }, (_, i) => ({
    id: i + 1,
    product_name: `Product ${i + 1}`,
    category: ['Electronics', 'Clothing', 'Food', 'Books'][i % 4],
    price: Math.round((Math.random() * 500 + 10) * 100) / 100,
    stock: Math.floor(Math.random() * 200),
    rating: Math.round((Math.random() * 2 + 3) * 10) / 10,
  })),
  rowCount: 100,
  executionTime: 1250,
};

const emptyResults = {
  columns: ['id', 'name'],
  rows: [],
  rowCount: 0,
  executionTime: 50,
};

const meta: Meta<typeof SqlResultsTable> = {
  title: 'Chat/SqlResultsTable',
  component: SqlResultsTable,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    results: {
      control: 'object',
      description: 'Query results to display',
    },
    isLoading: {
      control: 'boolean',
      description: 'Show loading state',
    },
    error: {
      control: 'text',
      description: 'Error message to display',
    },
  },
};

export default meta;
type Story = StoryObj<typeof SqlResultsTable>;

export const Default: Story = {
  args: {
    results: mockResults,
  },
};

export const LargeDataset: Story = {
  args: {
    results: largeResults,
  },
};

export const EmptyResults: Story = {
  args: {
    results: emptyResults,
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
  },
};

export const Error: Story = {
  args: {
    error: 'Syntax error near "SELECT" at line 1',
  },
};

export const NoData: Story = {
  args: {
    results: undefined,
  },
};
