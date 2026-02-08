import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

describe('Alert Components', () => {
  describe('Alert Component', () => {
    describe('Rendering', () => {
      it('should render default alert', () => {
        render(<Alert>Default alert message</Alert>);
        const alert = screen.getByText('Default alert message');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveClass('relative');
        expect(alert).toHaveClass('w-full');
        expect(alert).toHaveClass('rounded-lg');
      });

      it('should render with custom className', () => {
        render(<Alert className="custom-class">Custom alert</Alert>);
        const alert = screen.getByText('Custom alert');
        expect(alert).toHaveClass('custom-class');
      });

      it('should render children correctly', () => {
        render(
          <Alert>
            <span data-testid="child-span">Alert content</span>
          </Alert>
        );
        const child = screen.getByTestId('child-span');
        expect(child).toBeInTheDocument();
      });

      it('should render with icon', () => {
        render(
          <Alert>
            <svg data-testid="alert-icon" />
            Alert with icon
          </Alert>
        );
        const icon = screen.getByTestId('alert-icon');
        expect(icon).toBeInTheDocument();
      });
    });

    describe('Variant Styling', () => {
      it('should render default variant', () => {
        render(<Alert variant="default">Default</Alert>);
        const alert = screen.getByText('Default');
        expect(alert).toHaveClass('bg-background');
        expect(alert).toHaveClass('text-foreground');
      });

      it('should render destructive variant', () => {
        render(<Alert variant="destructive">Destructive</Alert>);
        const alert = screen.getByText('Destructive');
        expect(alert).toHaveClass('border-destructive');
        expect(alert).toHaveClass('text-destructive');
      });

      it('should render warning variant', () => {
        render(<Alert variant="warning">Warning</Alert>);
        const alert = screen.getByText('Warning');
        expect(alert).toHaveClass('border-yellow-500');
      });

      it('should render success variant', () => {
        render(<Alert variant="success">Success</Alert>);
        const alert = screen.getByText('Success');
        expect(alert).toHaveClass('border-green-500');
      });

      it('should render info variant', () => {
        render(<Alert variant="info">Info</Alert>);
        const alert = screen.getByText('Info');
        expect(alert).toHaveClass('border-blue-500');
      });
    });

    describe('Accessibility', () => {
      it('should have role="alert" by default', () => {
        render(<Alert>Important message</Alert>);
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
      });

      it('should pass through ARIA attributes', () => {
        render(
          <Alert aria-live="assertive" aria-atomic="true">
            Critical alert
          </Alert>
        );
        const alert = screen.getByRole('alert');
        expect(alert).toHaveAttribute('aria-live', 'assertive');
        expect(alert).toHaveAttribute('aria-atomic', 'true');
      });

      it('should be screen reader accessible', () => {
        render(<Alert>Screen reader message</Alert>);
        const alert = screen.getByRole('alert');
        expect(alert).toBeVisible();
      });
    });

    describe('Data Attributes', () => {
      it('should pass through data attributes', () => {
        render(
          <Alert data-testid="test-alert" data-type="notification">
            Alert with data
          </Alert>
        );
        const alert = screen.getByTestId('test-alert');
        expect(alert).toHaveAttribute('data-type', 'notification');
      });

      it('should support variant-specific data attributes', () => {
        render(<Alert data-variant="custom">Custom variant</Alert>);
        const alert = screen.getByText('Custom variant');
        expect(alert).toHaveAttribute('data-variant', 'custom');
      });
    });

    describe('Edge Cases', () => {
      it('should render with empty content', () => {
        const { container } = render(<Alert>{''}</Alert>);
        const alert = container.querySelector('[role="alert"]');
        expect(alert).toBeInTheDocument();
      });

      it('should render with special characters', () => {
        render(<Alert>Alert with &quot;quotes&quot; &amp; symbols</Alert>);
        const alert = screen.getByText(/quotes/);
        expect(alert).toBeInTheDocument();
      });

      it('should render with long text content', () => {
        const longText = 'This is a very long alert message that might wrap onto multiple lines';
        render(<Alert>{longText}</Alert>);
        const alert = screen.getByText(longText);
        expect(alert).toBeInTheDocument();
      });
    });

    describe('Dismissal Behavior', () => {
      it('should render with dismiss button when provided', () => {
        const handleDismiss = vi.fn();
        render(
          <Alert>
            Dismissible alert
            <button onClick={handleDismiss} aria-label="Dismiss">
              ×
            </button>
          </Alert>
        );
        const button = screen.getByRole('button', { name: 'Dismiss' });
        expect(button).toBeInTheDocument();
      });

      it('should handle dismissal click', async () => {
        const handleDismiss = vi.fn();
        render(
          <Alert>
            Dismissible alert
            <button onClick={handleDismiss} aria-label="Dismiss">
              ×
            </button>
          </Alert>
        );
        const button = screen.getByRole('button', { name: 'Dismiss' });
        await userEvent.click(button);
        expect(handleDismiss).toHaveBeenCalledTimes(1);
      });
    });

    describe('Composition Patterns', () => {
      it('should work with AlertTitle', () => {
        render(
          <Alert>
            <AlertTitle>Alert Title</AlertTitle>
            Alert content
          </Alert>
        );
        const title = screen.getByText('Alert Title');
        const content = screen.getByText('Alert content');
        expect(title).toBeInTheDocument();
        expect(content).toBeInTheDocument();
      });

      it('should work with AlertDescription', () => {
        render(
          <Alert>
            <AlertTitle>Title</AlertTitle>
            <AlertDescription>Description text</AlertDescription>
          </Alert>
        );
        const description = screen.getByText('Description text');
        expect(description).toBeInTheDocument();
      });

      it('should work with both title and description', () => {
        render(
          <Alert>
            <AlertTitle>Success!</AlertTitle>
            <AlertDescription>Your changes have been saved successfully.</AlertDescription>
          </Alert>
        );
        const title = screen.getByText('Success!');
        const description = screen.getByText(/changes have been saved/);
        expect(title).toBeInTheDocument();
        expect(description).toBeInTheDocument();
      });
    });

    describe('Visual States', () => {
      it('should apply custom styles via inline styles', () => {
        render(
          <Alert style={{ backgroundColor: '#ff0000', color: '#ffffff' }}>
            Custom styled alert
          </Alert>
        );
        const alert = screen.getByText('Custom styled alert');
        expect(alert).toHaveStyle({ backgroundColor: '#ff0000' });
        expect(alert).toHaveStyle({ color: '#ffffff' });
      });

      it('should handle CSS-in-JS styling', () => {
        const customStyle = { opacity: '0.9', transform: 'scale(1.02)' };
        render(<Alert style={customStyle}>Styled alert</Alert>);
        const alert = screen.getByText('Styled alert');
        expect(alert).toHaveStyle({ opacity: '0.9' });
      });
    });
  });

  describe('AlertTitle Component', () => {
    it('should render title with proper styling', () => {
      render(<AlertTitle>Alert Title</AlertTitle>);
      const title = screen.getByText('Alert Title');
      expect(title).toHaveClass('font-bold');
      expect(title).toHaveClass('mb-1');
    });

    it('should render with custom className', () => {
      render(<AlertTitle className="text-xl">Custom Title</AlertTitle>);
      const title = screen.getByText('Custom Title');
      expect(title).toHaveClass('text-xl');
    });

    it('should render heading level h5', () => {
      render(<AlertTitle>Heading Title</AlertTitle>);
      const title = screen.getByRole('heading', { level: 5 });
      expect(title).toBeInTheDocument();
    });
  });

  describe('AlertDescription Component', () => {
    it('should render description with proper styling', () => {
      render(<AlertDescription>Description text</AlertDescription>);
      const description = screen.getByText('Description text');
      expect(description).toHaveClass('text-sm');
      expect(description).toHaveClass('leading-relaxed');
    });

    it('should render with custom className', () => {
      render(<AlertDescription className="text-gray-600">Custom Description</AlertDescription>);
      const description = screen.getByText('Custom Description');
      expect(description).toHaveClass('text-gray-600');
    });

    it('should render as div by default', () => {
      render(<AlertDescription>Description</AlertDescription>);
      const description = screen.getByText('Description');
      expect(description.tagName).toBe('DIV');
    });

    it('should render HTML content', () => {
      render(
        <AlertDescription>
          Description with <strong>bold</strong> and <em>italic</em> text
        </AlertDescription>
      );
      const bold = screen.getByText('bold');
      const italic = screen.getByText('italic');
      expect(bold.tagName).toBe('STRONG');
      expect(italic.tagName).toBe('EM');
    });
  });

  describe('Complete Alert Examples', () => {
    it('should render a complete success alert', () => {
      render(
        <Alert variant="success">
          <AlertTitle>Success!</AlertTitle>
          <AlertDescription>Your operation completed successfully.</AlertDescription>
        </Alert>
      );
      const alert = screen.getByRole('alert');
      const title = screen.getByText('Success!');
      const description = screen.getByText(/operation completed/);
      expect(alert).toBeInTheDocument();
      expect(title).toBeInTheDocument();
      expect(description).toBeInTheDocument();
    });

    it('should render a complete error alert', () => {
      render(
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>Something went wrong. Please try again.</AlertDescription>
        </Alert>
      );
      const alert = screen.getByRole('alert');
      const title = screen.getByText('Error');
      const description = screen.getByText(/something went wrong/i);
      expect(alert).toBeInTheDocument();
      expect(title).toBeInTheDocument();
      expect(description).toBeInTheDocument();
    });

    it('should render a warning alert with icon', () => {
      render(
        <Alert variant="warning">
          <svg data-testid="warning-icon">!</svg>
          <AlertTitle>Warning</AlertTitle>
          <AlertDescription>Your session is about to expire.</AlertDescription>
        </Alert>
      );
      const icon = screen.getByTestId('warning-icon');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Multiple Alerts', () => {
    it('should render multiple alerts independently', () => {
      render(
        <>
          <Alert variant="success">First alert</Alert>
          <Alert variant="error">Second alert</Alert>
          <Alert variant="warning">Third alert</Alert>
        </>
      );
      const alerts = screen.getAllByRole('alert');
      expect(alerts).toHaveLength(3);
      expect(alerts[0]).toHaveTextContent('First alert');
      expect(alerts[1]).toHaveTextContent('Second alert');
      expect(alerts[2]).toHaveTextContent('Third alert');
    });
  });

  describe('Interactive Elements', () => {
    it('should contain interactive elements like links', () => {
      render(
        <Alert>
          Alert with <a href="/docs">link</a>
        </Alert>
      );
      const link = screen.getByRole('link', { name: 'link' });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', '/docs');
    });

    it('should contain buttons', () => {
      const handleClick = vi.fn();
      render(
        <Alert>
          Alert with action
          <button onClick={handleClick}>Learn more</button>
        </Alert>
      );
      const button = screen.getByRole('button', { name: 'Learn more' });
      expect(button).toBeInTheDocument();
    });
  });
});
