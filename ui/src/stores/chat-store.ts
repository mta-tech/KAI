import { create } from 'zustand';
import type { AgentEvent, AgentTodo, ChunkType } from '@/lib/api/types';

// Structured content from SSE events
export interface StructuredContent {
  sql?: string;
  summary?: string;
  insights?: string;
  chartRecommendations?: string;
  reasoning?: string;
  processStatus?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  events?: AgentEvent[];
  todos?: AgentTodo[];
  isStreaming?: boolean;
  // Structured content from SSE chunks
  structured?: StructuredContent;
}

interface ChatState {
  sessionId: string | null;
  connectionId: string | null;
  messages: ChatMessage[];
  currentTodos: AgentTodo[];
  isStreaming: boolean;

  setSession: (sessionId: string, connectionId: string) => void;
  addUserMessage: (content: string) => string;
  startAssistantMessage: (id: string) => void;
  appendToAssistantMessage: (id: string, content: string) => void;
  appendStructuredContent: (id: string, chunkType: ChunkType, content: string) => void;
  updateProcessStatus: (id: string, status: string) => void;
  updateTodos: (todos: AgentTodo[]) => void;
  addEvent: (messageId: string, event: AgentEvent) => void;
  finishAssistantMessage: (id: string) => void;
  setStreaming: (streaming: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: null,
  connectionId: null,
  messages: [],
  currentTodos: [],
  isStreaming: false,

  setSession: (sessionId, connectionId) => set({ sessionId, connectionId, messages: [] }),

  addUserMessage: (content) => {
    const id = `user-${Date.now()}`;
    set((state) => ({
      messages: [
        ...state.messages,
        { id, role: 'user', content, timestamp: new Date() },
      ],
    }));
    return id;
  },

  startAssistantMessage: (id) => {
    console.log('[Chat Store] startAssistantMessage called:', { id });
    set((state) => {
      const newMessage = { id, role: 'assistant' as const, content: '', timestamp: new Date(), events: [], isStreaming: true };
      console.log('[Chat Store] Creating new message:', newMessage);
      return {
        messages: [...state.messages, newMessage],
        isStreaming: true,
      };
    });
  },

  appendToAssistantMessage: (id, content) => {
    console.log('[Chat Store] appendToAssistantMessage called:', { id, content, contentLength: content.length });
    set((state) => {
      const message = state.messages.find((m) => m.id === id);
      console.log('[Chat Store] Current message:', {
        messageId: message?.id,
        currentContentLength: message?.content.length,
        isStreaming: message?.isStreaming
      });

      const updatedMessages = state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + content } : m
      );

      const updatedMessage = updatedMessages.find((m) => m.id === id);
      console.log('[Chat Store] Updated message:', {
        messageId: updatedMessage?.id,
        newContentLength: updatedMessage?.content.length
      });

      return { messages: updatedMessages };
    });
  },

  appendStructuredContent: (id, chunkType, content) => {
    console.log('[Chat Store] appendStructuredContent called:', { id, chunkType, contentLength: content.length });
    set((state) => ({
      messages: state.messages.map((m) => {
        if (m.id !== id) return m;

        const structured = m.structured || {};

        // Map chunk_type to structured content field
        switch (chunkType) {
          case 'sql':
            return { ...m, structured: { ...structured, sql: (structured.sql || '') + content } };
          case 'summary':
            return { ...m, structured: { ...structured, summary: (structured.summary || '') + content } };
          case 'insights':
            return { ...m, structured: { ...structured, insights: (structured.insights || '') + content } };
          case 'chart_recommendations':
            return { ...m, structured: { ...structured, chartRecommendations: (structured.chartRecommendations || '') + content } };
          case 'reasoning':
            return { ...m, structured: { ...structured, reasoning: (structured.reasoning || '') + content } };
          case 'text':
          default:
            // For text, append to main content
            return { ...m, content: m.content + content };
        }
      })
    }));
  },

  updateProcessStatus: (id, status) => {
    console.log('[Chat Store] updateProcessStatus called:', { id, status });
    set((state) => ({
      messages: state.messages.map((m) => {
        if (m.id !== id) return m;
        const structured = m.structured || {};
        return { ...m, structured: { ...structured, processStatus: status } };
      })
    }));
  },

  updateTodos: (todos) => set({ currentTodos: todos }),

  addEvent: (messageId, event) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === messageId ? { ...m, events: [...(m.events || []), event] } : m
      ),
    }));
  },

  finishAssistantMessage: (id) => {
    console.log('[Chat Store] finishAssistantMessage called:', { id });
    set((state) => {
      console.log('[Chat Store] Setting isStreaming to false, current state:', { isStreaming: state.isStreaming });
      return {
        messages: state.messages.map((m) =>
          m.id === id ? { ...m, isStreaming: false, todos: state.currentTodos } : m
        ),
        isStreaming: false,
      };
    });
  },

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  clearMessages: () => set({ messages: [], currentTodos: [] }),
}));
