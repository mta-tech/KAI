'use client';

/**
 * PageTransition Component
 *
 * Provides smooth page transitions with fade in/out animations.
 * Respects user's prefers-reduced-motion setting.
 *
 * Usage: Wrap page content in layout.tsx or individual pages
 */

import { useEffect, useState, useRef } from 'react';
import { usePathname } from 'next/navigation';

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export function PageTransition({ children, className = '' }: PageTransitionProps) {
  const [isReducedMotion, setIsReducedMotion] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const pathname = usePathname();
  const prevPathname = useRef(pathname);
  const [displayChildren, setDisplayChildren] = useState(children);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleChange = () => setIsReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  useEffect(() => {
    if (pathname !== prevPathname.current) {
      // Page is changing
      if (!isReducedMotion) {
        setIsExiting(true);
        const timeout = setTimeout(() => {
          setDisplayChildren(children);
          setIsExiting(false);
        }, 200);

        return () => clearTimeout(timeout);
      } else {
        setDisplayChildren(children);
      }
      prevPathname.current = pathname;
    } else {
      setDisplayChildren(children);
    }
  }, [children, pathname, isReducedMotion]);

  const animationClass = isExiting ? 'animate-page-exit' : 'animate-page-enter';

  return (
    <div
      className={`${className} ${isReducedMotion ? '' : animationClass}`}
    >
      {displayChildren}
    </div>
  );
}

/**
 * FadeIn animation for individual elements
 */
export function FadeIn({
  children,
  delay = 0,
  duration = 0.3,
  className = '',
}: {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleChange = () => setIsReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    // Trigger animation after mount
    const timeout = setTimeout(() => setIsVisible(true), delay * 1000);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
      clearTimeout(timeout);
    };
  }, [delay]);

  const style = !isReducedMotion
    ? {
        opacity: isVisible ? 1 : 0,
        transition: `opacity ${duration}s ease-in-out ${delay}s`,
      }
    : {};

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

/**
 * SlideIn animation for elements appearing from sides
 */
export function SlideIn({
  children,
  direction = 'up',
  delay = 0,
  className = '',
}: {
  children: React.ReactNode;
  direction?: 'up' | 'down' | 'left' | 'right';
  delay?: number;
  className?: string;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleChange = () => setIsReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    const timeout = setTimeout(() => setIsVisible(true), delay * 1000);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
      clearTimeout(timeout);
    };
  }, [delay]);

  const translateMap = {
    up: 'translateY(20px)',
    down: 'translateY(-20px)',
    left: 'translateX(20px)',
    right: 'translateX(-20px)',
  };

  const style = !isReducedMotion
    ? {
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'none' : translateMap[direction],
        transition: `opacity 0.3s ease-out ${delay}s, transform 0.3s ease-out ${delay}s`,
      }
    : {};

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

/**
 * ScaleIn animation for modal-like elements
 */
export function ScaleIn({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);

    const handleChange = () => setIsReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    const timeout = setTimeout(() => setIsVisible(true), 0);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
      clearTimeout(timeout);
    };
  }, []);

  const style = !isReducedMotion
    ? {
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'scale(1)' : 'scale(0.95)',
        transition: 'opacity 0.2s ease-out, transform 0.2s ease-out',
      }
    : {};

  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}
