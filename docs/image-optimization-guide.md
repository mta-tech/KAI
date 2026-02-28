# Image Optimization Guide

## Overview

The KAI UI application uses Next.js built-in image optimization to automatically serve optimized images in modern formats.

## Configuration

Image optimization is configured in `next.config.mjs`:

```js
images: {
  formats: ['image/avif', 'image/webp'],
  deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  minimumCacheTTL: 60,
  dangerouslyAllowSVG: true,
  contentDispositionType: 'attachment',
  contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
}
```

### What This Means

- **AVIF/WebP formats**: Modern formats with better compression
- **Responsive sizes**: Images served at appropriate sizes for device
- **SVG support**: SVG images can be used inline
- **CSP headers**: Security headers for image resources
- **Caching**: Images cached for 60 seconds minimum

## Using the OptimizedImage Component

### Basic Usage

```tsx
import { OptimizedImage } from '@/components/ui/image';

<OptimizedImage
  src="/path/to/image.png"
  alt="Description of the image"
  width={800}
  height={600}
/>
```

### With Lazy Loading (default)

```tsx
<OptimizedImage
  src="/large-image.jpg"
  alt="Large image"
  width={1920}
  height={1080}
  priority={false} // Lazy loads
/>
```

### Priority Loading (Above Fold)

```tsx
<OptimizedImage
  src="/hero-image.jpg"
  alt="Hero section image"
  width={1920}
  height={1080}
  priority={true} // Loads immediately
/>
```

### Responsive Fill

```tsx
<div className="relative h-64 w-full">
  <OptimizedImage
    src="/background.jpg"
    alt="Background"
    fill={true}
    sizes="(max-width: 768px) 100vw, 50vw"
  />
</div>
```

## Specialized Components

### AvatarImage

For user avatars and profile pictures:

```tsx
import { AvatarImage } from '@/components/ui/image';

<AvatarImage
  src="/user-avatar.jpg"
  alt="User name"
  size={40}
/>
```

### CardImage

For card images with aspect ratios:

```tsx
import { CardImage } from '@/components/ui/image';

<CardImage
  src="/card-image.jpg"
  alt="Card image"
  aspectRatio="16/9"
/>
```

Supported aspect ratios: '16/9', '4/3', '1/1', '3/2'

## Best Practices

1. **Always provide alt text** for accessibility
2. **Use priority for above-fold images** to prevent layout shift
3. **Specify appropriate sizes** for responsive images
4. **Use WebP/AVIF source images** when possible
5. **Optimize source images** before adding to project
6. **Use specialized components** (AvatarImage, CardImage) when applicable

## Image Formats

### Supported Formats

- JPEG/PNG - Convert to WebP automatically
- WebP - Served as-is when supported
- AVIF - Preferred when supported
- SVG - Served inline with CSP headers

### Format Priority

1. AVIF (best compression)
2. WebP (good compression, wide support)
3. Original format (fallback)

## Performance Tips

1. **Compress images before upload** - Use tools like squoosh.app
2. **Use appropriate dimensions** - Don't use larger images than needed
3. **Lazy load below-fold images** - Default behavior
4. **Use priority sparingly** - Only for critical images
5. **Consider using blur placeholders** - For better perceived performance

## Monitoring

Check image sizes in the bundle analyzer:

```bash
npm run analyze
```

Images served from Next.js optimization are not included in the bundle size.

## Current Status

- [x] Image optimization configured in next.config.mjs
- [x] AVIF/WebP formats enabled
- [x] Responsive sizes configured
- [x] OptimizedImage component created
- [x] AvatarImage component created
- [x] CardImage component created
- [x] Lazy loading enabled by default
- [x] CSP headers configured

## Future Improvements

- Add placeholder blur generation
- Implement progressive image loading
- Add WebP conversion script for existing images
- Consider adding a CDN for image delivery
