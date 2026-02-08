import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/components/ui/button';

/**
 * Unit Tests for Button Component
 *
 * Test Coverage:
 * - Variant rendering (default, destructive, outline, secondary, ghost, link, danger)
 * - Size variants (default, sm, lg, icon)
 * - Click handlers
 * - Disabled state
 * - asChild prop behavior
 * - Custom className merging
 * - Accessibility attributes
 */

describe('Button Component', () => {
  describe('Variant Rendering', () => {
    it('should render default variant', () => {
      render(<Button>Default Button</Button>);
      const button = screen.getByRole('button', { name: 'Default Button' });

      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('bg-primary');
      expect(button).toHaveClass('text-primary-foreground');
    });

    it('should render destructive variant', () => {
      render(<Button variant="destructive">Destructive</Button>);
      const button = screen.getByRole('button', { name: 'Destructive' });

      expect(button).toHaveClass('bg-destructive');
      expect(button).toHaveClass('text-destructive-foreground');
    });

    it('should render danger variant', () => {
      render(<Button variant="danger">Danger</Button>);
      const button = screen.getByRole('button', { name: 'Danger' });

      expect(button).toHaveClass('bg-destructive');
      expect(button).toHaveClass('text-destructive-foreground');
    });

    it('should render outline variant', () => {
      render(<Button variant="outline">Outline</Button>);
      const button = screen.getByRole('button', { name: 'Outline' });

      expect(button).toHaveClass('border');
      expect(button).toHaveClass('border-input');
    });

    it('should render secondary variant', () => {
      render(<Button variant="secondary">Secondary</Button>);
      const button = screen.getByRole('button', { name: 'Secondary' });

      expect(button).toHaveClass('bg-secondary');
      expect(button).toHaveClass('text-secondary-foreground');
    });

    it('should render ghost variant', () => {
      render(<Button variant="ghost">Ghost</Button>);
      const button = screen.getByRole('button', { name: 'Ghost' });

      expect(button).toHaveClass('hover:bg-accent');
    });

    it('should render link variant', () => {
      render(<Button variant="link">Link</Button>);
      const button = screen.getByRole('button', { name: 'Link' });

      expect(button).toHaveClass('text-primary');
      expect(button).toHaveClass('underline-offset-4');
      expect(button).toHaveClass('hover:underline');
    });
  });

  describe('Size Variants', () => {
    it('should render default size', () => {
      render(<Button size="default">Default Size</Button>);
      const button = screen.getByRole('button', { name: 'Default Size' });

      expect(button).toHaveClass('h-9');
      expect(button).toHaveClass('px-4');
    });

    it('should render small size', () => {
      render(<Button size="sm">Small</Button>);
      const button = screen.getByRole('button', { name: 'Small' });

      expect(button).toHaveClass('h-8');
      expect(button).toHaveClass('text-xs');
    });

    it('should render large size', () => {
      render(<Button size="lg">Large</Button>);
      const button = screen.getByRole('button', { name: 'Large' });

      expect(button).toHaveClass('h-10');
      expect(button).toHaveClass('px-8');
    });

    it('should render icon size', () => {
      render(<Button size="icon"><span>Icon</span></Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveClass('h-9');
      expect(button).toHaveClass('w-9');
    });
  });

  describe('Click Handlers', () => {
    it('should call onClick handler when clicked', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Click me</Button>);

      const button = screen.getByRole('button', { name: 'Click me' });
      await user.click(button);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not call onClick when disabled', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(
        <Button onClick={handleClick} disabled>
          Disabled
        </Button>
      );

      const button = screen.getByRole('button', { name: 'Disabled' });
      await user.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should handle multiple clicks', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Multi-click</Button>);

      const button = screen.getByRole('button', { name: 'Multi-click' });
      await user.tripleClick(button);

      expect(handleClick).toHaveBeenCalledTimes(3);
    });
  });

  describe('Disabled State', () => {
    it('should render disabled button', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button', { name: 'Disabled' });

      expect(button).toBeDisabled();
      expect(button).toHaveClass('disabled:opacity-50');
      expect(button).toHaveClass('disabled:pointer-events-none');
    });

    it('should have disabled attribute', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button', { name: 'Disabled' });

      expect(button).toHaveAttribute('disabled');
    });
  });

  describe('asChild Prop', () => {
    it('should render as child component when asChild is true', () => {
      render(
        <Button asChild>
          <a href="/test">Link Button</a>
        </Button>
      );

      const link = screen.getByRole('link', { name: 'Link Button' });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', '/test');
      // Should have button styling classes
      expect(link).toHaveClass('inline-flex');
    });

    it('should render as button when asChild is false or undefined', () => {
      render(<Button asChild={false}>Regular Button</Button>);
      const button = screen.getByRole('button', { name: 'Regular Button' });

      expect(button).toBeInTheDocument();
      expect(button.tagName).toBe('BUTTON');
    });
  });

  describe('Custom className', () => {
    it('should merge custom className with variant classes', () => {
      render(<Button className="custom-class">Custom</Button>);
      const button = screen.getByRole('button', { name: 'Custom' });

      expect(button).toHaveClass('custom-class');
      expect(button).toHaveClass('bg-primary'); // default variant class
    });

    it('should handle multiple custom classes', () => {
      render(<Button className="class1 class2">Multiple</Button>);
      const button = screen.getByRole('button', { name: 'Multiple' });

      expect(button).toHaveClass('class1');
      expect(button).toHaveClass('class2');
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Accessible</Button>);

      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should support ARIA attributes', () => {
      render(
        <Button aria-label="Close dialog" aria-describedby="description">
          Close
        </Button>
      );

      const button = screen.getByRole('button', { name: 'Close dialog' });
      expect(button).toHaveAttribute('aria-label', 'Close dialog');
      expect(button).toHaveAttribute('aria-describedby', 'description');
    });

    it('should support disabled ARIA state', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('HTML Button Attributes', () => {
    it('should pass through type attribute', () => {
      render(<Button type="submit">Submit</Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveAttribute('type', 'submit');
    });

    it('should pass through form attributes', () => {
      render(
        <Button form="my-form" formAction="/submit">
          Submit
        </Button>
      );
      const button = screen.getByRole('button');

      expect(button).toHaveAttribute('form', 'my-form');
      expect(button).toHaveAttribute('formAction', '/submit');
    });

    it('should pass through data attributes', () => {
      render(<Button data-testid="test-button">Test</Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveAttribute('data-testid', 'test-button');
    });
  });

  describe('Children Rendering', () => {
    it('should render text children', () => {
      render(<Button>Text Content</Button>);
      expect(screen.getByText('Text Content')).toBeInTheDocument();
    });

    it('should render icon with text', () => {
      render(
        <Button>
          <span data-testid="icon">→</span>
          Continue
        </Button>
      );

      expect(screen.getByText('Continue')).toBeInTheDocument();
      expect(screen.getByTestId('icon')).toBeInTheDocument();
    });

    it('should render complex children', () => {
      render(
        <Button>
          <strong>Bold</strong> and <em>italic</em>
        </Button>
      );

      expect(screen.getByText('Bold')).toBeInTheDocument();
      expect(screen.getByText('italic')).toBeInTheDocument();
    });
  });

  describe('Focus and Active States', () => {
    it('should apply focus-visible classes', () => {
      render(<Button>Focus Test</Button>);
      const button = screen.getByRole('button');

      // Check that focus-visible classes are present
      expect(button).toHaveClass('focus-visible:outline-none');
      expect(button).toHaveClass('focus-visible:ring-1');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Button></Button>);
      const button = screen.getByRole('button');

      expect(button).toBeInTheDocument();
      expect(button).toBeEmptyDOMElement();
    });

    it('should handle null children gracefully', () => {
      render(<Button>{null}</Button>);
      const button = screen.getByRole('button');

      expect(button).toBeInTheDocument();
    });

    it('should handle boolean children', () => {
      render(<Button>{true}</Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveTextContent('true');
    });
  });
});
