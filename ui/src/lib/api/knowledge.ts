import type { BusinessGlossary, Instruction } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const glossaryApi = {
  async list(dbConnectionId: string): Promise<BusinessGlossary[]> {
    const response = await fetch(
      `${API_BASE}/api/v1/business_glossaries?db_connection_id=${encodeURIComponent(dbConnectionId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch glossary: ${response.statusText}`);
    }

    const data = await response.json();
    return data || [];
  },

  async create(
    dbConnectionId: string,
    data: { term: string; definition: string; synonyms?: string[]; related_tables?: string[] }
  ): Promise<BusinessGlossary> {
    const response = await fetch(
      `${API_BASE}/api/v1/business_glossaries?db_connection_id=${encodeURIComponent(dbConnectionId)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to create glossary term: ${response.statusText}`);
    }

    return response.json();
  },

  async update(
    id: string,
    data: { term?: string; definition?: string; synonyms?: string[]; related_tables?: string[] }
  ): Promise<BusinessGlossary> {
    const response = await fetch(`${API_BASE}/api/v1/business_glossaries/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to update glossary term: ${response.statusText}`);
    }

    return response.json();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/business_glossaries/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete glossary term: ${response.statusText}`);
    }
  },
};

export const instructionsApi = {
  async list(dbConnectionId: string): Promise<Instruction[]> {
    const response = await fetch(
      `${API_BASE}/api/v1/instructions?db_connection_id=${encodeURIComponent(dbConnectionId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch instructions: ${response.statusText}`);
    }

    const data = await response.json();
    return data || [];
  },

  async create(data: {
    db_connection_id: string;
    content: string;
    metadata?: Record<string, unknown>;
  }): Promise<Instruction> {
    const response = await fetch(`${API_BASE}/api/v1/instructions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create instruction: ${response.statusText}`);
    }

    return response.json();
  },

  async update(
    id: string,
    data: { content?: string; metadata?: Record<string, unknown> }
  ): Promise<Instruction> {
    const response = await fetch(`${API_BASE}/api/v1/instructions/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to update instruction: ${response.statusText}`);
    }

    return response.json();
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/instructions/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete instruction: ${response.statusText}`);
    }
  },
};
