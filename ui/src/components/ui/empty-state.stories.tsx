import type { Meta, StoryObj } from '@storybook/react';
import { EmptyState } from './empty-state';
import { MessageSquare, Database, BookOpen } from 'lucide-react';
import { EmptyChatIllustration, EmptyKnowledgeIllustration, EmptyConnectionsIllustration } from '@/components/illustrations';

const meta = {
  title: 'UI/Empty State',
  component: EmptyState,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
      description: 'Heading text for the empty state',
    },
    description: {
      control: 'text',
      description: 'Optional description text',
    },
    action: {
      control: 'object',
      description: 'Optional action button configuration',
    },
  },
} satisfies Meta<typeof EmptyState>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic empty state
export const Default: Story = {
  args: {
    title: 'No items found',
    description: 'Get started by creating your first item.',
  },
};

// With icon
export const WithIcon: Story = {
  args: {
    icon: MessageSquare,
    title: 'No messages yet',
    description: 'Start a conversation to see your messages here.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state with an icon from lucide-react. Icons help users quickly understand the context.',
      },
    },
  },
};

// With action button
export const WithAction: Story = {
  args: {
    icon: Database,
    title: 'No connections',
    description: 'Connect to a database to start exploring your data.',
    action: {
      label: 'Add Connection',
      onClick: () => console.log('Add connection clicked'),
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state with a call-to-action button. Guide users toward the next step with a clear, actionable button.',
      },
    },
  },
};

// Empty chat state
export const EmptyChat: Story = {
  args: {
    title: "No messages yet",
    description: "Start a conversation by asking a question about your data.",
    action: {
      label: 'New Chat',
      onClick: () => console.log('New chat clicked'),
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state for the chat interface. Encourages users to start their first query.',
      },
    },
  },
};

// Empty knowledge base
export const EmptyKnowledge: Story = {
  args: {
    icon: BookOpen,
    title: "Your knowledge base is empty",
    description: "Save useful queries and domain knowledge to build a reusable library for your team.",
    action: {
      label: 'Create Entry',
      onClick: () => console.log('Create entry clicked'),
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state for the knowledge base. Explains the value of building a shared knowledge library.',
      },
    },
  },
};

// With custom illustration
export const WithIllustration: Story = {
  args: {
    title: "No messages yet",
    description: "Start a conversation to see your messages here.",
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state with custom SVG illustration. Illustrations add visual interest and reinforce the empty state context.',
      },
    },
  },
};

// All illustrations showcase
export const AllIllustrations: Story = {
  args: {
    title: "All Illustrations",
  },
  parameters: {
    docs: {
      description: {
        story: 'All custom empty state illustrations. These SVG illustrations use CSS custom properties for theme support.',
      },
    },
  },
};

// Accessibility
export const Accessibility: Story = {
  args: {
    icon: MessageSquare,
    title: "Accessible Empty State",
    description: "Empty states should be informative and provide clear next steps.",
    action: {
      label: 'Take Action',
      onClick: () => console.log('Action clicked'),
    },
  },
  parameters: {
    docs: {
      description: {
        story: `## Accessibility

Empty states should be accessible and informative:

### Visual Design
- Sufficient color contrast (4.5:1 for text)
- Clear visual hierarchy
- Icons are decorative (\`aria-hidden="true"\`)

### Content
- Descriptive titles explain what's empty
- Optional descriptions provide context
- Action buttons guide users to next steps

### Screen Readers
- Title is announced (heading level)
- Description provides additional context
- Action buttons are properly labeled

### Best Practices
- Be specific about what's empty (e.g., "No messages" vs "No items")
- Explain why it's empty when relevant
- Provide clear call-to-action
- Use illustrations to add visual interest
- Maintain brand consistency across all empty states`,
      },
    },
  },
};

// Usage guidelines
export const UsageGuidelines: Story = {
  args: {
    title: "Usage Guidelines",
  },
  parameters: {
    docs: {
      description: {
        story: `## Usage Guidelines

### When to Use Empty States

Use empty states when:
- A list has no items (zero state)
- A search returns no results
- A feature is not yet configured
- Data is still loading (with loading indicator)

### Content Guidelines

**Title:**
- Clear and specific
- Describes what's empty
- Use friendly, human language

**Description:**
- Explain why it's empty
- Provide context when helpful
- Keep it concise (1-2 sentences)

**Action:**
- Clear, actionable button text
- Leads to the next logical step
- Use primary button for main action

### Illustration Guidelines

**Custom SVG Illustrations:**
- Use CSS custom properties for colors
- Support light/dark themes
- Keep file size small (< 5KB)
- Use semantic, meaningful imagery

**Size Variants:**
- Small: 120px (inline empty states)
- Medium: 200px (page-level empty states)
- Large: 320px (full-page empty states)

### Component Examples

\`\`\`tsx
// Basic empty state
<EmptyState
  title="No items found"
/>

// With icon and description
<EmptyState
  icon={MessageSquare}
  title="No messages yet"
  description="Start a conversation..."
/>

// With action button
<EmptyState
  title="No connections"
  description="Connect to a database..."
  action={{
    label: 'Add Connection',
    onClick: handleAdd,
  }}
/>

// With custom illustration
<div>
  <EmptyChatIllustration size={200} />
  <EmptyState title="No messages" />
</div>
\`\`\``,
      },
    },
  },
};
