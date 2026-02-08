import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '@/components/ui/input';

/**
 * Unit Tests for Input Component
 *
 * Test Coverage:
 * - Rendering different input types
 * - Value changes and onChange handlers
 * - Placeholder text
 * - Disabled state
 * - Custom className
 * - Focus states
 * - Accessibility attributes
 * - File input styling
 */

describe('Input Component', () => {
  describe('Rendering', () => {
    it('should render text input by default', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');

      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
    });

    it('should render with custom type', () => {
      render(<Input type="email" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('type', 'email');
    });

    it('should render password input', () => {
      render(<Input type="password" />);
      const input = screen.getByLabelText(/password/i) || screen.getByRole('textbox');

      expect(input).toHaveAttribute('type', 'password');
    });

    it('should render number input', () => {
      render(<Input type="number" />);
      const input = screen.getByRole('spinbutton');

      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'number');
    });

    it('should render file input', () => {
      render(<Input type="file" />);
      const input = screen.getByRole('textbox') || screen.getByLabelText(/file/i);

      expect(input).toBeInTheDocument();
    });

    it('should render search input', () => {
      render(<Input type="search" />);
      const input = screen.getByRole('searchbox');

      expect(input).toBeInTheDocument();
    });

    it('should render tel input', () => {
      render(<Input type="tel" />);
      const input = screen.getByRole('textbox');

      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'tel');
    });

    it('should render url input', () => {
      render(<Input type="url" />);
      const input = screen.getByRole('textbox');

      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'url');
    });
  });

  describe('Value and onChange', () => {
    it('should render with initial value', () => {
      render(<Input value="initial value" />);
      const input = screen.getByDisplayValue('initial value');

      expect(input).toBeInTheDocument();
    });

    it('should call onChange when value changes', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();

      render(<Input onChange={handleChange} />);

      const input = screen.getByRole('textbox');
      await user.type(input, 'test');

      expect(handleChange).toHaveBeenCalled();
    });

    it('should not update value when controlled', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();

      render(<Input value="fixed" onChange={handleChange} />);

      const input = screen.getByDisplayValue('fixed');
      await user.clear(input);
      await user.type(input, 'new value');

      // In controlled mode, value stays as prop
      expect(screen.getByDisplayValue('fixed')).toBeInTheDocument();
      expect(handleChange).toHaveBeenCalled();
    });

    it('should update value when uncontrolled', async () => {
      const user = userEvent.setup();

      render(<Input defaultValue="initial" />);

      const input = screen.getByDisplayValue('initial');
      await user.clear(input);
      await user.type(input, 'updated');

      expect(screen.getByDisplayValue('updated')).toBeInTheDocument();
    });
  });

  describe('Placeholder', () => {
    it('should render placeholder text', () => {
      render(<Input placeholder="Enter your name" />);
      const input = screen.getByPlaceholderText('Enter your name');

      expect(input).toBeInTheDocument();
    });

    it('should have placeholder styling', () => {
      render(<Input placeholder="Placeholder text" />);
      const input = screen.getByPlaceholderText('Placeholder text');

      expect(input).toHaveClass('placeholder:text-muted-foreground');
    });
  });

  describe('Disabled State', () => {
    it('should render disabled input', () => {
      render(<Input disabled />);
      const input = screen.getByRole('textbox');

      expect(input).toBeDisabled();
    });

    it('should have disabled styling', () => {
      render(<Input disabled />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveClass('disabled:cursor-not-allowed');
      expect(input).toHaveClass('disabled:opacity-50');
    });

    it('should not be interactive when disabled', async () => {
      const user = userEvent.setup();
      const handleChange = vi.fn();

      render(<Input disabled onChange={handleChange} />);

      const input = screen.getByRole('textbox');
      await user.click(input);

      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Custom className', () => {
    it('should merge custom className with default classes', () => {
      render(<Input className="custom-class" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveClass('custom-class');
      expect(input).toHaveClass('flex');
      expect(input).toHaveClass('h-9');
    });

    it('should handle multiple custom classes', () => {
      render(<Input className="class1 class2" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveClass('class1');
      expect(input).toHaveClass('class2');
    });
  });

  describe('Focus States', () => {
    it('should apply focus-visible classes', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveClass('focus-visible:outline-none');
      expect(input).toHaveClass('focus-visible:ring-1');
      expect(input).toHaveClass('focus-visible:ring-ring');
    });

    it('should be focusable', async () => {
      const user = userEvent.setup();
      render(<Input />);

      const input = screen.getByRole('textbox');
      await user.click(input);

      expect(input).toHaveFocus();
    });
  });

  describe('Accessibility', () => {
    it('should support ARIA attributes', () => {
      render(
        <Input
          aria-label="Email address"
          aria-describedby="email-desc"
          aria-invalid="false"
        />
      );

      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-label', 'Email address');
      expect(input).toHaveAttribute('aria-describedby', 'email-desc');
      expect(input).toHaveAttribute('aria-invalid', 'false');
    });

    it('should support required attribute', () => {
      render(<Input required />);
      const input = screen.getByRole('textbox');

      expect(input).toBeRequired();
    });

    it('should support readonly attribute', () => {
      render(<Input readOnly />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('readonly');
    });

    it('should support autocomplete attribute', () => {
      render(<Input autoComplete="email" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('autocomplete', 'email');
    });
  });

  describe('HTML Input Attributes', () => {
    it('should support name attribute', () => {
      render(<Input name="username" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('name', 'username');
    });

    it('should support id attribute', () => {
      render(<Input id="input-id" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('id', 'input-id');
    });

    it('should support min and max for number inputs', () => {
      render(<Input type="number" min="0" max="100" />);
      const input = screen.getByRole('spinbutton');

      expect(input).toHaveAttribute('min', '0');
      expect(input).toHaveAttribute('max', '100');
    });

    it('should support step attribute for number inputs', () => {
      render(<Input type="number" step="0.01" />);
      const input = screen.getByRole('spinbutton');

      expect(input).toHaveAttribute('step', '0.01');
    });

    it('should support minLength and maxLength', () => {
      render(<Input minLength={3} maxLength={10} />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('minlength', '3');
      expect(input).toHaveAttribute('maxlength', '10');
    });

    it('should support pattern attribute', () => {
      render(<Input pattern="[0-9]*" />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveAttribute('pattern', '[0-9]*');
    });
  });

  describe('File Input Styling', () => {
    it('should apply file-specific classes', () => {
      render(<Input type="file" />);
      const input = screen.getByRole('textbox') || screen.getByLabelText(/file/i);

      expect(input).toHaveClass('file:border-0');
      expect(input).toHaveClass('file:bg-transparent');
      expect(input).toHaveClass('file:text-sm');
    });
  });

  describe('Responsive Design', () => {
    it('should have responsive text size classes', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');

      expect(input).toHaveClass('text-base');
      expect(input).toHaveClass('md:text-sm');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string value', () => {
      render(<Input value="" />);
      const input = screen.getByRole('textbox');

      expect(input).toBeInTheDocument();
      expect(input).toHaveValue('');
    });

    it('should handle null/undefined value gracefully', () => {
      render(<Input value={undefined} />);
      const input = screen.getByRole('textbox');

      expect(input).toBeInTheDocument();
    });

    it('should handle very long values', async () => {
      const user = userEvent.setup();
      const longValue = 'a'.repeat(1000);

      render(<Input />);

      const input = screen.getByRole('textbox');
      await user.type(input, longValue);

      expect(input).toHaveValue(longValue);
    });

    it('should handle special characters', async () => {
      const user = userEvent.setup();
      const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';

      render(<Input />);

      const input = screen.getByRole('textbox');
      await user.type(input, specialChars);

      expect(input).toHaveValue(specialChars);
    });
  });

  describe('Ref Forwarding', () => {
    it('should forward ref to input element', () => {
      let ref: HTMLInputElement | null = null;

      const TestComponent = () => {
        const inputRef = React.useRef<HTMLInputElement>(null);
        React.useEffect(() => {
          ref = inputRef.current;
        }, []);
        return <Input ref={inputRef} />;
      };

      render(<TestComponent />);

      expect(ref).toBeInstanceOf(HTMLInputElement);
    });
  });
});
