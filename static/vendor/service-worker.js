const CACHE_NAME = 'parfumai-v1';
const STATIC_ASSETS = [
    '/',
    '/survey',
    '/static/vendor/bootstrap.min.css',
    '/static/vendor/bootstrap-icons.min.css',
    '/static/vendor/chart.umd.min.js',
    '/static/vendor/bootstrap.bundle.min.js',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/vendor/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    // Static assets: cache-first
    if (url.pathname.startsWith('/static/') || url.pathname === '/' || url.pathname === '/survey') {
        event.respondWith(
            caches.match(event.request).then(cached => cached || fetch(event.request))
        );
        return;
    }
    // API calls: network-first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(event.request))
        );
        return;
    }
    // Perfume images: stale-while-revalidate
    if (url.pathname.startsWith('/static/perfume_images/')) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                const fetchPromise = fetch(event.request).then(response => {
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, response.clone()));
                    return response;
                });
                return cached || fetchPromise;
            })
        );
        return;
    }
    event.respondWith(fetch(event.request));
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        ))
    );
});
