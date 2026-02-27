import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Checkbox } from '@/components/ui/checkbox';

describe('Checkbox Component', () => {
  describe('Rendering', () => {
    it('should render unchecked checkbox by default', () => {
      render(<Checkbox />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
      expect(checkbox).not.toBeChecked();
    });

    it('should render checked checkbox when checked prop is true', () => {
      render(<Checkbox checked={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeChecked();
    });

    it('should render indeterminate checkbox when indeterminate prop is true', () => {
      render(<Checkbox checked={false} indeterminate={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'indeterminate');
    });

    it('should render disabled checkbox when disabled prop is true', () => {
      render(<Checkbox disabled />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeDisabled();
    });

    it('should render with custom className', () => {
      render(<Checkbox className="custom-class" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveClass('custom-class');
    });

    it('should render with custom id', () => {
      render(<Checkbox id="custom-id" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('id', 'custom-id');
    });
  });

  describe('User Interaction', () => {
    it('should toggle from unchecked to checked on click', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should toggle from checked to unchecked on click', () => {
      const handleChange = vi.fn();
      render(<Checkbox checked={true} onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);

      expect(handleChange).toHaveBeenCalledWith(false);
    });

    it('should not toggle when disabled', () => {
      const handleChange = vi.fn();
      render(<Checkbox disabled onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);

      expect(handleChange).not.toHaveBeenCalled();
    });

    it('should handle multiple clicks', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);
      fireEvent.click(checkbox);
      fireEvent.click(checkbox);

      expect(handleChange).toHaveBeenCalledTimes(3);
    });
  });

  describe('Keyboard Interaction', () => {
    it('should toggle on Space key press', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      checkbox.focus();
      fireEvent.keyDown(checkbox, { key: ' ' });

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should not respond to Enter key press', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      checkbox.focus();
      fireEvent.keyDown(checkbox, { key: 'Enter' });

      expect(handleChange).not.toHaveBeenCalled();
    });

    it('should not respond to letter keys', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      checkbox.focus();
      fireEvent.keyDown(checkbox, { key: 'a' });

      expect(handleChange).not.toHaveBeenCalled();
    });
  });

  describe('Controlled Component', () => {
    it('should respect controlled checked state', () => {
      const { rerender } = render(<Checkbox checked={false} />);
      const checkbox = screen.getByRole('checkbox');

      expect(checkbox).not.toBeChecked();

      rerender(<Checkbox checked={true} />);
      expect(checkbox).toBeChecked();
    });

    it('should call onCheckedChange but not update state in controlled mode', () => {
      const handleChange = vi.fn();
      const { rerender } = render(<Checkbox checked={false} onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);

      expect(handleChange).toHaveBeenCalledWith(true);
      expect(checkbox).not.toBeChecked();

      rerender(<Checkbox checked={true} onCheckedChange={handleChange} />);
      expect(checkbox).toBeChecked();
    });
  });

  describe('Indeterminate State', () => {
    it('should show indeterminate state visually', () => {
      render(<Checkbox indeterminate={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'indeterminate');
    });

    it('should respect indeterminate over checked when both are true', () => {
      render(<Checkbox checked={true} indeterminate={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'indeterminate');
    });

    it('should clear indeterminate state when clicked', () => {
      const handleChange = vi.fn();
      render(<Checkbox indeterminate={true} onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);

      expect(handleChange).toHaveBeenCalledWith(true);
    });
  });

  describe('Accessibility', () => {
    it('should have role="checkbox"', () => {
      render(<Checkbox />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeInTheDocument();
    });

    it('should have aria-checked="false" when unchecked', () => {
      render(<Checkbox />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-checked', 'false');
    });

    it('should have aria-checked="true" when checked', () => {
      render(<Checkbox checked={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-checked', 'true');
    });

    it('should have aria-checked="mixed" when indeterminate', () => {
      render(<Checkbox indeterminate={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('aria-checked', 'mixed');
    });

    it('should pass through additional ARIA attributes', () => {
      render(
        <Checkbox aria-label="Accept terms" aria-describedby="terms-desc" />
      );
      const checkbox = screen.getByRole('checkbox', { name: 'Accept terms' });
      expect(checkbox).toHaveAttribute('aria-describedby', 'terms-desc');
    });

    it('should be focusable', () => {
      render(<Checkbox />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('tabIndex', '0');
    });

    it('should not be focusable when disabled', () => {
      render(<Checkbox disabled />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-disabled');
    });
  });

  describe('Form Integration', () => {
    it('should work with form labels', () => {
      render(
        <label>
          I agree to terms
          <Checkbox />
        </label>
      );
      const checkbox = screen.getByRole('checkbox');
      const label = screen.getByLabelText('I agree to terms');
      expect(label).toContainElement(checkbox);
    });

    it('should associate with external label using htmlFor', () => {
      render(
        <>
          <label htmlFor="agree-checkbox">I accept</label>
          <Checkbox id="agree-checkbox" />
        </>
      );
      const checkbox = screen.getByRole('checkbox', { name: 'I accept' });
      expect(checkbox).toBeInTheDocument();
    });

    it('should work with native form validation', () => {
      render(
        <form>
          <Checkbox required name="terms" />
        </form>
      );
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeRequired();
    });
  });

  describe('Data Attributes', () => {
    it('should pass through data attributes', () => {
      render(
        <Checkbox data-testid="test-checkbox" data-feature="remember-me">
          Checkbox
        </Checkbox>
      );
      const checkbox = screen.getByTestId('test-checkbox');
      expect(checkbox).toHaveAttribute('data-feature', 'remember-me');
    });

    it('should support state-specific data attributes', () => {
      render(<Checkbox data-state="checked" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'checked');
    });
  });

  describe('Visual States', () => {
    it('should apply checked styles when checked', () => {
      render(<Checkbox checked={true} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'checked');
    });

    it('should apply unchecked styles when unchecked', () => {
      render(<Checkbox checked={false} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-state', 'unchecked');
    });

    it('should apply disabled styles', () => {
      render(<Checkbox disabled />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('data-disabled');
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicks without errors', () => {
      const handleChange = vi.fn();
      render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      for (let i = 0; i < 10; i++) {
        fireEvent.click(checkbox);
      }

      expect(handleChange).toHaveBeenCalledTimes(10);
    });

    it('should handle being unmounted while changing', () => {
      const handleChange = vi.fn();
      const { unmount } = render(<Checkbox onCheckedChange={handleChange} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.click(checkbox);
      unmount();

      expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('should handle null/undefined onCheckedChange', () => {
      expect(() => {
        render(<Checkbox onCheckedChange={undefined as any} />);
        const checkbox = screen.getByRole('checkbox');
        fireEvent.click(checkbox);
      }).not.toThrow();
    });
  });

  describe('Name and Value Attributes', () => {
    it('should pass name attribute', () => {
      render(<Checkbox name="remember" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('name', 'remember');
    });

    it('should pass value attribute', () => {
      render(<Checkbox value="yes" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('value', 'yes');
    });

    it('should pass both name and value attributes', () => {
      render(<Checkbox name="subscription" value="newsletter" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('name', 'subscription');
      expect(checkbox).toHaveAttribute('value', 'newsletter');
    });
  });

  describe('Ref Support', () => {
    it('should forward ref correctly', () => {
      const ref = { current: null };
      render(<Checkbox ref={ref} />);
      expect(ref.current).toBeTruthy();
      expect(ref.current).toHaveAttribute('role', 'checkbox');
    });
  });

  describe('Styling and Theming', () => {
    it('should apply custom styles via className', () => {
      render(<Checkbox className="border-red-500" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveClass('border-red-500');
    });

    it('should merge multiple classNames correctly', () => {
      render(<Checkbox className="class1 class2" />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveClass('class1');
      expect(checkbox).toHaveClass('class2');
    });
  });

  describe('Mouse Interaction', () => {
    it('should handle mouse enter', () => {
      const handleMouseEnter = vi.fn();
      render(<Checkbox onMouseEnter={handleMouseEnter} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.mouseEnter(checkbox);

      expect(handleMouseEnter).toHaveBeenCalledTimes(1);
    });

    it('should handle mouse leave', () => {
      const handleMouseLeave = vi.fn();
      render(<Checkbox onMouseLeave={handleMouseLeave} />);
      const checkbox = screen.getByRole('checkbox');

      fireEvent.mouseLeave(checkbox);

      expect(handleMouseLeave).toHaveBeenCalledTimes(1);
    });
  });
});
