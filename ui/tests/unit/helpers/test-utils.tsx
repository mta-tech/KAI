import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { vi, beforeAll, afterAll } from 'vitest';

/**
 * Custom render function that includes any necessary providers
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  // Add any necessary providers here (Theme, Query, etc.)
  return render(ui, options);
}

/**
 * Mock intersection observer for components that use it
 */
export function mockIntersectionObserver() {
  const mockIntersectionObserver = vi.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.IntersectionObserver = mockIntersectionObserver as any;
}

/**
 * Mock window.matchMedia for responsive testing
 */
export function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

/**
 * Wait for async updates to complete
 */
export async function waitForAnimations() {
  await new Promise(resolve => setTimeout(resolve, 0));
}

/**
 * Create a mock function with TypeScript typing
 */
export function createMock<T extends (...args: any[]) => any>() {
  return vi.fn() as unknown as T;
}

/**
 * Mock React Query mutations
 */
export function mockMutation<T>() {
  return {
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    reset: vi.fn(),
  } as unknown as T;
}

/**
 * Suppress console errors during test execution
 */
export function suppressConsoleErrors() {
  const originalError = console.error;
  beforeAll(() => {
    console.error = vi.fn();
  });

  afterAll(() => {
    console.error = originalError;
  });
}

/**
 * Test utility to check if element has specific class
 */
export function hasClass(element: HTMLElement, className: string): boolean {
  return element.classList.contains(className);
}

/**
 * Test utility to check if element has data attribute
 */
export function hasDataAttribute(element: HTMLElement, attr: string): boolean {
  return element.hasAttribute(`data-${attr}`);
}

/**
 * Mock window.location
 */
export function mockWindowLocation(href: string) {
  delete (window as any).location;
  (window as any).location = { href };
}

/**
 * Restore window.location
 */
export function restoreWindowLocation() {
  delete (window as any).location;
  Object.defineProperty(window, 'location', {
    value: location,
    writable: true,
    configurable: true,
  });
}
