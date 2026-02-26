import type { MDLManifest } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const mdlApi = {
  async list(dbConnectionId?: string): Promise<MDLManifest[]> {
    const url = dbConnectionId
      ? `${API_BASE}/api/v1/mdl/manifests?db_connection_id=${encodeURIComponent(dbConnectionId)}`
      : `${API_BASE}/api/v1/mdl/manifests`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch MDL manifests: ${response.statusText}`);
    }

    const data = await response.json();
    return data || [];
  },

  async get(id: string): Promise<MDLManifest> {
    const response = await fetch(`${API_BASE}/api/v1/mdl/manifests/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch MDL manifest: ${response.statusText}`);
    }

    return response.json();
  },

  async buildFromDatabase(request: {
    db_connection_id: string;
    name: string;
    catalog: string;
    schema: string;
    infer_relationships?: boolean;
  }): Promise<{ manifest_id: string }> {
    const response = await fetch(`${API_BASE}/api/v1/mdl/manifests/build`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to build MDL manifest: ${response.statusText}`);
    }

    return response.json();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/mdl/manifests/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete MDL manifest: ${response.statusText}`);
    }
  },

  async export(id: string): Promise<MDLManifest> {
    const response = await fetch(`${API_BASE}/api/v1/mdl/manifests/${id}/export`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to export MDL manifest: ${response.statusText}`);
    }

    return response.json();
  },
};
