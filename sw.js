const CACHE_NAME = 'mentora-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/script.js',
    '/style.css',
    '/style_additions.css',
    '/logo.svg',
    '/bg.jpg',
    '/icon-192.png',
    '/icon-512.png',
    '/manifest.json'
];

// Install: cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// Fetch: network-first for API calls, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Always go to network for API calls
    if (url.pathname.startsWith('/api')) {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response(
                    JSON.stringify({ type: 'text', message: '📱 You appear to be offline. Please check your connection.' }),
                    { headers: { 'Content-Type': 'application/json' } }
                );
            })
        );
        return;
    }

    // Cache-first for static assets
    event.respondWith(
        caches.match(event.request).then((cached) => {
            const networkFetch = fetch(event.request).then((response) => {
                // Update cache with fresh response
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            }).catch(() => cached);

            return cached || networkFetch;
        })
    );
});
