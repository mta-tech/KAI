# Visual Regression Testing Guide

This guide covers visual regression testing setup and usage for the KAI UI application using Chromatic with Storybook.

## Overview

Visual regression testing automatically detects unintended visual changes by comparing screenshots of components against approved baselines.

## Setup

### Prerequisites
- ✅ Storybook installed and configured (#22)
- ✅ Base component library built (#20)
- ✅ Design tokens established (#19)
- ✅ @chromatic-com/storybook package installed

### Chromatic Integration

Chromatic is already integrated via `@chromatic-com/storybook` in package.json.

## Running Visual Tests

### Build Storybook for Chromatic
```bash
npm run build-storybook
```

### Run Chromatic Locally
```bash
npx chromatic --project-token=YOUR_TOKEN
```

## Workflow

### 1. Initial Baseline
When setting up visual regression for the first time:
1. Build Storybook: `npm run build-storybook`
2. Run Chromatic to capture baselines
3. Review and approve all baseline snapshots
4. Baseline is now established

### 2. Development Workflow
When making visual changes:
1. Make component changes
2. Update/add Storybook stories if needed
3. Run Chromatic to see visual diffs
4. Review changes:
   - **Green**: No visual changes ✅
   - **Yellow**: Acceptable changes (approve them) ⚠️
   - **Red**: Unintended changes (fix them) ❌

### 3. CI/CD Integration
Chromatic runs automatically on PRs:
- Compares against baseline
- Comments on PR with visual changes
- Blocks merge if unintended changes detected

## Component Coverage

### Priority Components for Visual Testing

#### Base UI Components (High Priority)
- Button
- Input
- Select
- Checkbox
- Radio
- Switch
- Dialog
- Dropdown Menu
- Toast
- Tabs
- Card

#### Feature Components (Medium Priority)
- Chat components (MessageBubble, ChatInput, SessionSidebar)
- Knowledge components (InstructionCard, GlossaryItem)
- Schema components (TableCard, ColumnDetails)
- Connection components (ConnectionCard, AddConnectionDialog)

#### Layout Components (Medium Priority)
- Sidebar
- Header
- Layout structure

#### Page Components (Lower Priority)
- Dashboard
- Settings
- Forms

## Writing Visual Tests

### Story Structure for Visual Testing

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './button';

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Default: Story = {
  args: {
    variant: 'default',
    size: 'default',
    children: 'Button',
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4 flex-wrap">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
    </div>
  ),
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-4 items-center">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      <Button size="icon">Icon</Button>
    </div>
  ),
};
```

### Best Practices for Visual Tests

1. **Cover All Variants**: Test all combinations of variants, sizes, states
2. **Test Interactive States**: Include hover, focus, disabled states
3. **Use Real Content**: Use realistic text and data
4. **Test Edge Cases**: Empty states, loading states, error states
5. **Organize by Hierarchy**: Group related stories logically

### Testing States

```typescript
export const States: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button>Default</Button>
      <Button disabled>Disabled</Button>
      <Button className="pointer-events-none">Hover (simulated)</Button>
    </div>
  ),
};
```

### Testing with Different Content

```typescript
export const WithLongContent: Story = {
  args: {
    children: 'This is a very long button text that should wrap or truncate properly',
  },
};

export const WithIcon: Story = {
  args: {
    children: (
      <>
        <Icon name="check" className="mr-2" />
        With Icon
      </>
    ),
  },
};
```

## Handling Visual Changes

### Accepting Intended Changes
When you've made intentional visual changes:
1. Review the diff in Chromatic
2. Add a note explaining the change
3. Accept the new baseline
4. Chromatic updates the baseline

### Rejecting Unintended Changes
When you see unintended changes:
1. Identify the cause (spacing, color, typography, etc.)
2. Fix the issue in the code
3. Push the fix
4. Chromatic will show the fix resolved

### Common Visual Regressions

| Issue | Cause | Fix |
|-------|-------|-----|
| Spacing changes | CSS conflicts, margin/padding | Review cascade styles, use design tokens |
| Color shifts | Token not applied, wrong token | Verify design token usage |
| Typography | Font family/size mismatch | Check text styles, use token-based typography |
| Layout shifts | Missing styles, responsive issues | Test at multiple breakpoints |
| Missing content | Conditional rendering | Verify all states are tested |

## Configuration

### Chromatic Project Configuration

Create `.chromaticrc.json`:
```json
{
  "projectId": "kai-ui",
  "buildScriptName": "build-storybook",
  "exitZeroOnChanges": true,
  "autoAcceptChanges": "none",
  "branches": ["main", "develop"],
  "onlyStoryKinds": [
    "component",
    "story"
  ]
}
```

### Ignore Patterns

Ignore elements that change frequently but don't affect design:

```typescript
// In story decorators
export const decorators = [
  (Story) => (
    <div className="visual-testing">
      <Story />
    </div>
  ),
];
```

CSS to ignore:
```css
.visual-testing {
  /* Ignore dynamic elements */
  animation: none !important;
  transition: none !important;
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Chromatic

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Install dependencies
        run: npm ci
      - name: Build Storybook
        run: npm run build-storybook
      - name: Publish to Chromatic
        uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          token: ${{ secrets.GITHUB_TOKEN }}
```

### Pre-commit Hook

Run visual tests before committing:
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm run build-storybook && npx chromatic --only-changed"
    }
  }
}
```

## Troubleshooting

### Stories Not Appearing
- Check Storybook build completed successfully
- Verify stories are properly exported
- Check console for errors in Storybook

### False Positives
- Add ignore patterns for dynamic content
- Use consistent data in stories
- Mock dynamic data (dates, random numbers)

### Slow Builds
- Only test changed stories: `--only-changed`
- Split into multiple projects
- Use `exitZeroOnChanges` for non-blocking checks

## Best Practices

1. **Commit Baselines**: Always commit visual baselines for approved stories
2. **Review Diffs Carefully**: Take time to review all visual changes
3. **Document Changes**: Add notes when accepting changes for context
4. **Test Multiple Breakpoints**: Ensure responsive design works
5. **Keep Stories Simple**: Focus on visual output, not complex interactions
6. **Use Real Data**: Visual tests should reflect production appearance

## Metrics

Track visual regression testing:
- Number of components covered
- Number of stories tested
- False positive rate
- Time to review changes
- Test duration

## References

- [Chromatic Documentation](https://www.chromatic.com/docs)
- [Storybook Visual Testing](https://storybook.js.org/docs/essentials/visual-testing)
- [Design Tokens Guide](../ui/BROWSER_TESTING_MATRIX.md)
