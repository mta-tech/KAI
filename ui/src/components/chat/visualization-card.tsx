'use client';

import { useRef, useState } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  MoreHorizontal,
  FileImage,
  Table as TableIcon,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export type ChartType = 'bar' | 'line' | 'pie';

export interface ChartData {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface VisualizationCardProps {
  title: string;
  description?: string;
  type: ChartType;
  data: ChartData[];
  xAxisKey?: string;
  yAxisKey?: string;
  colorScheme?: 'default' | 'blue' | 'green' | 'purple' | 'orange';
  className?: string;
}

// Color schemes for charts - using design tokens for consistency
// Default scheme uses primary brand color (Deep Indigo) as base
const colorSchemes = {
  // Primary (Deep Indigo) + complementary colors from design system
  default: ['hsl(239 84% 67%)', 'hsl(262 83% 58%)', 'hsl(330 81% 60%)', 'hsl(35 92% 60%)', 'hsl(142 71% 45%)', 'hsl(239 84% 58%)'],
  // Blue palette (from design tokens)
  blue: ['hsl(221 83% 53%)', 'hsl(217 91% 60%)', 'hsl(214 95% 66%)', 'hsl(215 98% 76%)', 'hsl(215 100% 86%)', 'hsl(215 100% 94%)'],
  // Green palette (from design tokens)
  green: ['hsl(142 76% 36%)', 'hsl(142 71% 45%)', 'hsl(141 73% 48%)', 'hsl(142 76% 52%)', 'hsl(142 71% 60%)', 'hsl(142 79% 70%)'],
  // Purple palette (from design tokens)
  purple: ['hsl(270 67% 31%)', 'hsl(268 72% 45%)', 'hsl(268 78% 56%)', 'hsl(268 82% 67%)', 'hsl(268 80% 77%)', 'hsl(268 86% 88%)'],
  // Orange palette (from design tokens)
  orange: ['hsl(20 67% 39%)', 'hsl(24 72% 46%)', 'hsl(24 72% 56%)', 'hsl(25 95% 53%)', 'hsl(25 97% 60%)', 'hsl(25 97% 73%)'],
};

// Custom tooltip with better styling
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-popover border border-border rounded-lg shadow-lg p-3">
      <p className="text-sm font-medium text-foreground">{label}</p>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-sm" style={{ color: entry.color }}>
          {entry.name}: {entry.value.toLocaleString()}
        </p>
      ))}
    </div>
  );
};

// Custom legend
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomLegend = ({ payload }: any) => {
  return (
    <div className="flex flex-wrap justify-center gap-4 mt-4">
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-xs text-muted-foreground">{entry.value}</span>
        </div>
      ))}
    </div>
  );
};

export function VisualizationCard({
  title,
  description,
  type,
  data,
  xAxisKey = 'name',
  yAxisKey = 'value',
  colorScheme = 'default',
  className,
}: VisualizationCardProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const colors = colorSchemes[colorScheme];

  // Export chart as image
  const exportAsImage = async () => {
    setIsExporting(true);
    try {
      const element = chartRef.current;
      if (!element) return;

      // Use HTML Canvas API to capture the chart
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Set canvas size
      canvas.width = 800;
      canvas.height = 400;

      // Fill background - using design token colors
      const isDark = document.documentElement.classList.contains('dark');
      ctx.fillStyle = isDark
        ? '#0f172a' // slate-950 (dark background from design tokens)
        : '#ffffff'; // white (light background)
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Add title - using design token colors
      ctx.fillStyle = isDark
        ? '#f8fafc' // slate-50 (light text in dark mode)
        : '#0f172a'; // slate-950 (dark text in light mode)
      ctx.font = 'bold 20px sans-serif';
      ctx.fillText(title, 20, 30);

      // Simple SVG capture for chart
      const svgElement = element.querySelector('svg');
      if (svgElement) {
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);

        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 20, 50, 760, 330);
          URL.revokeObjectURL(url);

          // Download
          canvas.toBlob((blob) => {
            if (blob) {
              const link = document.createElement('a');
              link.download = `${title.toLowerCase().replace(/\s+/g, '-')}.png`;
              link.href = URL.createObjectURL(blob);
              link.click();
            }
            setIsExporting(false);
          });
        };
        img.onerror = () => {
          // Fallback: notify user
          console.error('Failed to export chart as image');
          setIsExporting(false);
        };
        img.src = url;
      } else {
        setIsExporting(false);
      }
    } catch (error) {
      console.error('Error exporting chart:', error);
      setIsExporting(false);
    }
  };

  // Export data as CSV
  const exportAsCSV = () => {
    const headers = [xAxisKey, yAxisKey];
    const rows = data.map((item) => [item[xAxisKey], item[yAxisKey]]);
    const csv = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = `${title.toLowerCase().replace(/\s+/g, '-')}.csv`;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  };

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 5 },
    };

    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey={xAxisKey}
                className="text-xs"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fontSize: 11 }}
              />
              <YAxis
                className="text-xs"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fontSize: 11 }}
                width={45}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend />} />
              <Bar
                dataKey={yAxisKey}
                fill={colors[0]}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey={xAxisKey}
                className="text-xs"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fontSize: 11 }}
              />
              <YAxis
                className="text-xs"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fontSize: 11 }}
                width={45}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend />} />
              <Line
                type="monotone"
                dataKey={yAxisKey}
                stroke={colors[0]}
                strokeWidth={2}
                dot={{ fill: colors[0], r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => (
                  <tspan style={{ fontSize: '11px' }}>{entry.name}</tspan>
                )}
                outerRadius={70}
                fill={colors[0]}
                dataKey={yAxisKey}
              >
                {data.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend />} />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <Card
      ref={chartRef}
      className={cn('overflow-hidden transition-all hover:shadow-md', className)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 flex-1 min-w-0">
            <CardTitle className="text-base sm:text-lg truncate">{title}</CardTitle>
            {description && (
              <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
            )}
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-11 w-11 p-0 flex-shrink-0"
                aria-label="Chart options"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={exportAsImage}
                disabled={isExporting}
                className="min-h-[44px]"
              >
                <FileImage className="h-4 w-4 mr-2" />
                Export as Image
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={exportAsCSV}
                className="min-h-[44px]"
              >
                <TableIcon className="h-4 w-4 mr-2" />
                Export as CSV
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="w-full">{renderChart()}</div>
      </CardContent>
    </Card>
  );
}
