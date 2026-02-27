/**
 * KAI UI Service Worker
 *
 * Caching strategy:
 * - Static assets: Cache-first with stale-while-revalidate
 * - API responses: Network-first with cache fallback
 * - Navigation: Network-first with offline fallback
 */

const CACHE_NAME = 'kai-v1';
const OFFLINE_CACHE = 'kai-offline-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/offline',
  '/manifest.json',
  // Icons and images will be cached dynamically
];

// API endpoints that can be cached
const CACHEABLE_API_PATTERNS = [
  /\/api\/knowledge\/glossary$/,
  /\/api\/knowledge\/instruction$/,
  /\/api\/connections$/,
  // Add more cacheable endpoints as needed
];

// API endpoints that should never be cached
const NO_CACHE_PATTERNS = [
  /\/api\/chat\/stream/,
  /\/api\/query/,
  // Real-time or sensitive endpoints
];

/**
 * Install event - cache static assets
 */
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      await cache.addAll(STATIC_ASSETS);

      // Create offline cache
      const offlineCache = await caches.open(OFFLINE_CACHE);
      await offlineCache.add('/offline');

      // Skip waiting to activate immediately
      self.skipWaiting();
    })()
  );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      // Delete old caches
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== OFFLINE_CACHE)
          .map((name) => caches.delete(name))
      );

      // Take control of all pages immediately
      self.clients.claim();
    })()
  );
});

/**
 * Fetch event - handle requests with caching strategies
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    // For API calls to backend, use network-first with cache fallback
    if (shouldCacheAPI(request.url)) {
      event.respondWith(networkFirstWithCache(request));
      return;
    }
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  // Handle static assets with cache-first strategy
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirstWithRefresh(request));
    return;
  }

  // Default: network-first
  event.respondWith(networkFirstWithCache(request));
});

/**
 * Handle navigation requests
 */
async function handleNavigation(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Show offline page
    const offlineCache = await caches.open(OFFLINE_CACHE);
    const offlineResponse = await offlineCache.match('/offline');
    if (offlineResponse) {
      return offlineResponse;
    }

    // Return basic offline response
    return new Response(
      '<h1>Offline</h1><p>You are currently offline. Please check your connection.</p>',
      {
        headers: { 'Content-Type': 'text/html' },
        status: 503,
      }
    );
  }
}

/**
 * Cache-first with stale-while-revalidate strategy
 */
async function cacheFirstWithRefresh(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);

  // Fetch in background to update cache
  const fetchPromise = fetch(request).then((networkResponse) => {
    cache.put(request, networkResponse.clone());
    return networkResponse;
  });

  // Return cached response immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }

  // Otherwise wait for network
  return fetchPromise;
}

/**
 * Network-first with cache fallback strategy
 */
async function networkFirstWithCache(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    const networkResponse = await fetch(request);

    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Return error response
    return new Response('Network request failed', { status: 503 });
  }
}

/**
 * Check if URL should be cached
 */
function shouldCacheAPI(url) {
  // Check if URL matches cacheable patterns
  for (const pattern of CACHEABLE_API_PATTERNS) {
    if (pattern.test(url)) {
      return true;
    }
  }

  // Check if URL is in no-cache list
  for (const pattern of NO_CACHE_PATTERNS) {
    if (pattern.test(url)) {
      return false;
    }
  }

  return false;
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(pathname) {
  return (
    pathname.includes('/static/') ||
    pathname.includes('/_next/static/') ||
    pathname.includes('/_next/image/') ||
    pathname.match(/\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/)
  );
}

/**
 * Message event - handle messages from clients
 */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        await cache.addAll(event.data.urls);
      })()
    );
  }
});
