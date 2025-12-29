import type {
  AgentSession,
  CreateSessionRequest,
  SendMessageRequest,
  SessionsListResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug logging for test environment
if (typeof window !== 'undefined') {
  console.log('[Agent API] Environment:', {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    API_BASE,
    windowLocation: window.location.href,
  });
}

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

  streamTask(
    sessionId: string,
    query: string,
    onEvent: (event: import('./types').AgentEvent) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): () => void {
    const controller = new AbortController();
    const streamUrl = `${API_BASE}/api/v1/sessions/${sessionId}/query/stream`;

    console.log('[Agent API] Starting stream:', {
      url: streamUrl,
      sessionId,
      query,
    });

    fetch(streamUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
      signal: controller.signal,
    })
      .then(async (response) => {
        console.log('[Agent API] Stream response received:', {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
        });

        if (!response.ok) {
          throw new Error(`Failed to stream task: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              onComplete();
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.trim()) {
                try {
                  const event = JSON.parse(line);
                  console.log('[Agent API] Event received:', event);
                  onEvent(event);
                } catch (e) {
                  console.warn('[Agent API] Failed to parse event:', line, e);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          console.error('[Agent API] Stream error:', error);
          onError(error);
        }
      });

    return () => controller.abort();
  },
};
