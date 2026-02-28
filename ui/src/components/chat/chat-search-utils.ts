export type DateRangePreset = 'today' | 'week' | 'month' | 'custom' | 'all';
export type ChatTypeFilter = 'all' | 'user' | 'assistant' | 'sql' | 'with_todos';

/** Escape special regex characters in a string. */
export function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Wrap matched text in a highlight mark for display. */
export function highlightText(text: string, query: string): string {
  if (!query) return text;
  const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
  return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded px-0.5">$1</mark>');
}

/** Human-readable label for a ChatTypeFilter value. */
export function getChatTypeLabel(type: ChatTypeFilter): string {
  switch (type) {
    case 'user': return 'User messages';
    case 'assistant': return 'AI responses';
    case 'sql': return 'With SQL';
    case 'with_todos': return 'With tasks';
    default: return 'All messages';
  }
}
