# Page Transitions Guide

## Overview

The KAI UI application includes smooth page transitions and animation components that respect user accessibility preferences.

## Implementation

### PageTransition Component

The main `PageTransition` component provides fade in/out animations when navigating between routes.

#### Usage

Wrap page content in your layout:

```tsx
// app/layout.tsx
import { PageTransition } from '@/components/page-transition';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <PageTransition>
          {children}
        </PageTransition>
      </body>
    </html>
  );
}
```

### Animation Components

#### FadeIn

Fade in elements with optional delay:

```tsx
import { FadeIn } from '@/components/page-transition';

<FadeIn delay={0.1} duration={0.3}>
  <div>This content fades in</div>
</FadeIn>
```

#### SlideIn

Slide elements in from a direction:

```tsx
import { SlideIn } from '@/components/page-transition';

<SlideIn direction="up" delay={0.2}>
  <div>Slides up</div>
</SlideIn>

<SlideIn direction="left">
  <div>Slides from left</div>
</SlideIn>
```

Directions: `up`, `down`, `left`, `right`

#### ScaleIn

Scale elements in (good for modals):

```tsx
import { ScaleIn } from '@/components/page-transition';

<ScaleIn>
  <div>Scales in</div>
</ScaleIn>
```

## Accessibility

All animations automatically respect `prefers-reduced-motion`:

- When reduced motion is detected, animations are disabled
- No CSS animations are applied
- Content is immediately visible

### Testing Reduced Motion

To test reduced motion:
1. Open browser DevTools
2. Open Rendering tab
3. Enable "Emulate CSS media feature prefers-reduced-motion: reduce"

## CSS Animations

The following CSS animations are available via utility classes:

### Page Transitions

- `animate-page-enter` - Fade in from bottom
- `animate-page-exit` - Fade out to top

### Element Animations

- `animate-fade-in` - Simple fade
- `animate-slide-in-up` - Slide from bottom
- `animate-slide-in-down` - Slide from top
- `animate-slide-in-left` - Slide from left
- `animate-slide-in-right` - Slide from right
- `animate-scale-in` - Scale from 0.95 to 1

### Usage Example

```tsx
<div className="animate-fade-in">
  Content fades in
</div>

<div className="animate-slide-in-up">
  Content slides up
</div>
```

## Performance

- Animations use CSS transforms and opacity (GPU accelerated)
- Duration defaults to 200-300ms for snappy feel
- No JavaScript libraries required (framer-motion free)
- Automatically disabled for reduced motion users

## Best Practices

1. **Use sparingly** - Animate only when it adds value
2. **Keep it short** - 200-300ms is usually enough
3. **Test reduced motion** - Always verify with prefers-reduced-motion
4. **Consider context** - Don't animate critical alerts or error messages
5. **Consistent duration** - Use similar durations across the app

## Troubleshooting

### Animations not working

1. Check if reduced motion is enabled in browser
2. Verify CSS classes are applied (check DevTools)
3. Ensure JavaScript is enabled for component animations

### Transitions feel slow

1. Reduce duration in component props
2. Consider disabling certain animations
3. Profile performance in DevTools

### Accessibility issues

1. Always test with screen reader
2. Ensure animated content is announced
3. Respect user's motion preferences
