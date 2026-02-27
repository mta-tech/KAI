import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/badge';

describe('Badge Component', () => {
  describe('Rendering', () => {
    it('should render default badge', () => {
      render(<Badge>Default Badge</Badge>);
      const badge = screen.getByText('Default Badge');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('inline-flex');
      expect(badge).toHaveClass('items-center');
      expect(badge).toHaveClass('rounded-full');
    });

    it('should render with custom className', () => {
      render(<Badge className="custom-class">Custom Badge</Badge>);
      const badge = screen.getByText('Custom Badge');
      expect(badge).toHaveClass('custom-class');
    });

    it('should render children correctly', () => {
      render(
        <Badge>
          <span data-testid="child-span">Child content</span>
        </Badge>
      );
      const child = screen.getByTestId('child-span');
      expect(child).toBeInTheDocument();
      expect(child).toHaveTextContent('Child content');
    });

    it('should render with icon', () => {
      render(
        <Badge>
          <svg data-testid="test-icon" />
          Badge with Icon
        </Badge>
      );
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Variant Styling', () => {
    it('should render default variant', () => {
      render(<Badge>Default</Badge>);
      const badge = screen.getByText('Default');
      expect(badge).toHaveClass('border');
      expect(badge).toHaveClass('transparent');
    });

    it('should render secondary variant', () => {
      render(<Badge variant="secondary">Secondary</Badge>);
      const badge = screen.getByText('Secondary');
      expect(badge).toHaveClass('bg-secondary');
    });

    it('should render destructive variant', () => {
      render(<Badge variant="destructive">Destructive</Badge>);
      const badge = screen.getByText('Destructive');
      expect(badge).toHaveClass('bg-destructive');
    });

    it('should render outline variant', () => {
      render(<Badge variant="outline">Outline</Badge>);
      const badge = screen.getByText('Outline');
      expect(badge).toHaveClass('text-foreground');
    });

    it('should render success variant (custom)', () => {
      render(<Badge variant="success">Success</Badge>);
      const badge = screen.getByText('Success');
      expect(badge).toHaveClass('bg-green-500');
    });

    it('should render warning variant (custom)', () => {
      render(<Badge variant="warning">Warning</Badge>);
      const badge = screen.getByText('Warning');
      expect(badge).toHaveClass('bg-yellow-500');
    });
  });

  describe('Size Variants', () => {
    it('should render default size', () => {
      render(<Badge>Default Size</Badge>);
      const badge = screen.getByText('Default Size');
      expect(badge).toHaveClass('px-3');
      expect(badge).toHaveClass('py-1');
    });

    it('should render small size', () => {
      render(<Badge size="sm">Small</Badge>);
      const badge = screen.getByText('Small');
      expect(badge).toHaveClass('text-xs');
    });

    it('should render large size', () => {
      render(<Badge size="lg">Large</Badge>);
      const badge = screen.getByText('Large');
      expect(badge).toHaveClass('text-base');
    });
  });

  describe('Accessibility', () => {
    it('should be accessible by text content', () => {
      render(<Badge>Accessible Badge</Badge>);
      const badge = screen.getByText('Accessible Badge');
      expect(badge).toBeVisible();
    });

    it('should pass through additional ARIA attributes', () => {
      render(<Badge role="status" aria-live="polite">Status Badge</Badge>);
      const badge = screen.getByRole('status');
      expect(badge).toHaveAttribute('aria-live', 'polite');
    });

    it('should handle long text content appropriately', () => {
      render(
        <Badge>
          This is a very long badge text that might need truncation or wrapping
        </Badge>
      );
      const badge = screen.getByText(/very long badge text/);
      expect(badge).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should render with empty content', () => {
      const { container } = render(<Badge>{''}</Badge>);
      const badge = container.querySelector('.inline-flex');
      expect(badge).toBeInTheDocument();
      expect(badge).toBeEmptyDOMElement();
    });

    it('should render with whitespace content', () => {
      render(<Badge>{'   '}</Badge>);
      const badge = screen.getByText('   ');
      expect(badge).toBeInTheDocument();
    });

    it('should render with special characters', () => {
      render(<Badge>Badge with &quot;quotes&quot; &amp; symbols</Badge>);
      const badge = screen.getByText(/quotes/);
      expect(badge).toBeInTheDocument();
    });

    it('should render with number content', () => {
      render(<Badge>{42}</Badge>);
      const badge = screen.getByText('42');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('Interactive Behavior', () => {
    it('should handle click events when made interactive', () => {
      const handleClick = vi.fn();
      const { container } = render(
        <Badge asChild onClick={handleClick}>
          <button>Clickable Badge</button>
        </Badge>
      );
      const button = container.querySelector('button');
      button?.click();
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not be interactive by default', () => {
      render(<Badge>Static Badge</Badge>);
      const badge = screen.getByText('Static Badge');
      expect(badge.tagName).toBe('DIV');
    });
  });

  describe('Composition Patterns', () => {
    it('should work with icons', () => {
      render(
        <Badge>
          <span data-testid="icon">★</span>
          Featured
        </Badge>
      );
      const icon = screen.getByTestId('icon');
      const text = screen.getByText('Featured');
      expect(icon).toBeInTheDocument();
      expect(text).toBeInTheDocument();
    });

    it('should work with avatar components', () => {
      render(
        <Badge>
          <span data-testid="avatar">AB</span>
          User Badge
        </Badge>
      );
      const avatar = screen.getByTestId('avatar');
      expect(avatar).toBeInTheDocument();
    });

    it('should work in flex containers', () => {
      const { container } = render(
        <div className="flex gap-2">
          <Badge>Badge 1</Badge>
          <Badge>Badge 2</Badge>
          <Badge>Badge 3</Badge>
        </div>
      );
      const badges = container.querySelectorAll('.inline-flex');
      expect(badges).toHaveLength(3);
    });
  });

  describe('Data Attributes', () => {
    it('should pass through data attributes', () => {
      render(
        <Badge data-testid="test-badge" data-value="123">
          Data Badge
        </Badge>
      );
      const badge = screen.getByTestId('test-badge');
      expect(badge).toHaveAttribute('data-value', '123');
    });

    it('should support custom data attributes for testing', () => {
      render(
        <Badge data-state="active" data-variant="custom">
          Custom Data
        </Badge>
      );
      const badge = screen.getByText('Custom Data');
      expect(badge).toHaveAttribute('data-state', 'active');
      expect(badge).toHaveAttribute('data-variant', 'custom');
    });
  });

  describe('Visual States', () => {
    it('should apply custom colors via inline styles', () => {
      render(
        <Badge style={{ backgroundColor: '#ff0000', color: '#ffffff' }}>
          Custom Color
        </Badge>
      );
      const badge = screen.getByText('Custom Color');
      expect(badge).toHaveStyle({ backgroundColor: '#ff0000' });
      expect(badge).toHaveStyle({ color: '#ffffff' });
    });

    it('should handle CSS-in-JS styling', () => {
      const customStyle = { opacity: '0.8', transform: 'scale(1.1)' };
      render(<Badge style={customStyle}>Styled Badge</Badge>);
      const badge = screen.getByText('Styled Badge');
      expect(badge).toHaveStyle({ opacity: '0.8' });
    });
  });
});
