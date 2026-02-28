/**
 * OptimizedImage Component
 *
 * A wrapper around Next.js Image component with sensible defaults
 * for automatic image optimization, lazy loading, and responsive sizing.
 *
 * Usage:
 * ```tsx
 * import { OptimizedImage } from '@/components/ui/image';
 *
 * <OptimizedImage
 *   src="/path/to/image.png"
 *   alt="Description"
 *   width={800}
 *   height={600}
 *   priority={false} // Set to true for above-fold images
 * />
 * ```
 */

import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
  fill?: boolean;
  sizes?: string;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  fill = false,
  sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  quality = 75,
  placeholder = 'empty',
  blurDataURL,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  if (error) {
    return (
      <div
        className={`flex items-center justify-center bg-muted ${className}`}
        style={{ width, height }}
      >
        <span className="text-sm text-muted-foreground">Image not available</span>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {isLoading && !priority && (
        <div className="absolute inset-0 animate-pulse bg-muted" />
      )}
      <Image
        src={src}
        alt={alt}
        width={fill ? undefined : width}
        height={fill ? undefined : height}
        fill={fill}
        sizes={sizes}
        quality={quality}
        priority={priority}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        className={`transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setError(true);
        }}
      />
    </div>
  );
}

/**
 * AvatarImage - Optimized component for user avatars
 */
export function AvatarImage({
  src,
  alt,
  size = 40,
}: {
  src: string;
  alt: string;
  size?: number;
}) {
  return (
    <OptimizedImage
      src={src}
      alt={alt}
      width={size}
      height={size}
      className="rounded-full"
      sizes={`${size}px`}
    />
  );
}

/**
 * CardImage - Optimized component for card images
 */
export function CardImage({
  src,
  alt,
  aspectRatio = '16/9',
}: {
  src: string;
  alt: string;
  aspectRatio?: '16/9' | '4/3' | '1/1' | '3/2';
}) {
  const [width, height] = aspectRatio.split('/').map(Number);

  return (
    <OptimizedImage
      src={src}
      alt={alt}
      width={800}
      height={(800 * height) / width}
      className="w-full rounded-t-lg"
      sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
    />
  );
}
