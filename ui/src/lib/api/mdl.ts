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
};
