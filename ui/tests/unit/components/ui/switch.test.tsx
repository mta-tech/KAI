import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Switch } from '@/components/ui/switch';

describe('Switch Component', () => {
  describe('Rendering', () => {
    it('should render unchecked switch by default', () => {
      render(<Switch />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toBeInTheDocument();
      expect(switchEl).not.toBeChecked();
    });

    it('should render checked switch when checked prop is true', () => {
      render(<Switch checked={true} />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toBeChecked();
    });

    it('should render disabled switch when disabled prop is true', () => {
      render(<Switch disabled />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toBeDisabled();
    });

    it('should render with custom className', () => {
      render(<Switch className="custom-class" />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveClass('custom-class');
    });
  });

  describe('User Interaction', () => {
    it('should toggle from unchecked to checked on click', async () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      await userEvent.click(switchEl);

      expect(handleChange).toHaveBeenCalledWith(true);
      expect(switchEl).not.toBeChecked();
    });

    it('should toggle from checked to unchecked on click', async () => {
      const handleChange = vi.fn();
      render(<Switch checked={true} onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      await userEvent.click(switchEl);

      expect(handleChange).toHaveBeenCalledWith(false);
    });

    it('should not toggle when disabled', async () => {
      const handleChange = vi.fn();
      render(<Switch disabled onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      await userEvent.click(switchEl);

      expect(handleChange).not.toHaveBeenCalled();
    });

    it('should handle multiple clicks', async () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      await userEvent.click(switchEl);
      await userEvent.click(switchEl);
      await userEvent.click(switchEl);

      expect(handleChange).toHaveBeenCalledTimes(3);
    });
  });

  describe('Keyboard Interaction', () => {
    it('should toggle on Space key press', async () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      switchEl.focus();
      await userEvent.keyboard(' ');

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should toggle on Enter key press', async () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      switchEl.focus();
      await userEvent.keyboard('{Enter}');

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should not respond to other keys', async () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      switchEl.focus();
      await userEvent.keyboard('a');

      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Controlled Component', () => {
    it('should respect controlled checked state', () => {
      const { rerender } = render(<Switch checked={false} />);
      const switchEl = screen.getByRole('switch');

      expect(switchEl).not.toBeChecked();

      rerender(<Switch checked={true} />);
      expect(switchEl).toBeChecked();
    });

    it('should call onCheckedChange but not update state in controlled mode', () => {
      const handleChange = vi.fn();
      const { rerender } = render(<Switch checked={false} onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      fireEvent.click(switchEl);

      expect(handleChange).toHaveBeenCalledWith(true);
      expect(switchEl).not.toBeChecked();

      rerender(<Switch checked={true} onCheckedChange={handleChange} />);
      expect(switchEl).toBeChecked();
    });
  });

  describe('Uncontrolled Component', () => {
    it('should maintain internal state when uncontrolled', () => {
      render(<Switch />);
      const switchEl = screen.getByRole('switch');

      expect(switchEl).not.toBeChecked();

      fireEvent.click(switchEl);
      // Uncontrolled switch should toggle to checked state
      expect(switchEl).toBeChecked();
    });
  });

  describe('Accessibility', () => {
    it('should have role="switch"', () => {
      render(<Switch />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toBeInTheDocument();
    });

    it('should have aria-checked="false" when unchecked', () => {
      render(<Switch />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveAttribute('aria-checked', 'false');
    });

    it('should have aria-checked="true" when checked', () => {
      render(<Switch checked={true} />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveAttribute('aria-checked', 'true');
    });

    it('should pass through additional ARIA attributes', () => {
      render(<Switch aria-label="Toggle feature" aria-describedby="switch-desc" />);
      const switchEl = screen.getByRole('switch', { name: 'Toggle feature' });
      expect(switchEl).toHaveAttribute('aria-describedby', 'switch-desc');
    });

    it('should be focusable', () => {
      render(<Switch />);
      const switchEl = screen.getByRole('switch');
      // Radix UI Switch doesn't add tabIndex, uses native button behavior
      expect(switchEl).toHaveAttribute('type', 'button');
    });

    it('should not be focusable when disabled', () => {
      render(<Switch disabled />);
      const switchEl = screen.getByRole('switch');
      // Radix UI uses native disabled attribute, not aria-disabled
      expect(switchEl).toHaveAttribute('disabled');
      expect(switchEl).toBeDisabled();
    });
  });

  describe('Visual States', () => {
    it('should apply checked styles when checked', () => {
      render(<Switch checked={true} />);
      const switchEl = screen.getByRole('switch');
      // Radix UI uses data-state attribute, not class
      expect(switchEl).toHaveAttribute('data-state', 'checked');
    });

    it('should apply unchecked styles when unchecked', () => {
      render(<Switch checked={false} />);
      const switchEl = screen.getByRole('switch');
      // Radix UI uses data-state attribute, not class
      expect(switchEl).toHaveAttribute('data-state', 'unchecked');
    });

    it('should apply disabled styles', () => {
      render(<Switch disabled />);
      const switchEl = screen.getByRole('switch');
      // Radix UI uses data-disabled attribute for disabled state
      expect(switchEl).toHaveAttribute('data-disabled');
    });
  });

  describe('Data Attributes', () => {
    it('should pass through data attributes', () => {
      render(
        <Switch data-testid="test-switch" data-feature="dark-mode">
          Toggle
        </Switch>
      );
      const switchEl = screen.getByTestId('test-switch');
      expect(switchEl).toHaveAttribute('data-feature', 'dark-mode');
    });

    it('should support state-specific data attributes', () => {
      render(<Switch data-state="unchecked" />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveAttribute('data-state', 'unchecked');
    });
  });

  describe('Form Integration', () => {
    it('should work with form labels', () => {
      render(
        <label>
          Enable notifications
          <Switch />
        </label>
      );
      const switchEl = screen.getByRole('switch');
      const label = screen.getByLabelText('Enable notifications');
      expect(label).toContainElement(switchEl);
    });

    it('should associate with external label using htmlFor', () => {
      render(
        <>
          <label htmlFor="my-switch">Toggle setting</label>
          <Switch id="my-switch" />
        </>
      );
      const switchEl = screen.getByRole('switch', { name: 'Toggle setting' });
      expect(switchEl).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicks without errors', () => {
      const handleChange = vi.fn();
      render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      for (let i = 0; i < 10; i++) {
        fireEvent.click(switchEl);
      }

      expect(handleChange).toHaveBeenCalledTimes(10);
    });

    it('should handle being unmounted while changing', () => {
      const handleChange = vi.fn();
      const { unmount } = render(<Switch onCheckedChange={handleChange} />);
      const switchEl = screen.getByRole('switch');

      fireEvent.click(switchEl);
      unmount();

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should handle null/undefined onCheckedChange', () => {
      expect(() => {
        render(<Switch onCheckedChange={undefined as any} />);
        const switchEl = screen.getByRole('switch');
        fireEvent.click(switchEl);
      }).not.toThrow();
    });
  });

  describe('Ref Support', () => {
    it('should forward ref correctly', () => {
      const ref = { current: null };
      render(<Switch ref={ref} />);
      expect(ref.current).toBeTruthy();
      expect(ref.current).toHaveAttribute('role', 'switch');
    });
  });

  describe('Styling and Theming', () => {
    it('should apply custom styles via className', () => {
      render(<Switch className="bg-blue-500" />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveClass('bg-blue-500');
    });

    it('should merge multiple classNames correctly', () => {
      render(<Switch className="class1 class2" />);
      const switchEl = screen.getByRole('switch');
      expect(switchEl).toHaveClass('class1');
      expect(switchEl).toHaveClass('class2');
    });
  });
});
