import { useCallback, useRef } from 'react';
import { useChatStore } from '@/stores/chat-store';
import { agentApi } from '@/lib/api/agent';
import type { AgentEvent, ChunkType, MissionStreamEvent, StreamingEvent } from '@/lib/api/types';
import { isMissionStreamEvent } from '@/lib/api/types';

export function useChat() {
  const abortRef = useRef<(() => void) | null>(null);

  const {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    addUserMessage,
    startAssistantMessage,
    appendToAssistantMessage,
    appendStructuredContent,
    updateProcessStatus,
    updateTodos,
    addEvent,
    addMissionEvent,
    finishAssistantMessage,
    setStreaming,
    clearMessages,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      // Get current state directly from store to avoid stale closure
      const storeState = useChatStore.getState();
      const { isStreaming: currentlyStreaming, sessionId: currentSessionId } = storeState;

      if (!currentSessionId || currentlyStreaming) {
        return;
      }

      addUserMessage(content);
      const assistantId = `assistant-${Date.now()}`;
      startAssistantMessage(assistantId);

      const handleEvent = (event: StreamingEvent) => {
        // Handle mission events separately
        if (isMissionStreamEvent(event)) {
          console.log('[Chat Hook] Processing mission event:', { type: event.type, stage: event.stage });
          addMissionEvent(assistantId, event as MissionStreamEvent);

          // Handle mission complete event
          if (event.type === 'mission_complete') {
            finishAssistantMessage(assistantId);
          }
          // Handle mission error event
          if (event.type === 'mission_error') {
            appendToAssistantMessage(assistantId, `\n\nMission Error: ${event.error || 'Unknown error'}`);
            if (!event.can_retry) {
              finishAssistantMessage(assistantId);
            }
          }
          return;
        }

        // Handle legacy agent events
        const agentEvent = event as AgentEvent;
        addEvent(assistantId, agentEvent);

        switch (agentEvent.type) {
          case 'token':
            if (agentEvent.content) {
              const chunkType = agentEvent.chunk_type as ChunkType;
              if (chunkType && chunkType !== 'text') {
                appendStructuredContent(assistantId, chunkType, agentEvent.content);
              } else {
                appendToAssistantMessage(assistantId, agentEvent.content);
              }
            }
            break;

          // Structured chunk types from backend SSE
          case 'sql':
          case 'summary':
          case 'insights':
          case 'chart_recommendations':
          case 'reasoning':
            if (agentEvent.content) {
              appendStructuredContent(assistantId, agentEvent.type as ChunkType, agentEvent.content);
            }
            break;

          case 'text':
            if (agentEvent.content) {
              appendToAssistantMessage(assistantId, agentEvent.content);
            }
            break;

          case 'status':
            if (agentEvent.message) {
              updateProcessStatus(assistantId, agentEvent.message);
            }
            break;

          case 'todo_update':
            if (agentEvent.todos) {
              updateTodos(agentEvent.todos);
            }
            break;

          case 'done':
            finishAssistantMessage(assistantId);
            break;

          case 'error':
            appendToAssistantMessage(assistantId, `\n\nError: ${agentEvent.error || agentEvent.message}`);
            finishAssistantMessage(assistantId);
            break;
        }
      };

      const handleError = (error: Error) => {
        appendToAssistantMessage(assistantId, `\n\nConnection error: ${error.message}`);
        finishAssistantMessage(assistantId);
      };

      const handleComplete = () => {
        finishAssistantMessage(assistantId);
      };

      abortRef.current = agentApi.streamTask(
        currentSessionId,
        content,
        handleEvent,
        handleError,
        handleComplete
      );
    },
    [
      addUserMessage,
      startAssistantMessage,
      appendToAssistantMessage,
      appendStructuredContent,
      updateProcessStatus,
      updateTodos,
      addEvent,
      addMissionEvent,
      finishAssistantMessage,
    ]
  );

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
      setStreaming(false);
    }
  }, [setStreaming]);

  return {
    sessionId,
    connectionId,
    messages,
    currentTodos,
    isStreaming,
    setSession,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}
