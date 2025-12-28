import { create } from 'zustand';
import type { AgentEvent, AgentTodo } from '@/lib/api/types';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  events?: AgentEvent[];
  todos?: AgentTodo[];
  isStreaming?: boolean;
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
    set((state) => ({
      messages: [
        ...state.messages,
        { id, role: 'assistant', content: '', timestamp: new Date(), events: [], isStreaming: true },
      ],
      isStreaming: true,
    }));
  },

  appendToAssistantMessage: (id, content) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + content } : m
      ),
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
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, isStreaming: false, todos: state.currentTodos } : m
      ),
      isStreaming: false,
    }));
  },

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  clearMessages: () => set({ messages: [], currentTodos: [] }),
}));
