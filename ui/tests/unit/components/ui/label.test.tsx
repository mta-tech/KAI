import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Label } from '@/components/ui/label';

describe('Label Component', () => {
  describe('Rendering', () => {
    it('should render default label', () => {
      render(<Label>Default Label</Label>);
      const label = screen.getByText('Default Label');
      expect(label).toBeInTheDocument();
      expect(label.tagName).toBe('LABEL');
    });

    it('should render with custom className', () => {
      render(<Label className="custom-class">Custom Label</Label>);
      const label = screen.getByText('Custom Label');
      expect(label).toHaveClass('custom-class');
    });

    it('should render children correctly', () => {
      render(
        <Label>
          <span data-testid="child-span">Label with span</span>
        </Label>
      );
      const child = screen.getByTestId('child-span');
      expect(child).toBeInTheDocument();
    });

    it('should render with icon', () => {
      render(
        <Label>
          <svg data-testid="test-icon" />
          Label with Icon
        </Label>
      );
      const icon = screen.getByTestId('test-icon');
      expect(icon).toBeInTheDocument();
    });

    it('should render with HTML content', () => {
      render(<Label>Label with <strong>bold</strong> text</Label>);
      const boldText = screen.getByText('bold');
      expect(boldText).toBeInTheDocument();
      expect(boldText.tagName).toBe('STRONG');
    });
  });

  describe('Accessibility', () => {
    it('should have htmlFor attribute when provided', () => {
      render(<Label htmlFor="input-id">For Input</Label>);
      const label = screen.getByText('For Input');
      expect(label).toHaveAttribute('for', 'input-id');
    });

    it('should associate with form control via htmlFor', () => {
      render(
        <>
          <Label htmlFor="test-input">Test Label</Label>
          <input id="test-input" type="text" />
        </>
      );
      const input = screen.getByRole('textbox', { name: 'Test Label' });
      expect(input).toBeInTheDocument();
    });

    it('should associate with nested form control', () => {
      render(
        <Label>
          Nested Label
          <input type="text" />
        </Label>
      );
      const input = screen.getByRole('textbox', { name: 'Nested Label' });
      expect(input).toBeInTheDocument();
    });

    it('should pass through ARIA attributes', () => {
      render(
        <Label aria-required="true" aria-describedby="help-text">
          Required Field
        </Label>
      );
      const label = screen.getByText('Required Field');
      expect(label).toHaveAttribute('aria-required', 'true');
      expect(label).toHaveAttribute('aria-describedby', 'help-text');
    });
  });

  describe('Styling', () => {
    it('should apply default label styling', () => {
      render(<Label>Styled Label</Label>);
      const label = screen.getByText('Styled Label');
      expect(label).toHaveClass('text-sm');
      expect(label).toHaveClass('font-medium');
      expect(label).toHaveClass('leading-none');
    });

    it('should apply peer-disabled styles when parent is disabled', () => {
      const { container } = render(
        <div className="disabled">
          <Label>Disabled Label</Label>
        </div>
      );
      const label = screen.getByText('Disabled Label');
      expect(label).toBeInTheDocument();
    });

    it('should handle inline styles', () => {
      render(
        <Label style={{ color: 'red', fontSize: '16px' }}>
          Inline Styled
        </Label>
      );
      const label = screen.getByText('Inline Styled');
      expect(label).toHaveStyle({ color: 'red', fontSize: '16px' });
    });
  });

  describe('Form Integration', () => {
    it('should work with input fields', () => {
      render(
        <>
          <Label htmlFor="username">Username</Label>
          <input id="username" type="text" />
        </>
      );
      const input = screen.getByRole('textbox', { name: 'Username' });
      expect(input).toHaveAttribute('id', 'username');
    });

    it('should work with checkbox', () => {
      render(
        <>
          <Label htmlFor="agree">I agree</Label>
          <input id="agree" type="checkbox" />
        </>
      );
      const checkbox = screen.getByRole('checkbox', { name: 'I agree' });
      expect(checkbox).toHaveAttribute('id', 'agree');
    });

    it('should work with select dropdown', () => {
      render(
        <>
          <Label htmlFor="country">Country</Label>
          <select id="country">
            <option>USA</option>
            <option>Canada</option>
          </select>
        </>
      );
      const select = screen.getByRole('combobox', { name: 'Country' });
      expect(select).toHaveAttribute('id', 'country');
    });

    it('should work with textarea', () => {
      render(
        <>
          <Label htmlFor="message">Message</Label>
          <textarea id="message" />
        </>
      );
      const textarea = screen.getByRole('textbox', { name: 'Message' });
      expect(textarea).toHaveAttribute('id', 'message');
    });
  });

  describe('Data Attributes', () => {
    it('should pass through data attributes', () => {
      render(
        <Label data-testid="test-label" data-field="email">
          Email Label
        </Label>
      );
      const label = screen.getByTestId('test-label');
      expect(label).toHaveAttribute('data-field', 'email');
    });

    it('should support custom data attributes', () => {
      render(
        <Label data-required="true" data-variant="floating">
          Custom Data
        </Label>
      );
      const label = screen.getByText('Custom Data');
      expect(label).toHaveAttribute('data-required', 'true');
      expect(label).toHaveAttribute('data-variant', 'floating');
    });
  });

  describe('Edge Cases', () => {
    it('should render with empty content', () => {
      const { container } = render(<Label>{''}</Label>);
      const label = container.querySelector('label');
      expect(label).toBeInTheDocument();
      expect(label).toBeEmptyDOMElement();
    });

    it('should render with whitespace content', () => {
      render(<Label>{'   '}</Label>);
      const label = screen.getByText('   ');
      expect(label).toBeInTheDocument();
    });

    it('should render with special characters', () => {
      render(<Label>Email &amp; Password (optional)</Label>);
      const label = screen.getByText(/Email & Password/);
      expect(label).toBeInTheDocument();
    });

    it('should render with very long text', () => {
      const longText = 'This is a very long label text that might wrap onto multiple lines';
      render(<Label>{longText}</Label>);
      const label = screen.getByText(longText);
      expect(label).toBeInTheDocument();
    });

    it('should render with number content', () => {
      render(<Label>{12345}</Label>);
      const label = screen.getByText('12345');
      expect(label).toBeInTheDocument();
    });
  });

  describe('Composition Patterns', () => {
    it('should work with required indicator', () => {
      render(
        <Label>
          Email
          <span className="text-red-500">*</span>
        </Label>
      );
      const label = screen.getByText('Email');
      const asterisk = screen.getByText('*');
      expect(label).toContainElement(asterisk);
    });

    it('should work with tooltip trigger', () => {
      render(
        <Label>
          Password
          <span data-testid="info-icon" aria-label="Password requirements">
            ℹ️
          </span>
        </Label>
      );
      const label = screen.getByText('Password');
      const icon = screen.getByTestId('info-icon');
      expect(label).toContainElement(icon);
    });

    it('should work in form groups', () => {
      const { container } = render(
        <div className="space-y-2">
          <Label htmlFor="field1">Field 1</Label>
          <input id="field1" type="text" />
          <Label htmlFor="field2">Field 2</Label>
          <input id="field2" type="text" />
        </div>
      );
      const labels = container.querySelectorAll('label');
      expect(labels).toHaveLength(2);
    });
  });

  describe('HTML Attributes', () => {
    it('should support id attribute', () => {
      render(<Label id="label-id">With ID</Label>);
      const label = screen.getByText('With ID');
      expect(label).toHaveAttribute('id', 'label-id');
    });

    it('should support title attribute for tooltip', () => {
      render(<Label title="This is a tooltip">Hover me</Label>);
      const label = screen.getByText('Hover me');
      expect(label).toHaveAttribute('title', 'This is a tooltip');
    });

    it('should support form attribute', () => {
      render(<Label form="form-id">Form Label</Label>);
      const label = screen.getByText('Form Label');
      expect(label).toHaveAttribute('form', 'form-id');
    });
  });

  describe('Click Behavior', () => {
    it('should focus associated input when clicked', () => {
      render(
        <>
          <Label htmlFor="click-input">Click to focus</Label>
          <input id="click-input" type="text" />
        </>
      );
      const label = screen.getByText('Click to focus');
      const input = screen.getByRole('textbox');

      label.click();

      expect(document.activeElement).toBe(input);
    });

    it('should toggle checkbox when clicked', () => {
      render(
        <>
          <Label htmlFor="click-checkbox">Click to toggle</Label>
          <input id="click-checkbox" type="checkbox" />
        </>
      );
      const label = screen.getByText('Click to toggle');
      const checkbox = screen.getByRole('checkbox');

      expect(checkbox).not.toBeChecked();
      label.click();
      expect(checkbox).toBeChecked();
      label.click();
      expect(checkbox).not.toBeChecked();
    });

    it('should focus radio button when clicked', () => {
      render(
        <>
          <Label htmlFor="click-radio">Click to select</Label>
          <input id="click-radio" type="radio" name="radio-group" />
        </>
      );
      const label = screen.getByText('Click to select');
      const radio = screen.getByRole('radio');

      expect(radio).not.toBeChecked();
      label.click();
      expect(radio).toBeChecked();
    });
  });

  describe('Multiple Labels', () => {
    it('should allow multiple labels for different inputs', () => {
      render(
        <>
          <Label htmlFor="field1">First Field</Label>
          <input id="field1" type="text" />
          <Label htmlFor="field2">Second Field</Label>
          <input id="field2" type="text" />
        </>
      );
      const label1 = screen.getByText('First Field');
      const label2 = screen.getByText('Second Field');
      const input1 = screen.getByRole('textbox', { name: 'First Field' });
      const input2 = screen.getByRole('textbox', { name: 'Second Field' });

      expect(label1).toHaveAttribute('for', 'field1');
      expect(label2).toHaveAttribute('for', 'field2');
      expect(input1).toHaveAttribute('id', 'field1');
      expect(input2).toHaveAttribute('id', 'field2');
    });
  });

  describe('CSS Classes', () => {
    it('should merge multiple classNames correctly', () => {
      render(<Label className="class1 class2 class3">Multiple Classes</Label>);
      const label = screen.getByText('Multiple Classes');
      expect(label).toHaveClass('class1');
      expect(label).toHaveClass('class2');
      expect(label).toHaveClass('class3');
    });

    it('should apply conditional className', () => {
      const condition = true;
      render(
        <Label className={condition ? 'condition-true' : 'condition-false'}>
          Conditional
        </Label>
      );
      const label = screen.getByText('Conditional');
      expect(label).toHaveClass('condition-true');
      expect(label).not.toHaveClass('condition-false');
    });
  });

  describe('Ref Support', () => {
    it('should forward ref correctly', () => {
      const ref = { current: null };
      render(<Label ref={ref}>With Ref</Label>);
      expect(ref.current).toBeTruthy();
      expect(ref.current.tagName).toBe('LABEL');
    });
  });

  describe('Accessibility Best Practices', () => {
    it('should have descriptive text for screen readers', () => {
      render(
        <>
          <Label htmlFor="accessible-input">Accessible Input Label</Label>
          <input id="accessible-input" aria-describedby="input-help" type="text" />
          <span id="input-help">This field accepts alphanumeric characters</span>
        </>
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAccessibleDescription('This field accepts alphanumeric characters');
    });

    it('should work with aria-labelledby', () => {
      render(
        <>
          <Label id="label1">Part 1</Label>
          <Label id="label2">Part 2</Label>
          <input aria-labelledby="label1 label2" type="text" />
        </>
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-labelledby', 'label1 label2');
    });
  });
});
