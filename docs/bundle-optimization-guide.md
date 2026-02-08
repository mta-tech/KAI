# Bundle Optimization Guide

## Overview

This guide describes the bundle optimization strategies implemented in the KAI UI application.

## Implemented Optimizations

### 1. Route-Based Code Splitting

Next.js App Router automatically splits each route into its own chunk. See [code-splitting-guide.md](./code-splitting-guide.md) for details.

### 2. Tree Shaking

Tree shaking is enabled by default in Next.js production builds. We've enhanced it with:

- **Modular imports for lucide-react**: Icons are imported individually to reduce bundle size
- **Named imports only**: All imports use named imports for optimal tree shaking

```js
// next.config.mjs
modularizeImports: {
  'lucide-react': {
    transform: 'lucide-react/dist/esm/icons/{{kebabCase member}}',
  },
},
```

### 3. Production Optimizations

The following optimizations are enabled in `next.config.mjs`:

```js
{
  // Disable source maps in production to reduce size
  productionBrowserSourceMaps: false,

  // Enable gzip compression
  compress: true,

  // Optimize images with modern formats
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // Webpack optimizations
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false, // Remove fs polyfill from client bundle
      };
    }
    return config;
  },
}
```

### 4. Dependency Management

We actively manage dependencies to keep bundle size small:

- Regularly check for unused dependencies
- Prefer smaller alternative packages
- Use bundlephobia.com when adding new dependencies

## Monitoring Bundle Size

### Analyze Bundle

Run the bundle analyzer to see detailed breakdown:

```bash
npm run analyze
```

### Check Bundle Budgets

After build, check if within budget:

```bash
npm run bundle-size
```

Current budgets:
- Initial JS: 200KB gzipped
- Page JS: 100KB per page
- Total JS: 500KB total

### Check Unused Dependencies

```bash
npm run check-deps
```

## Best Practices

1. **Use dynamic imports** for heavy components
2. **Import specific icons** from lucide-react
3. **Avoid large libraries** if a smaller alternative exists
4. **Run bundle analyzer** before committing significant changes
5. **Monitor bundle size** in CI/CD

## Current Bundle Status

As of latest build:

- Initial bundle: TBD
- Total JS: TBD

Run `npm run analyze` to get current numbers.

## Optimization Checklist

- [x] Enable tree shaking
- [x] Modular imports for lucide-react
- [x] Production source maps disabled
- [x] Gzip compression enabled
- [x] Image optimization configured
- [x] Bundle analyzer integrated
- [x] Bundle size budgets defined
- [x] Dependency analysis script

## Future Optimizations

- Consider implementing dynamic imports for heavy chart components
- Add bundle size regression to CI
- Implement service worker for caching
- Add more aggressive code splitting for vendor chunks
