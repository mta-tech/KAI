import type { Meta, StoryObj } from '@storybook/react';
import { BulkTableOperations } from './bulk-table-operations';
import type { TableDescription } from '@/lib/api/types';

const mockTables: TableDescription[] = [
  {
    id: 'table-1',
    table_name: 'users',
    db_schema: 'public',
    db_connection_id: 'conn-1',
    sync_status: 'SCANNED',
    description: 'User accounts and profiles',
    columns: [
      { name: 'id', data_type: 'uuid', is_nullable: false, description: 'Primary key' },
      { name: 'email', data_type: 'varchar', is_nullable: false, description: 'User email' },
      { name: 'created_at', data_type: 'timestamp', is_nullable: false, description: 'Creation time' },
    ],
  },
  {
    id: 'table-2',
    table_name: 'orders',
    db_schema: 'public',
    db_connection_id: 'conn-1',
    sync_status: 'SCANNED',
    description: 'Customer orders',
    columns: [
      { name: 'id', data_type: 'uuid', is_nullable: false, description: 'Primary key' },
      { name: 'user_id', data_type: 'uuid', is_nullable: false, description: 'Foreign key to users' },
      { name: 'total', data_type: 'decimal', is_nullable: false, description: 'Order total' },
    ],
  },
  {
    id: 'table-3',
    table_name: 'products',
    db_schema: 'public',
    db_connection_id: 'conn-1',
    sync_status: 'NOT_SCANNED',
    columns: [
      { name: 'id', data_type: 'uuid', is_nullable: false },
      { name: 'name', data_type: 'varchar', is_nullable: false },
      { name: 'price', data_type: 'decimal', is_nullable: false },
    ],
  },
  {
    id: 'table-4',
    table_name: 'analytics_events',
    db_schema: 'analytics',
    db_connection_id: 'conn-1',
    sync_status: 'SCANNED',
    description: 'Event tracking data',
    columns: [
      { name: 'id', data_type: 'uuid', is_nullable: false },
      { name: 'event_type', data_type: 'varchar', is_nullable: false },
      { name: 'timestamp', data_type: 'timestamp', is_nullable: false },
    ],
  },
];

const meta: Meta<typeof BulkTableOperations> = {
  title: 'Schema/BulkTableOperations',
  component: BulkTableOperations,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    tables: {
      control: 'object',
      description: 'Array of tables to display and operate on',
    },
    connectionId: {
      control: 'text',
      description: 'Database connection ID',
    },
    connectionAlias: {
      control: 'text',
      description: 'Database connection alias',
    },
    onTablesChange: {
      action: 'onTablesChange',
      description: 'Callback when tables are modified',
    },
  },
};

export default meta;
type Story = StoryObj<typeof BulkTableOperations>;

export const Default: Story = {
  args: {
    tables: mockTables,
    connectionId: 'conn-1',
    connectionAlias: 'Test Database',
  },
};

export const EmptyState: Story = {
  args: {
    tables: [],
    connectionId: 'conn-1',
    connectionAlias: 'Test Database',
  },
};

export const ManyTables: Story = {
  args: {
    tables: Array.from({ length: 20 }, (_, i) => ({
      id: `table-${i}`,
      table_name: `table_${i}`,
      db_schema: i % 3 === 0 ? 'analytics' : 'public',
      db_connection_id: 'conn-1',
      sync_status: i % 2 === 0 ? 'SCANNED' : 'NOT_SCANNED',
      description: i % 2 === 0 ? `Description for table ${i}` : undefined,
      columns: [
        { name: 'id', data_type: 'uuid', is_nullable: false },
        { name: 'name', data_type: 'varchar', is_nullable: false },
      ],
    })),
    connectionId: 'conn-1',
    connectionAlias: 'Test Database',
  },
};

export const AllScanned: Story = {
  args: {
    tables: mockTables.map(t => ({ ...t, sync_status: 'SCANNED' as const })),
    connectionId: 'conn-1',
    connectionAlias: 'Test Database',
  },
};

export const NoneScanned: Story = {
  args: {
    tables: mockTables.map(t => ({ ...t, sync_status: 'NOT_SCANNED' as const, description: undefined })),
    connectionId: 'conn-1',
    connectionAlias: 'Test Database',
  },
};