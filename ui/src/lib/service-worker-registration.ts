/**
 * Service Worker Registration
 *
 * Handles service worker registration and provides utilities for
 * communicating with the service worker.
 */

const PUBLIC_SW_URL = '/sw.js';

let registration: ServiceWorkerRegistration | null = null;
let isUpdating = false;

export interface ServiceWorkerStatus {
  isSupported: boolean;
  isRegistered: boolean;
  isActivated: boolean;
  isUpdating: boolean;
}

/**
 * Check if service workers are supported
 */
export function isServiceWorkerSupported(): boolean {
  return 'serviceWorker' in navigator;
}

/**
 * Register the service worker
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!isServiceWorkerSupported()) {
    console.warn('Service workers are not supported in this browser');
    return null;
  }

  if (registration) {
    return registration;
  }

  try {
    registration = await navigator.serviceWorker.register(PUBLIC_SW_URL, {
      updateViaCache: 'imports',
    });

    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration?.installing;
      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New version available
            isUpdating = true;
            notifyUpdateAvailable();
          }
        });
      }
    });

    // Handle controller change (new service worker activated)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      window.location.reload();
    });

    return registration;
  } catch (error) {
    console.error('Service worker registration failed:', error);
    return null;
  }
}

/**
 * Unregister the service worker
 */
export async function unregisterServiceWorker(): Promise<void> {
  if (!isServiceWorkerSupported()) {
    return;
  }

  const reg = await navigator.serviceWorker.getRegistration();
  if (reg) {
    await reg.unregister();
    registration = null;
  }
}

/**
 * Get service worker status
 */
export function getServiceWorkerStatus(): ServiceWorkerStatus {
  return {
    isSupported: isServiceWorkerSupported(),
    isRegistered: registration !== null,
    isActivated: navigator.serviceWorker.controller !== null,
    isUpdating,
  };
}

/**
 * Skip waiting and activate the new service worker immediately
 */
export function skipWaiting(): void {
  if (registration && registration.waiting) {
    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  }
}

/**
 * Cache specific URLs
 */
export function cacheUrls(urls: string[]): void {
  if (registration && registration.active) {
    registration.active.postMessage({ type: 'CACHE_URLS', urls });
  }
}

/**
 * Clear all caches
 */
export async function clearAllCaches(): Promise<void> {
  if (!isServiceWorkerSupported()) {
    return;
  }

  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map((name) => caches.delete(name)));
}

/**
 * Get estimated cache size
 */
export async function getCacheSize(): Promise<number> {
  if (!isServiceWorkerSupported()) {
    return 0;
  }

  const cacheNames = await caches.keys();
  let totalSize = 0;

  for (const name of cacheNames) {
    const cache = await caches.open(name);
    const keys = await cache.keys();
    for (const request of keys) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        totalSize += blob.size;
      }
    }
  }

  return totalSize;
}

/**
 * Notify about available updates
 * Dispatches a custom event that components can listen to
 */
function notifyUpdateAvailable(): void {
  window.dispatchEvent(new CustomEvent('sw-update-available'));
}

/**
 * Listen for service worker updates
 */
export function onUpdateAvailable(callback: () => void): () => void {
  window.addEventListener('sw-update-available', callback);
  return () => window.removeEventListener('sw-update-available', callback);
}
