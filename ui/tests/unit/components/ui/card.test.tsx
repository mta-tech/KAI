import * as React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';

/**
 * Unit Tests for Card Components
 *
 * Test Coverage:
 * - Card component rendering
 * - CardHeader, CardContent, CardFooter
 * - CardTitle and CardDescription
 * - Custom className merging
 * - Composing card components
 * - Accessibility
 * - Ref forwarding
 */

describe('Card Components', () => {
  describe('Card Component', () => {
    it('should render card with default styling', () => {
      render(<Card>Card content</Card>);
      const card = screen.getByText('Card content');

      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('rounded-xl');
      expect(card).toHaveClass('border');
      expect(card).toHaveClass('bg-card');
      expect(card).toHaveClass('shadow');
    });

    it('should merge custom className', () => {
      render(<Card className="custom-class">Custom Card</Card>);
      const card = screen.getByText('Custom Card');

      expect(card).toHaveClass('custom-class');
      expect(card).toHaveClass('rounded-xl'); // default class preserved
    });

    it('should pass through other HTML attributes', () => {
      render(<Card data-testid="test-card">Test</Card>);
      const card = screen.getByTestId('test-card');

      expect(card).toBeInTheDocument();
    });

    it('should render complex children', () => {
      render(
        <Card>
          <h2>Title</h2>
          <p>Description</p>
          <button>Action</button>
        </Card>
      );

      expect(screen.getByText('Title')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Action')).toBeInTheDocument();
    });
  });

  describe('CardHeader Component', () => {
    it('should render header with default styling', () => {
      render(<CardHeader>Header content</CardHeader>);
      const header = screen.getByText('Header content');

      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('p-6');
      expect(header).toHaveClass('flex');
      expect(header).toHaveClass('flex-col');
      expect(header).toHaveClass('space-y-1.5');
    });

    it('should merge custom className', () => {
      render(<CardHeader className="custom-header">Header</CardHeader>);
      const header = screen.getByText('Header');

      expect(header).toHaveClass('custom-header');
      expect(header).toHaveClass('p-6'); // default preserved
    });
  });

  describe('CardTitle Component', () => {
    it('should render title with default styling', () => {
      render(<CardTitle>Card Title</CardTitle>);
      const title = screen.getByText('Card Title');

      expect(title).toBeInTheDocument();
      expect(title).toHaveClass('font-semibold');
      expect(title).toHaveClass('leading-none');
      expect(title).toHaveClass('tracking-tight');
    });

    it('should render as heading element semantically', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle asChild>
              <h1>Main Title</h1>
            </CardTitle>
          </CardHeader>
        </Card>
      );

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Main Title');
    });

    it('should merge custom className', () => {
      render(<CardTitle className="text-xl">Custom Title</CardTitle>);
      const title = screen.getByText('Custom Title');

      expect(title).toHaveClass('text-xl');
      expect(title).toHaveClass('font-semibold'); // default preserved
    });
  });

  describe('CardDescription Component', () => {
    it('should render description with default styling', () => {
      render(<CardDescription>Description text</CardDescription>);
      const description = screen.getByText('Description text');

      expect(description).toBeInTheDocument();
      expect(description).toHaveClass('text-sm');
      expect(description).toHaveClass('text-muted-foreground');
    });

    it('should merge custom className', () => {
      render(
        <CardDescription className="custom-desc">Description</CardDescription>
      );
      const description = screen.getByText('Description');

      expect(description).toHaveClass('custom-desc');
      expect(description).toHaveClass('text-sm'); // default preserved
    });
  });

  describe('CardContent Component', () => {
    it('should render content with default styling', () => {
      render(<CardContent>Content here</CardContent>);
      const content = screen.getByText('Content here');

      expect(content).toBeInTheDocument();
      expect(content).toHaveClass('p-6');
      expect(content).toHaveClass('pt-0');
    });

    it('should merge custom className', () => {
      render(<CardContent className="custom-content">Content</CardContent>);
      const content = screen.getByText('Content');

      expect(content).toHaveClass('custom-content');
      expect(content).toHaveClass('p-6'); // default preserved
    });
  });

  describe('CardFooter Component', () => {
    it('should render footer with default styling', () => {
      render(<CardFooter>Footer actions</CardFooter>);
      const footer = screen.getByText('Footer actions');

      expect(footer).toBeInTheDocument();
      expect(footer).toHaveClass('p-6');
      expect(footer).toHaveClass('pt-0');
      expect(footer).toHaveClass('flex');
      expect(footer).toHaveClass('items-center');
    });

    it('should merge custom className', () => {
      render(<CardFooter className="custom-footer">Footer</CardFooter>);
      const footer = screen.getByText('Footer');

      expect(footer).toHaveClass('custom-footer');
      expect(footer).toHaveClass('p-6'); // default preserved
    });

    it('should align footer items horizontally by default', () => {
      render(
        <CardFooter>
          <button>Cancel</button>
          <button>Confirm</button>
        </CardFooter>
      );

      const footer = screen.getByText('Footer actions').parentElement;
      expect(footer).toHaveClass('flex');
      expect(footer).toHaveClass('items-center');
    });
  });

  describe('Complete Card Composition', () => {
    it('should render a complete card with all components', () => {
      render(
        <Card data-testid="complete-card">
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Card content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Cancel</button>
            <button>Save</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Card description')).toBeInTheDocument();
      expect(screen.getByText('Card content goes here')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Save')).toBeInTheDocument();

      const card = screen.getByTestId('complete-card');
      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('rounded-xl');
    });

    it('should render card without optional components', () => {
      render(
        <Card>
          <CardContent>Just content</CardContent>
        </Card>
      );

      expect(screen.getByText('Just content')).toBeInTheDocument();
    });

    it('should render card with multiple content sections', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
          </CardHeader>
          <CardContent>
            <p>First content</p>
          </CardContent>
          <CardContent>
            <p>Second content</p>
          </CardContent>
        </Card>
      );

      expect(screen.getByText('First content')).toBeInTheDocument();
      expect(screen.getByText('Second content')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should support ARIA attributes on Card', () => {
      render(<Card role="article" aria-labelledby="card-title">Content</Card>);
      const card = screen.getByRole('article');

      expect(card).toHaveAttribute('aria-labelledby', 'card-title');
    });

    it('should support heading hierarchy in CardTitle', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle asChild>
              <h2 id="card-title">Main Heading</h2>
            </CardTitle>
            <CardDescription>Description</CardDescription>
          </CardHeader>
        </Card>
      );

      const heading = screen.getByRole('heading', { level: 2 });
      expect(heading).toHaveAttribute('id', 'card-title');
    });
  });

  describe('Ref Forwarding', () => {
    it('should forward ref for Card', () => {
      let ref: HTMLDivElement | null = null;

      const TestComponent = () => {
        const cardRef = React.useRef<HTMLDivElement>(null);
        React.useEffect(() => {
          ref = cardRef.current;
        }, []);
        return <Card ref={cardRef}>Content</Card>;
      };

      render(<TestComponent />);

      expect(ref).toBeInstanceOf(HTMLDivElement);
    });

    it('should forward ref for CardHeader', () => {
      let ref: HTMLDivElement | null = null;

      const TestComponent = () => {
        const headerRef = React.useRef<HTMLDivElement>(null);
        React.useEffect(() => {
          ref = headerRef.current;
        }, []);
        return <CardHeader ref={headerRef}>Header</CardHeader>;
      };

      render(<TestComponent />);

      expect(ref).toBeInstanceOf(HTMLDivElement);
    });

    it('should forward ref for CardTitle', () => {
      let ref: HTMLDivElement | null = null;

      const TestComponent = () => {
        const titleRef = React.useRef<HTMLDivElement>(null);
        React.useEffect(() => {
          ref = titleRef.current;
        }, []);
        return <CardTitle ref={titleRef}>Title</CardTitle>;
      };

      render(<TestComponent />);

      expect(ref).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty children gracefully', () => {
      render(<Card></Card>);
      const card = screen.getByRole('article') || document.querySelector('.rounded-xl');

      expect(card).toBeInTheDocument();
    });

    it('should handle null children', () => {
      render(<Card>{null}</Card>);
      const card = screen.getByRole('article') || document.querySelector('.rounded-xl');

      expect(card).toBeInTheDocument();
    });

    it('should handle deeply nested content', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
            <CardDescription>Description</CardDescription>
          </CardHeader>
          <CardContent>
            <div>
              <span>Nested content</span>
            </div>
          </CardContent>
        </Card>
      );

      expect(screen.getByText('Nested content')).toBeInTheDocument();
    });

    it('should handle boolean children', () => {
      render(
        <Card>
          <CardContent>{true}</CardContent>
        </Card>
      );

      const content = screen.getByText('true');
      expect(content).toBeInTheDocument();
    });
  });
});
