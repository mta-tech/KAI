import type { Meta, StoryObj } from '@storybook/react';
import { KnowledgeEditor } from './knowledge-editor';
import type { BusinessGlossary, Instruction } from '@/lib/api/types';

const mockGlossaries: BusinessGlossary[] = [
  {
    id: 'gloss-1',
    db_connection_id: 'conn-1',
    term: 'Gross Revenue',
    definition: 'Total revenue before any deductions or discounts',
    synonyms: ['total revenue', 'gross sales', 'top-line revenue'],
    related_tables: ['orders', 'order_items'],
    metadata: { category: 'financial' },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'gloss-2',
    db_connection_id: 'conn-1',
    term: 'Active User',
    definition: 'A user who has logged in or performed an action within the last 30 days',
    synonyms: ['active customer', 'engaged user', 'returning user'],
    related_tables: ['users', 'sessions'],
    metadata: { category: 'user metrics' },
    created_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 'gloss-3',
    db_connection_id: 'conn-1',
    term: 'Conversion Rate',
    definition: 'The percentage of visitors who complete a desired action',
    synonyms: ['conversion', 'completion rate', 'success rate'],
    related_tables: ['analytics_events'],
    metadata: { category: 'analytics' },
    created_at: '2024-01-03T00:00:00Z',
  },
];

const mockInstructions: Instruction[] = [
  {
    id: 'inst-1',
    db_connection_id: 'conn-1',
    condition: 'When the user asks about sales data',
    rules: 'Always exclude cancelled orders from calculations. Use the order_status column to filter. Join with order_items for detailed product information.',
    is_default: false,
    metadata: { category: 'sales' },
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'inst-2',
    db_connection_id: 'conn-1',
    condition: 'When calculating user metrics',
    rules: 'Use the sessions table to determine active users. A user is considered active if they have a session in the last 30 days.',
    is_default: true,
    metadata: { category: 'default' },
    created_at: '2024-01-02T00:00:00Z',
  },
];

const meta: Meta<typeof KnowledgeEditor> = {
  title: 'Knowledge/KnowledgeEditor',
  component: KnowledgeEditor,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof KnowledgeEditor>;

export const Default: Story = {
  args: {
    connectionId: 'conn-1',
    glossaries: mockGlossaries,
    instructions: mockInstructions,
  },
};

export const EmptyState: Story = {
  args: {
    connectionId: 'conn-1',
    glossaries: [],
    instructions: [],
  },
};

export const OnlyGlossaries: Story = {
  args: {
    connectionId: 'conn-1',
    glossaries: mockGlossaries,
    instructions: [],
  },
};

export const OnlyInstructions: Story = {
  args: {
    connectionId: 'conn-1',
    glossaries: [],
    instructions: mockInstructions,
  },
};

export const ManyItems: Story = {
  args: {
    connectionId: 'conn-1',
    glossaries: Array.from({ length: 20 }, (_, i) => ({
      id: `gloss-${i}`,
      db_connection_id: 'conn-1',
      term: `Term ${i}`,
      definition: `Definition for term ${i}`,
      synonyms: [`synonym-${i}`],
      related_tables: [`table-${i % 5}`],
      metadata: { category: ['financial', 'user metrics', 'analytics'][i % 3] },
      created_at: new Date(Date.now() - i * 86400000).toISOString(),
    })),
    instructions: Array.from({ length: 10 }, (_, i) => ({
      id: `inst-${i}`,
      db_connection_id: 'conn-1',
      condition: `Condition ${i}`,
      rules: `Rules for condition ${i}`,
      is_default: i === 0,
      metadata: { category: ['sales', 'default', 'custom'][i % 3] },
      created_at: new Date(Date.now() - i * 86400000).toISOString(),
    })),
  },
};