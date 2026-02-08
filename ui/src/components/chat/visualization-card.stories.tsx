import type { Meta, StoryObj } from '@storybook/react';
import { VisualizationCard, type ChartData, type ChartType } from './visualization-card';

const meta: Meta<typeof VisualizationCard> = {
  title: 'Chat/VisualizationCard',
  component: VisualizationCard,
  parameters: {
    layout: 'centered',
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#0f172a' },
      ],
    },
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['bar', 'line', 'pie'] as ChartType[],
      description: 'Type of chart to display',
    },
    colorScheme: {
      control: 'select',
      options: ['default', 'blue', 'green', 'purple', 'orange'] as const,
      description: 'Color scheme for the chart (uses design tokens)',
    },
    data: {
      control: 'object',
      description: 'Chart data array',
    },
  },
};

export default meta;
type Story = StoryObj<typeof VisualizationCard>;

// Sample data for demonstrations
const sampleData: ChartData[] = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 600 },
  { name: 'Apr', value: 800 },
  { name: 'May', value: 500 },
];

const salesData: ChartData[] = [
  { name: 'Product A', value: 12000 },
  { name: 'Product B', value: 8500 },
  { name: 'Product C', value: 15000 },
  { name: 'Product D', value: 9200 },
];

const distributionData: ChartData[] = [
  { name: 'Desktop', value: 45 },
  { name: 'Mobile', value: 35 },
  { name: 'Tablet', value: 20 },
];

export const BarChart: Story = {
  args: {
    title: 'Monthly Revenue',
    description: 'Revenue breakdown by month for Q1-Q2',
    type: 'bar',
    data: sampleData,
    xAxisKey: 'name',
    yAxisKey: 'value',
    colorScheme: 'default',
  },
};

export const BarChartSales: Story = {
  args: {
    title: 'Sales by Product',
    description: 'Total sales performance across all products',
    type: 'bar',
    data: salesData,
    xAxisKey: 'name',
    yAxisKey: 'value',
    colorScheme: 'green', // Green theme for sales
  },
};

export const LineChart: Story = {
  args: {
    title: 'User Growth Trend',
    description: 'Monthly active users over time',
    type: 'line',
    data: sampleData,
    xAxisKey: 'name',
    yAxisKey: 'value',
    colorScheme: 'orange', // Orange theme for growth/trends
  },
};

export const LineChartTraffic: Story = {
  args: {
    title: 'Website Traffic',
    description: 'Daily visitors for the past week',
    type: 'line',
    data: [
      { name: 'Mon', value: 1200 },
      { name: 'Tue', value: 1450 },
      { name: 'Wed', value: 1100 },
      { name: 'Thu', value: 1680 },
      { name: 'Fri', value: 1900 },
      { name: 'Sat', value: 2100 },
      { name: 'Sun', value: 1850 },
    ],
    colorScheme: 'blue', // Blue theme for traffic
  },
};

export const PieChart: Story = {
  args: {
    title: 'Device Distribution',
    description: 'User distribution across device types',
    type: 'pie',
    data: distributionData,
    xAxisKey: 'name',
    yAxisKey: 'value',
    colorScheme: 'purple', // Purple theme for distribution
  },
};

export const WithDescription: Story = {
  args: {
    title: 'Regional Performance',
    description: 'Sales performance by region showing consistent growth across all markets',
    type: 'bar',
    data: [
      { name: 'North', value: 45000 },
      { name: 'South', value: 38000 },
      { name: 'East', value: 52000 },
      { name: 'West', value: 41000 },
    ],
    colorScheme: 'default',
  },
};

export const LargeDataset: Story = {
  args: {
    title: 'Annual Performance',
    description: 'Complete year performance data',
    type: 'bar',
    data: Array.from({ length: 12 }, (_, i) => ({
      name: new Date(2024, i).toLocaleDateString('en-US', { month: 'short' }),
      value: Math.floor(Math.random() * 1000) + 500,
    })),
    colorScheme: 'default',
  },
};

// Dark mode examples
export const BarChartDark: Story = {
  args: {
    title: 'Monthly Revenue',
    description: 'Revenue breakdown by month for Q1-Q2',
    type: 'bar',
    data: sampleData,
    colorScheme: 'default',
  },
  parameters: {
    backgrounds: {
      default: 'dark',
    },
  },
};

export const PieChartDark: Story = {
  args: {
    title: 'Market Share',
    description: 'Current market distribution',
    type: 'pie',
    data: [
      { name: 'Company A', value: 35 },
      { name: 'Company B', value: 25 },
      { name: 'Company C', value: 20 },
      { name: 'Others', value: 20 },
    ],
    colorScheme: 'default',
  },
  parameters: {
    backgrounds: {
      default: 'dark',
    },
  },
};

// Color scheme examples
export const ColorSchemeBlue: Story = {
  args: {
    title: 'User Acquisition',
    description: 'New users by channel',
    type: 'bar',
    data: [
      { name: 'Organic', value: 2300 },
      { name: 'Direct', value: 1800 },
      { name: 'Referral', value: 1200 },
      { name: 'Social', value: 950 },
    ],
    colorScheme: 'blue',
  },
};

export const ColorSchemeGreen: Story = {
  args: {
    title: 'Revenue by Quarter',
    description: 'Quarterly revenue performance',
    type: 'bar',
    data: [
      { name: 'Q1', value: 125000 },
      { name: 'Q2', value: 142000 },
      { name: 'Q3', value: 168000 },
      { name: 'Q4', value: 195000 },
    ],
    colorScheme: 'green',
  },
};

export const ColorSchemePurple: Story = {
  args: {
    title: 'Category Distribution',
    description: 'Product category breakdown',
    type: 'pie',
    data: [
      { name: 'Electronics', value: 40 },
      { name: 'Clothing', value: 25 },
      { name: 'Home', value: 20 },
      { name: 'Other', value: 15 },
    ],
    colorScheme: 'purple',
  },
};

export const ColorSchemeOrange: Story = {
  args: {
    title: 'Growth Rate',
    description: 'Month-over-month growth percentage',
    type: 'line',
    data: [
      { name: 'Jan', value: 12 },
      { name: 'Feb', value: 15 },
      { name: 'Mar', value: 18 },
      { name: 'Apr', value: 22 },
      { name: 'May', value: 25 },
    ],
    colorScheme: 'orange',
  },
};

// Interactive examples
export const ExportExample: Story = {
  args: {
    title: 'Exportable Chart',
    description: 'Use the menu in the top-right to export as image or CSV',
    type: 'bar',
    data: salesData,
    colorScheme: 'default',
  },
};
