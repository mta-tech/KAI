'use client';

import { useMemo } from 'react';
import { VisualizationCard, type ChartData, type ChartType } from './visualization-card';

export interface ChartRecommendation {
  chart_type: 'bar' | 'line' | 'pie';
  title: string;
  description?: string;
  x_axis?: string;
  y_axis?: string;
  reason?: string;
}

export interface VisualizationsProps {
  data: ChartData[];
  recommendations: string | ChartRecommendation[];
  className?: string;
}

// Parse chart recommendations from markdown/JSON
function parseRecommendations(
  recommendations: string | ChartRecommendation[]
): ChartRecommendation[] {
  if (Array.isArray(recommendations)) {
    return recommendations;
  }

  // Try to parse JSON from markdown code blocks
  const jsonMatch = recommendations.match(/```json\s*([\s\S]*?)\s*```/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[1]);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    } catch {
      // Not valid JSON, continue
    }
  }

  // Parse from list format
  const lines = recommendations.split('\n').filter((line) => line.trim());
  const parsed: ChartRecommendation[] = [];

  for (const line of lines) {
    // Match format: "- **ChartType**: Title - description"
    const match = line.match(/-\s*\*\*(Bar|Line|Pie)\*:\*\s*(.+?)(?:\s+-\s*(.+))?$/);
    if (match) {
      const [, chartType, title, description] = match;
      parsed.push({
        chart_type: chartType.toLowerCase() as ChartType,
        title: title.trim(),
        description: description?.trim(),
      });
    }
  }

  return parsed;
}

// Extract color scheme from recommendations
function getColorScheme(title: string): 'default' | 'blue' | 'green' | 'purple' | 'orange' {
  const lowerTitle = title.toLowerCase();

  if (lowerTitle.includes('sales') || lowerTitle.includes('revenue')) {
    return 'green';
  }
  if (lowerTitle.includes('traffic') || lowerTitle.includes('users')) {
    return 'blue';
  }
  if (lowerTitle.includes('distribution') || lowerTitle.includes('share')) {
    return 'purple';
  }
  if (lowerTitle.includes('growth') || lowerTitle.includes('trend')) {
    return 'orange';
  }

  return 'default';
}

export function Visualizations({
  data,
  recommendations,
  className,
}: VisualizationsProps) {
  const parsedRecommendations = useMemo(
    () => parseRecommendations(recommendations),
    [recommendations]
  );

  if (!parsedRecommendations || parsedRecommendations.length === 0) {
    return null;
  }

  return (
    <div className={className}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {parsedRecommendations.map((rec, index) => (
          <VisualizationCard
            key={`${rec.chart_type}-${index}`}
            title={rec.title}
            description={rec.description || rec.reason}
            type={rec.chart_type}
            data={data}
            xAxisKey={rec.x_axis || 'name'}
            yAxisKey={rec.y_axis || 'value'}
            colorScheme={getColorScheme(rec.title)}
          />
        ))}
      </div>
    </div>
  );
}

// Hook to extract visualization data from message events
export function useVisualizationData(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  events: any[] = []
): {
  data: ChartData[];
  hasData: boolean;
} {
  return useMemo(() => {
    // Look for chart data in tool_end events
    for (let i = events.length - 1; i >= 0; i--) {
      const event = events[i];
      if (event.type === 'tool_end' && event.tool === 'generate_chart') {
        const output = typeof event.output === 'string'
          ? JSON.parse(event.output)
          : event.output;

        if (output.data && Array.isArray(output.data)) {
          return {
            data: output.data,
            hasData: true,
          };
        }
      }
    }

    return { data: [], hasData: false };
  }, [events]);
}
