import type { TableDescription } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const tablesApi = {
  async list(dbConnectionId: string): Promise<TableDescription[]> {
    const response = await fetch(
      `${API_BASE}/api/v1/table-descriptions?db_connection_id=${encodeURIComponent(dbConnectionId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch tables: ${response.statusText}`);
    }

    const data = await response.json();
    return data || [];
  },

  async get(id: string): Promise<TableDescription> {
    const response = await fetch(`${API_BASE}/api/v1/table-descriptions/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch table: ${response.statusText}`);
    }

    return response.json();
  },

  async scan(tableIds: string[], withAI: boolean = false, instruction?: string): Promise<TableDescription[]> {
    const response = await fetch(`${API_BASE}/api/v1/table-descriptions/sync-schemas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        table_description_ids: tableIds,
        instruction: withAI ? (instruction || 'Generate detailed descriptions for tables and columns') : null,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `Failed to scan tables: ${response.statusText}`);
    }

    return response.json();
  },
};
