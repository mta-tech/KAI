import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Skeleton } from '@/components/ui/skeleton';

describe('Skeleton Component', () => {
  describe('Rendering', () => {
    it('should render default skeleton', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveClass('animate-pulse');
      expect(skeleton).toHaveClass('bg-muted');
    });

    it('should render with custom className', () => {
      const { container } = render(<Skeleton className="custom-class" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('custom-class');
    });

    it('should merge className with default classes', () => {
      const { container } = render(<Skeleton className="w-20 h-20" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('animate-pulse');
      expect(skeleton).toHaveClass('w-20');
      expect(skeleton).toHaveClass('h-20');
    });

    it('should be empty (no children)', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton).toBeEmptyDOMElement();
    });
  });

  describe('Visual Styling', () => {
    it('should apply rounded corners by default', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('rounded-md');
    });

    it('should apply custom border radius', () => {
      const { container } = render(<Skeleton className="rounded-full" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('rounded-full');
    });

    it('should apply custom background color via className', () => {
      const { container } = render(<Skeleton className="bg-gray-200" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('bg-gray-200');
    });

    it('should apply inline styles', () => {
      const { container } = render(<Skeleton style={{ width: '100px', height: '50px' }} />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveStyle({ width: '100px' });
      expect(skeleton).toHaveStyle({ height: '50px' });
    });
  });

  describe('Size Variations', () => {
    it('should render text skeleton size', () => {
      const { container } = render(<Skeleton className="h-4 w-24" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-4');
      expect(skeleton).toHaveClass('w-24');
    });

    it('should render avatar skeleton size', () => {
      const { container } = render(<Skeleton className="h-12 w-12 rounded-full" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-12');
      expect(skeleton).toHaveClass('w-12');
      expect(skeleton).toHaveClass('rounded-full');
    });

    it('should render card skeleton size', () => {
      const { container } = render(<Skeleton className="h-32 w-full" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-32');
      expect(skeleton).toHaveClass('w-full');
    });

    it('should render circular skeleton', () => {
      const { container } = render(<Skeleton className="h-16 w-16 rounded-full" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('rounded-full');
      expect(skeleton).toHaveClass('h-16');
      expect(skeleton).toHaveClass('w-16');
    });
  });

  describe('Animation', () => {
    it('should have pulse animation by default', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('animate-pulse');
    });

    it('should allow custom animation classes', () => {
      const { container } = render(<Skeleton className="animate-bounce" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('animate-bounce');
    });

    it('should allow disabling animation', () => {
      const { container } = render(<Skeleton className="animate-none" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('animate-none');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-hidden="true" by default', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveAttribute('aria-hidden', 'true');
    });

    it('should have role="status" for accessibility', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveAttribute('role', 'status');
    });

    it('should be hidden from screen readers', () => {
      const { container } = render(<Skeleton />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Data Attributes', () => {
    it('should pass through data attributes', () => {
      const { container } = render(<Skeleton data-testid="test-skeleton" data-type="loading" />);
      const skeleton = container.querySelector('[data-testid="test-skeleton"]');
      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveAttribute('data-type', 'loading');
    });

    it('should support custom data attributes', () => {
      const { container } = render(<Skeleton data-loading="true" data-variant="circular" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton).toHaveAttribute('data-loading', 'true');
      expect(skeleton).toHaveAttribute('data-variant', 'circular');
    });
  });

  describe('Layout Patterns', () => {
    it('should work in flex containers', () => {
      const { container } = render(
        <div className="flex gap-2">
          <Skeleton className="flex-1" />
          <Skeleton className="flex-1" />
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(2);
    });

    it('should work in grid layouts', () => {
      const { container } = render(
        <div className="grid grid-cols-3 gap-4">
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(3);
    });

    it('should work in vertical stacks', () => {
      const { container } = render(
        <div className="space-y-2">
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(3);
    });
  });

  describe('Common UI Patterns', () => {
    it('should create a card loading pattern', () => {
      const { container } = render(
        <div className="space-y-3">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(4);
    });

    it('should create an avatar loading pattern', () => {
      const { container } = render(
        <div className="flex items-center space-x-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(3);
    });

    it('should create a table loading pattern', () => {
      const { container } = render(
        <div className="space-y-2">
          <div className="flex gap-4">
            <Skeleton className="h-8 flex-1" />
            <Skeleton className="h-8 flex-1" />
            <Skeleton className="h-8 flex-1" />
          </div>
          <div className="flex gap-4">
            <Skeleton className="h-8 flex-1" />
            <Skeleton className="h-8 flex-1" />
            <Skeleton className="h-8 flex-1" />
          </div>
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(6);
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero dimensions', () => {
      const { container } = render(<Skeleton className="h-0 w-0" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-0');
      expect(skeleton).toHaveClass('w-0');
    });

    it('should handle very large dimensions', () => {
      const { container } = render(<Skeleton className="h-[1000px] w-[1000px]" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-[1000px]');
      expect(skeleton).toHaveClass('w-[1000px]');
    });

    it('should handle percentage dimensions', () => {
      const { container } = render(<Skeleton className="h-full w-1/2" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('h-full');
      expect(skeleton).toHaveClass('w-1/2');
    });
  });

  describe('Composition', () => {
    it('should work with other components', () => {
      const { container } = render(
        <div>
          <Skeleton className="h-4 w-1/4 mb-2" />
          <p>Actual content</p>
          <Skeleton className="h-4 w-3/4 mt-2" />
        </div>
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(2);
      expect(screen.getByText('Actual content')).toBeInTheDocument();
    });

    it('should work in conditional rendering', () => {
      const { container, rerender } = render(<Skeleton />);
      let skeleton = container.firstChild;
      expect(skeleton).toHaveClass('animate-pulse');

      rerender(<div>Content loaded</div>);
      expect(screen.queryByText('Content loaded')).toBeInTheDocument();
      expect(container.querySelector('.animate-pulse')).not.toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should render efficiently', () => {
      const startTime = performance.now();
      const { container } = render(
        <>
          <Skeleton />
          <Skeleton />
          <Skeleton />
          <Skeleton />
          <Skeleton />
        </>
      );
      const endTime = performance.now();
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(5);
      expect(endTime - startTime).toBeLessThan(100);
    });
  });

  describe('CSS Integration', ()   => {
    it('should work with Tailwind utilities', () => {
      const { container } = render(<Skeleton className="bg-blue-100 dark:bg-blue-900" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('bg-blue-100');
      expect(skeleton).toHaveClass('dark:bg-blue-900');
    });

    it('should support arbitrary values', () => {
      const { container } = render(<Skeleton className="w-[123px] h-[456px]" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('w-[123px]');
      expect(skeleton).toHaveClass('h-[456px]');
    });

    it('should support important modifier', () => {
      const { container } = render(<Skeleton className="!w-full" />);
      const skeleton = container.firstChild;
      expect(skeleton).toHaveClass('!w-full');
    });
  });
});
