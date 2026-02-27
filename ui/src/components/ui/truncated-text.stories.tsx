import type { Meta, StoryObj } from '@storybook/react';
import { TruncatedText, TruncatedCell } from '@/components/ui/truncated-text';

const meta: Meta<typeof TruncatedText> = {
  title: 'UI/Truncated Text',
  component: TruncatedText,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof TruncatedText>;

export const Default: Story = {
  render: () => (
    <div className="w-80">
      <TruncatedText>
        This is a very long text that should be truncated when it exceeds the container width
      </TruncatedText>
    </div>
  ),
};

export const WithMaxLength: Story = {
  render: () => (
    <div>
      <TruncatedText maxLength={20}>
        This is a very long text that should be truncated at 20 characters
      </TruncatedText>
    </div>
  ),
};

export const ShortText: Story = {
  render: () => (
    <div className="w-80">
      <TruncatedText>Short text</TruncatedText>
    </div>
  ),
};

export const TableCell: Story = {
  render: () => (
    <div className="w-64 border rounded p-4">
      <TruncatedCell header="Description">
        This is a very long description that would typically overflow in a table cell
      </TruncatedCell>
    </div>
  ),
};

export const Mobile: Story = {
  render: () => (
    <div className="w-64">
      <p className="text-xs text-muted-foreground mb-2">Long press for tooltip on mobile</p>
      <TruncatedText>
        On mobile, long press (500ms) to see the full text in a tooltip. Regular hover works on desktop.
      </TruncatedText>
    </div>
  ),
  parameters: {
    viewport: {
      defaultViewport: 'iphone12',
    },
  },
};

export const MultipleItems: Story = {
  render: () => (
    <div className="space-y-2 w-80">
      <TruncatedText>
        First item with very long text that needs truncation
      </TruncatedText>
      <TruncatedText>
        Second item with very long text that needs truncation
      </TruncatedText>
      <TruncatedText>
        Third item with very long text that needs truncation
      </TruncatedText>
    </div>
  ),
};
