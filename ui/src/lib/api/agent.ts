import type {
  AgentSession,
  CreateSessionRequest,
  SendMessageRequest,
  AgentResponse,
  SessionsListResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const agentApi = {
  async createSession(
    request: CreateSessionRequest
  ): Promise<{ session_id: string }> {
    const response = await fetch(`${API_BASE}/api/v1/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return response.json();
  },

  async listSessions(dbConnectionId?: string): Promise<SessionsListResponse> {
    const url = dbConnectionId
      ? `${API_BASE}/api/v1/sessions?db_connection_id=${encodeURIComponent(dbConnectionId)}`
      : `${API_BASE}/api/v1/sessions`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.statusText}`);
    }

    return response.json();
  },

  async getSession(sessionId: string): Promise<AgentSession> {
    const response = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch session: ${response.statusText}`);
    }

    return response.json();
  },

  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/api/v1/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to delete session: ${response.statusText}`);
    }
  },

  async sendMessageStream(
    request: SendMessageRequest,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const response = await fetch(
      `${API_BASE}/api/v1/sessions/${request.session_id}/query/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: request.query }),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } finally {
      reader.releaseLock();
    }
  },
};
