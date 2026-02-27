'use client';

import { useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import {
  Search,
  Filter,
  X,
  ChevronDown,
  CalendarIcon,
  MessageSquare,
  Code,
  FileText,
} from 'lucide-react';
import { format } from '@/lib/date-utils';
import type { ChatMessage } from '@/stores/chat-store';
import { useChatSearch } from './use-chat-search';
import { getChatTypeLabel } from './chat-search-utils';
import type { DateRangePreset, ChatTypeFilter } from './chat-search-utils';

export { useChatSearch } from './use-chat-search';

interface ChatSearchProps {
  messages: ChatMessage[];
  sessions?: any[];
  onResultsFound?: (count: number) => void;
  onResultClick?: (messageId: string) => void;
}

export function ChatSearch({ messages, sessions, onResultsFound, onResultClick }: ChatSearchProps) {
  const {
    filters,
    setFilters,
    isFilterOpen,
    setIsFilterOpen,
    searchMessages,
    hasActiveFilters,
    clearFilters,
    activeFilterCount,
  } = useChatSearch();

  const searchResults = useMemo(() => searchMessages(messages, sessions || []), [filters, messages, sessions, searchMessages]);

  // Notify parent of results count
  useMemo(() => {
    onResultsFound?.(searchResults.length);
  }, [searchResults.length, onResultsFound]);

  const getDateRangeLabel = () => {
    switch (filters.dateRange) {
      case 'today':
        return 'Today';
      case 'week':
        return 'Last 7 days';
      case 'month':
        return 'Last 30 days';
      case 'custom':
        return filters.customDateStart && filters.customDateEnd
          ? `${format(filters.customDateStart, 'MMM d')} - ${format(filters.customDateEnd, 'MMM d')}`
          : 'Custom range';
      case 'all':
      default:
        return 'All time';
    }
  };

  return (
    <div className="space-y-2">
      {/* Search Input */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search messages..."
            value={filters.query}
            onChange={(e) => setFilters({ ...filters, query: e.target.value })}
            className="pl-9 pr-8"
          />
          {filters.query && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-2"
              onClick={() => setFilters({ ...filters, query: '' })}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" className="relative">
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {activeFilterCount > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1 text-xs">
                  {activeFilterCount}
                </Badge>
              )}
              <ChevronDown className="h-4 w-4 ml-2" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="start">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Search Filters</h3>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    Clear all
                  </Button>
                )}
              </div>

              {/* Date Range Filter */}
              <div className="space-y-2">
                <Label>Date Range</Label>
                <Select
                  value={filters.dateRange}
                  onValueChange={(value: DateRangePreset) =>
                    setFilters({ ...filters, dateRange: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All time</SelectItem>
                    <SelectItem value="today">Today</SelectItem>
                    <SelectItem value="week">Last 7 days</SelectItem>
                    <SelectItem value="month">Last 30 days</SelectItem>
                    <SelectItem value="custom">Custom range</SelectItem>
                  </SelectContent>
                </Select>

                {filters.dateRange === 'custom' && (
                  <div className="space-y-2">
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start">
                          <CalendarIcon className="h-4 w-4 mr-2" />
                          {filters.customDateStart
                            ? format(filters.customDateStart, 'MMM d, yyyy')
                            : 'Start date'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={filters.customDateStart}
                          onSelect={(date) =>
                            setFilters({ ...filters, customDateStart: date })
                          }
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>

                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start">
                          <CalendarIcon className="h-4 w-4 mr-2" />
                          {filters.customDateEnd
                            ? format(filters.customDateEnd, 'MMM d, yyyy')
                            : 'End date'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={filters.customDateEnd}
                          onSelect={(date) =>
                            setFilters({ ...filters, customDateEnd: date })
                          }
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                )}
              </div>

              {/* Chat Type Filter */}
              <div className="space-y-2">
                <Label>Message Type</Label>
                <Select
                  value={filters.chatType}
                  onValueChange={(value: ChatTypeFilter) =>
                    setFilters({ ...filters, chatType: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All messages</SelectItem>
                    <SelectItem value="user">User messages</SelectItem>
                    <SelectItem value="assistant">AI responses</SelectItem>
                    <SelectItem value="sql">Messages with SQL</SelectItem>
                    <SelectItem value="with_todos">Messages with tasks</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Session Filter - Note: Session filtering would require tracking session info in messages */}
              {/* This is a placeholder for future implementation */}
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex items-center gap-2 flex-wrap">
          {filters.query && (
            <Badge variant="secondary" className="gap-1">
              <Search className="h-3 w-3" />
              "{filters.query}"
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => setFilters({ ...filters, query: '' })}
              />
            </Badge>
          )}
          {filters.dateRange !== 'all' && (
            <Badge variant="secondary" className="gap-1">
              <CalendarIcon className="h-3 w-3" />
              {getDateRangeLabel()}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => setFilters({ ...filters, dateRange: 'all' })}
              />
            </Badge>
          )}
          {filters.chatType !== 'all' && (
            <Badge variant="secondary" className="gap-1">
              <MessageSquare className="h-3 w-3" />
              {getChatTypeLabel(filters.chatType)}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => setFilters({ ...filters, chatType: 'all' })}
              />
            </Badge>
          )}
          {/* Session filter display would go here when implemented */}
        </div>
      )}

      {/* Search Results */}
      {(searchResults.length > 0 || hasActiveFilters) && (
        <div className="border rounded-lg">
          {searchResults.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              No messages match your search criteria
            </div>
          ) : (
            <div className="max-h-96 overflow-y-auto">
              <div className="sticky top-0 bg-background border-b px-3 py-2 text-sm font-medium">
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
              </div>
              <div className="divide-y">
                {searchResults.map((result) => (
                  <div
                    key={result.messageId}
                    className="p-3 hover:bg-muted cursor-pointer transition-colors"
                    onClick={() => onResultClick?.(result.messageId)}
                  >
                    <div className="flex items-start gap-2">
                      {result.message.role === 'user' ? (
                        <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="text-xs font-medium">U</span>
                        </div>
                      ) : (
                        <div className="h-6 w-6 rounded-full bg-secondary flex items-center justify-center">
                          <span className="text-xs font-medium">AI</span>
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium truncate">
                            {result.message.role === 'user' ? 'You' : 'AI Assistant'}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {format(new Date(result.message.timestamp), 'MMM d, h:mm a')}
                          </span>
                          {result.message.structured?.sql && (
                            <Badge variant="outline" className="text-xs gap-1">
                              <Code className="h-3 w-3" />
                              SQL
                            </Badge>
                          )}
                          {result.message.todos && result.message.todos.length > 0 && (
                            <Badge variant="outline" className="text-xs gap-1">
                              <FileText className="h-3 w-3" />
                              {result.message.todos.length} tasks
                            </Badge>
                          )}
                        </div>
                        <p
                          className="text-sm text-muted-foreground line-clamp-2"
                          dangerouslySetInnerHTML={{ __html: result.highlightedContent }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

