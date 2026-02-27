/** Format an array or object value to a markdown string. */
export function formatToMarkdown(value: unknown): string {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (typeof item === 'string') return `- ${item}`;
      if (typeof item === 'object' && item !== null) {
        const obj = item as Record<string, unknown>;
        if (obj.title && obj.description) {
          return `**${obj.title}**: ${obj.description}`;
        }
        if (obj.chart_type && obj.reason) {
          return `**${obj.chart_type}**: ${obj.reason}`;
        }
        return `- ${JSON.stringify(item)}`;
      }
      return `- ${String(item)}`;
    }).join('\n');
  }
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

/** Parse JSON from a markdown code block or raw JSON content. */
export function parseJsonContent(content: string): { parsed: Record<string, unknown> | null; text: string } {
  const jsonBlockMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
  if (jsonBlockMatch) {
    try {
      const parsed = JSON.parse(jsonBlockMatch[1]);
      const text = content.replace(/```json\s*[\s\S]*?\s*```/, '').trim();
      return { parsed, text };
    } catch {
      // Not valid JSON, fall through
    }
  }

  const trimmed = content.trim();
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    try {
      const parsed = JSON.parse(trimmed);
      return { parsed, text: '' };
    } catch {
      // Not valid JSON
    }
  }

  return { parsed: null, text: content };
}
