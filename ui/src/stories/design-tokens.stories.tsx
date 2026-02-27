import type { Meta, StoryObj } from '@storybook/react';
import { designTokens } from '../lib/tokens';

const meta = {
  title: 'Design Tokens/Overview',
  parameters: {
    layout: 'centered',
    options: {
      showPanel: false,
    },
  },
  tags: ['autodocs'],
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const DesignSystemOverview: Story = {
  render: () => (
    <div className="max-w-4xl mx-auto p-8 space-y-8">
      {/* Header */}
      <div className="border-b pb-6">
        <h1 className="text-4xl font-bold text-primary mb-2">KAI Design System</h1>
        <p className="text-lg text-muted-foreground">
          Design tokens and component library for the KAI application
        </p>
      </div>

      {/* Brand Colors */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Brand Colors</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Primary brand color is Deep Indigo (#6366f1)
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="h-20 rounded-lg bg-primary shadow-sm mb-2" />
            <p className="font-medium text-sm">Primary</p>
            <p className="text-xs text-muted-foreground">#6366f1</p>
          </div>
          <div>
            <div className="h-20 rounded-lg bg-secondary shadow-sm mb-2" />
            <p className="font-medium text-sm">Secondary</p>
            <p className="text-xs text-muted-foreground">#F6F6F6</p>
          </div>
          <div>
            <div className="h-20 rounded-lg bg-accent shadow-sm mb-2" />
            <p className="font-medium text-sm">Accent</p>
            <p className="text-xs text-muted-foreground">#F1F2FE</p>
          </div>
          <div>
            <div className="h-20 rounded-lg bg-destructive shadow-sm mb-2" />
            <p className="font-medium text-sm">Destructive</p>
            <p className="text-xs text-muted-foreground">#EF4444</p>
          </div>
        </div>
      </section>

      {/* Spacing Scale */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Spacing Scale</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Base unit: 4px. Scale follows a consistent rhythm.
        </p>
        <div className="space-y-2">
          {Object.entries(designTokens.spacing).slice(0, 12).map(([key, value]) => (
            <div key={key} className="flex items-center gap-4">
              <div className="w-16 text-sm font-medium">spacing-{key}</div>
              <div className="flex-1 border-b border-muted" />
              <div 
                className="bg-primary/20 rounded h-4" 
                style={{ width: key === '0' || key === 'px' ? value : `calc(${value} * 4)` }}
              />
              <div className="w-20 text-xs text-muted-foreground text-right">{value}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Typography */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Typography</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Font Sizes</h3>
            <div className="space-y-3">
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">xs</span>
                <span className="text-xs" style={{ fontSize: '0.75rem', lineHeight: '1rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">0.75rem (12px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">sm</span>
                <span className="text-sm" style={{ fontSize: '0.875rem', lineHeight: '1.25rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">0.875rem (14px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">base</span>
                <span className="text-base" style={{ fontSize: '1rem', lineHeight: '1.5rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">1rem (16px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">lg</span>
                <span className="text-lg" style={{ fontSize: '1.125rem', lineHeight: '1.75rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">1.125rem (18px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">xl</span>
                <span className="text-xl" style={{ fontSize: '1.25rem', lineHeight: '1.75rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">1.25rem (20px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">2xl</span>
                <span className="text-2xl" style={{ fontSize: '1.5rem', lineHeight: '2rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">1.5rem (24px)</span>
              </div>
              <div className="flex items-baseline gap-4">
                <span className="text-xs text-muted-foreground w-16">3xl</span>
                <span className="text-3xl" style={{ fontSize: '1.875rem', lineHeight: '2.25rem' }}>
                  The quick brown fox
                </span>
                <span className="text-xs text-muted-foreground">1.875rem (30px)</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-3">Font Weights</h3>
            <div className="space-y-2">
              {['light', 'normal', 'medium', 'semibold', 'bold'].map((weight) => (
                <div key={weight} className="flex items-center gap-4">
                  <span className="text-xs text-muted-foreground w-24">{weight}</span>
                  <span className={`font-${weight}`}>The quick brown fox jumps over the lazy dog</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Border Radius */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Border Radius</h2>
        <div className="flex flex-wrap gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-none mb-2" />
            <p className="text-xs text-muted-foreground">none</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-sm mb-2" />
            <p className="text-xs text-muted-foreground">sm</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded mb-2" />
            <p className="text-xs text-muted-foreground">default</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-md mb-2" />
            <p className="text-xs text-muted-foreground">md</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-lg mb-2" />
            <p className="text-xs text-muted-foreground">lg</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-xl mb-2" />
            <p className="text-xs text-muted-foreground">xl</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-2xl mb-2" />
            <p className="text-xs text-muted-foreground">2xl</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/20 rounded-full mb-2" />
            <p className="text-xs text-muted-foreground">full</p>
          </div>
        </div>
      </section>

      {/* Shadows */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Shadows</h2>
        <div className="flex flex-wrap gap-6">
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow-sm mb-2 border" />
            <p className="text-xs text-muted-foreground">sm</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow mb-2 border" />
            <p className="text-xs text-muted-foreground">default</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow-md mb-2 border" />
            <p className="text-xs text-muted-foreground">md</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow-lg mb-2 border" />
            <p className="text-xs text-muted-foreground">lg</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow-xl mb-2 border" />
            <p className="text-xs text-muted-foreground">xl</p>
          </div>
          <div className="text-center">
            <div className="w-24 h-24 bg-card rounded-lg shadow-2xl mb-2 border" />
            <p className="text-xs text-muted-foreground">2xl</p>
          </div>
        </div>
      </section>

      {/* Chart Colors */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">Chart Colors</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Colors for data visualization
        </p>
        <div className="flex gap-4">
          {Object.entries(designTokens.colors.chart).map(([key, value]) => (
            <div key={key} className="text-center">
              <div 
                className="w-16 h-16 rounded-lg mb-2" 
                style={{ backgroundColor: `hsl(${value})` }}
              />
              <p className="text-xs text-muted-foreground">chart-{key}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  ),
};
