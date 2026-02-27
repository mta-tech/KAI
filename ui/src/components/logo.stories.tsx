import type { Meta, StoryObj } from '@storybook/react';
import { Logo, LogoCompact, LogoMark } from './logo';

const meta = {
  title: 'Components/Logo',
  component: Logo,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Logo>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => <Logo />,
};

export const WithoutText: Story = {
  render: () => <Logo showText={false} />,
};

export const Small: Story = {
  render: () => <Logo size="sm" />,
};

export const Large: Story = {
  render: () => <Logo size="lg" />,
};

export const Compact: Story = {
  render: () => <LogoCompact />,
};

export const LogoMarkSmall: Story = {
  render: () => <LogoMark size="sm" />,
};

export const LogoMarkDefault: Story = {
  render: () => <LogoMark size="md" />,
};

export const LogoMarkLarge: Story = {
  render: () => <LogoMark size="lg" />,
};

export const InHeader: Story = {
  render: () => (
    <div className="flex items-center justify-between w-full px-4 py-3 border rounded-lg bg-background">
      <Logo />
      <div className="flex gap-2">
        <div className="h-8 w-20 bg-muted rounded" />
      </div>
    </div>
  ),
};

export const InSidebar: Story = {
  render: () => (
    <div className="w-64 p-4 space-y-4 border rounded-lg bg-background">
      <div className="flex items-center justify-between pb-3 border-b">
        <Logo />
      </div>
      <div className="space-y-2">
        {['Dashboard', 'Connections', 'Schema', 'Chat'].map((item) => (
          <div key={item} className="flex items-center gap-3 p-2 rounded hover:bg-muted cursor-pointer">
            <div className="h-4 w-4 bg-muted rounded" />
            <span className="text-sm">{item}</span>
          </div>
        ))}
      </div>
    </div>
  ),
};

export const AllVariants: Story = {
  render: () => (
    <div className="space-y-8 p-8">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Logo Variants</h3>
        <div className="flex flex-wrap gap-8 items-center">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Default</p>
            <Logo />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Small</p>
            <Logo size="sm" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Large</p>
            <Logo size="lg" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Compact</p>
            <LogoCompact />
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Logo Mark (Icon Only)</h3>
        <div className="flex flex-wrap gap-8 items-center">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Small</p>
            <LogoMark size="sm" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Default</p>
            <LogoMark size="md" />
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Large</p>
            <LogoMark size="lg" />
          </div>
        </div>
      </div>
    </div>
  ),
};
