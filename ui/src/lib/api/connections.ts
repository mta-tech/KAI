import type { Connection, CreateConnectionRequest } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const connectionsApi = {
  async list(): Promise<Connection[]> {
    const response = await fetch(`${API_BASE}/api/v1/database-connections`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch connections: ${response.statusText}`);
    }

    const data = await response.json();
    return data || [];
  },

  async get(id: string): Promise<Connection> {
    const response = await fetch(`${API_BASE}/api/v1/database-connections/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch connection: ${response.statusText}`);
    }

    return response.json();
  },

  async create(data: CreateConnectionRequest): Promise<Connection> {
    const response = await fetch(`${API_BASE}/api/v1/database-connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create connection: ${response.statusText}`);
    }

    return response.json();
  },

  async update(id: string, data: CreateConnectionRequest): Promise<Connection> {
    const response = await fetch(`${API_BASE}/api/v1/database-connections/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to update connection: ${response.statusText}`);
    }

    return response.json();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/database-connections/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete connection: ${response.statusText}`);
    }
  },
};
