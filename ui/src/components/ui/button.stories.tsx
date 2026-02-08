import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './button';

const meta = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'danger', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Button',
  },
};

export const Destructive: Story = {
  args: {
    variant: 'destructive',
    children: 'Destructive',
  },
};

export const Danger: Story = {
  args: {
    variant: 'danger',
    children: 'Danger',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Outline',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary',
  },
};

export const Ghost: Story = {
  args: {
    variant: 'ghost',
    children: 'Ghost',
  },
};

export const Link: Story = {
  args: {
    variant: 'link',
    children: 'Link',
  },
};

export const Small: Story = {
  args: {
    size: 'sm',
    children: 'Small',
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
    children: 'Large',
  },
};

export const Icon: Story = {
  args: {
    size: 'icon',
    children: '🔍',
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="danger">Danger</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
    </div>
  ),
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-2 items-center">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      <Button size="icon">🔍</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Available button sizes from small (32px) to large (40px). Icon buttons are square and designed for icon-only usage.',
      },
    },
  },
};

// Accessibility documentation
export const Accessibility: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <Button>Accessible Button</Button>
      <Button variant="outline">Secondary Action</Button>
      <Button variant="destructive">Destructive Action</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `## Accessibility

The Button component follows WCAG 2.1 AA guidelines:

### Keyboard Navigation
- \`Tab\` - Focus the next button
- \`Shift + Tab\` - Focus the previous button
- \`Enter\` or \`Space\` - Activate the button
- Focus indicator is always visible (2px outline ring)

### Screen Readers
- Uses native \`<button>\` element for proper semantics
- Button text is announced by screen readers
- Disabled state is communicated via \`disabled\` attribute

### Color Contrast
- Default variant: Meets 4.5:1 contrast ratio
- All text on buttons meets WCAG AA requirements
- Focus indicator has 3:1 contrast against background

### Best Practices
- Use clear, descriptive button text (avoid "Click Here")
- Don't rely on color alone to convey meaning
- Include icons to reinforce button actions
- Provide loading states for async actions
- Use \`danger\`/ \`destructive\` variants for irreversible actions`,
      },
    },
  },
};

// Design tokens reference
export const DesignTokens: Story = {
  render: () => <div className="hidden">Design tokens documentation only - see description tab</div>,
  parameters: {
    docs: {
      description: {
        story: `## Design Tokens

### Colors
| Token | Usage | Value |
|-------|-------|-------|
| \`--primary\` | Default button background | \`hsl(var(--primary))\` |
| \`--primary-foreground\` | Default button text | \`hsl(var(--primary-foreground))\` |
| \`--destructive\` | Destructive button background | \`hsl(var(--destructive))\` |
| \`--secondary\` | Secondary button background | \`hsl(var(--secondary))\` |
| \`--accent\` | Hover state background | \`hsl(var(--accent))\` |
| \`--ring\` | Focus ring color | \`hsl(var(--ring))\` |

### Spacing
| Size | Height | Padding |
|------|--------|---------|
| Small | 32px (\`h-8\`) | 12px (\`px-3\`) |
| Default | 36px (\`h-9\`) | 16px (\`px-4\`) |
| Large | 40px (\`h-10\`) | 32px (\`px-8\`) |
| Icon | 36px (\`h-9 w-9\`) | N/A |

### Typography
- Font size: \`text-sm\` (14px)
- Font weight: \`font-medium\` (500)
- Letter spacing: Normal

### Border Radius
- All sizes: \`rounded-md\` (6px)
- Consistent across all variants

### Transitions
- Duration: 150ms (transition-colors)
- Easing: ease-in-out
- Properties: color, background-color, border-color

### Focus States
- Outline: 2px solid
- Offset: 2px from button
- Color: \`--ring\` token`,
      },
    },
  },
};
