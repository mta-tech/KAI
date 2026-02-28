import { useState, useMemo } from 'react';
import { isWithinInterval, startOfDay, endOfDay, subDays, subMonths } from '@/lib/date-utils';
import { highlightText } from './chat-search-utils';
import type { ChatMessage } from '@/stores/chat-store';
import type { DateRangePreset, ChatTypeFilter } from './chat-search-utils';

export interface SearchFilters {
  query: string;
  dateRange: DateRangePreset;
  customDateStart: Date | undefined;
  customDateEnd: Date | undefined;
  chatType: ChatTypeFilter;
  sessionId: string | 'all';
}

export interface SearchResult {
  messageId: string;
  message: ChatMessage;
  highlightedContent: string;
  relevanceScore: number;
}

const DEFAULT_FILTERS: SearchFilters = {
  query: '',
  dateRange: 'all',
  customDateStart: undefined,
  customDateEnd: undefined,
  chatType: 'all',
  sessionId: 'all',
};

export function useChatSearch() {
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const searchMessages = (messages: ChatMessage[], sessions: unknown[] = []): SearchResult[] => {
    const { query, dateRange, chatType, customDateStart, customDateEnd } = filters;

    if (!query && dateRange === 'all' && chatType === 'all' && filters.sessionId === 'all') {
      return [];
    }

    const results: SearchResult[] = [];
    const lowerQuery = query.toLowerCase();

    messages.forEach((message) => {
      // Date range filter
      if (dateRange !== 'all') {
        const messageDate = new Date(message.timestamp);
        let startDate: Date;
        let endDate = new Date();

        switch (dateRange) {
          case 'today':
            startDate = startOfDay(new Date());
            endDate = endOfDay(new Date());
            break;
          case 'week':
            startDate = startOfDay(subDays(new Date(), 7));
            break;
          case 'month':
            startDate = startOfDay(subMonths(new Date(), 1));
            break;
          case 'custom':
            if (!customDateStart || !customDateEnd) return;
            startDate = startOfDay(customDateStart);
            endDate = endOfDay(customDateEnd);
            break;
          default:
            return;
        }

        if (!isWithinInterval(messageDate, { start: startDate, end: endDate })) {
          return;
        }
      }

      // Chat type filter
      if (chatType !== 'all') {
        switch (chatType) {
          case 'user':
            if (message.role !== 'user') return;
            break;
          case 'assistant':
            if (message.role !== 'assistant') return;
            break;
          case 'sql':
            if (!message.structured?.sql) return;
            break;
          case 'with_todos':
            if (!message.todos || message.todos.length === 0) return;
            break;
        }
      }

      // Text search
      if (lowerQuery) {
        const content = message.content.toLowerCase();
        const sql = message.structured?.sql?.toLowerCase() || '';
        const summary = message.structured?.summary?.toLowerCase() || '';
        const insights = message.structured?.insights?.toLowerCase() || '';

        const matchesQuery =
          content.includes(lowerQuery) ||
          sql.includes(lowerQuery) ||
          summary.includes(lowerQuery) ||
          insights.includes(lowerQuery);

        if (!matchesQuery) return;

        let score = 0;
        if (content.includes(lowerQuery)) score += 3;
        if (sql.includes(lowerQuery)) score += 5;
        if (summary.includes(lowerQuery)) score += 4;
        if (insights.includes(lowerQuery)) score += 2;
        if (content === lowerQuery || sql === lowerQuery) score += 10;

        results.push({
          messageId: message.id,
          message,
          highlightedContent: highlightText(message.content, lowerQuery),
          relevanceScore: score,
        });
      } else {
        results.push({
          messageId: message.id,
          message,
          highlightedContent: message.content,
          relevanceScore: 0,
        });
      }
    });

    results.sort((a, b) => b.relevanceScore - a.relevanceScore);
    return results;
  };

  const hasActiveFilters = useMemo(() =>
    filters.query !== '' ||
    filters.dateRange !== 'all' ||
    filters.chatType !== 'all' ||
    filters.sessionId !== 'all',
    [filters],
  );

  const clearFilters = () => setFilters(DEFAULT_FILTERS);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.query !== '') count++;
    if (filters.dateRange !== 'all') count++;
    if (filters.chatType !== 'all') count++;
    return count;
  }, [filters]);

  return {
    filters,
    setFilters,
    isFilterOpen,
    setIsFilterOpen,
    searchMessages,
    hasActiveFilters,
    clearFilters,
    activeFilterCount,
  };
}
