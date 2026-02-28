import type { Meta, StoryObj } from '@storybook/react';
import {
  Skeleton,
  EnhancedSkeleton,
  SkeletonCard,
  SkeletonList,
  SkeletonTable,
  SkeletonChat,
  SkeletonAvatar,
  SkeletonText,
  SkeletonForm,
  SkeletonDashboard,
} from './skeleton';

const meta = {
  title: 'UI/Skeleton',
  component: Skeleton,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Skeleton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <Skeleton className="h-[100px] w-[200px] rounded-xl" />,
};

export const Variants: Story = {
  render: () => (
    <div className="space-y-4">
      <EnhancedSkeleton variant="default" width="full" height={48} />
      <EnhancedSkeleton variant="shimmer" width="full" height={48} />
      <EnhancedSkeleton variant="pulse" width="full" height={48} />
    </div>
  ),
};

export const WithWidthAndHeight: Story = {
  render: () => (
    <div className="space-y-4">
      <EnhancedSkeleton width={200} height={40} />
      <EnhancedSkeleton width="50%" height={32} />
      <EnhancedSkeleton width="full" height={56} />
    </div>
  ),
};

export const Multiple: Story = {
  render: () => <EnhancedSkeleton count={5} height={40} />,
};

export const CardSkeleton: Story = {
  render: () => (
    <div className="w-80">
      <SkeletonCard />
    </div>
  ),
};

export const ListSkeleton: Story = {
  render: () => (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex items-center space-x-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      ))}
    </div>
  ),
};

export const NewList: Story = {
  render: () => <SkeletonList count={5} />,
};

export const FormSkeleton: Story = {
  render: () => (
    <div className="space-y-4 w-[400px]">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-10 w-[100px]" />
    </div>
  ),
};

export const NewForm: Story = {
  render: () => <SkeletonForm />,
};

export const TableSkeleton: Story = {
  render: () => (
    <div className="space-y-3 w-[500px]">
      <Skeleton className="h-10 w-full" />
      {[1, 2, 3, 4, 5].map((i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  ),
};

export const NewTable: Story = {
  render: () => <SkeletonTable rows={5} columns={4} />,
};

export const ChatSkeleton: Story = {
  render: () => (
    <div className="w-full max-w-md">
      <SkeletonChat />
    </div>
  ),
};

export const AvatarSkeleton: Story = {
  render: () => (
    <div className="flex items-center space-x-4">
      <Skeleton className="h-12 w-12 rounded-full" />
      <Skeleton className="h-4 w-[250px]" />
    </div>
  ),
};

export const NewAvatar: Story = {
  render: () => (
    <div className="flex gap-4">
      <SkeletonAvatar size="sm" />
      <SkeletonAvatar size="default" />
      <SkeletonAvatar size="lg" />
    </div>
  ),
};

export const TextSkeleton: Story = {
  render: () => <SkeletonText lines={3} />,
};

export const MultipleSkeletons: Story = {
  render: () => (
    <div className="flex gap-4">
      <Skeleton className="h-20 w-20 rounded-lg" />
      <Skeleton className="h-20 w-20 rounded-full" />
      <Skeleton className="h-20 w-20" />
      <Skeleton className="h-20 w-20 rounded-xl" />
    </div>
  ),
};

export const DashboardSkeleton: Story = {
  render: () => <SkeletonDashboard />,
};

export const Mobile: Story = {
  render: () => (
    <div className="w-full max-w-sm">
      <SkeletonDashboard />
    </div>
  ),
  parameters: {
    viewport: {
      defaultViewport: 'iphone12',
    },
  },
};

export const ReducedMotion: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <EnhancedSkeleton variant="shimmer" width="full" height={48} />
      <EnhancedSkeleton variant="pulse" width="full" height={48} />
      <SkeletonList count={3} />
    </div>
  ),
  parameters: {
    prefersReducedMotion: 'reduce',
  },
};
