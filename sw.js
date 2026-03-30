const CACHE_NAME = 'fom-newsroom-v4';
const KNOWN_PAGES = ['', 'index.html', 'medien.html', 'kontakt.html', 'artikel.html', 'autor.html', 'admin.html', '404.html'];
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/kontakt.html',
    '/medien.html',
    '/artikel.html',
    '/autor.html',
    '/fom-logo.png',
    '/fom-logo.svg',
    '/fom-logo-white.svg',
    '/akkreditierung.svg',
    '/auth.js',
    '/fonts/Neue-Haas-Grotesk-Text-Pro/Neue-Haas-Grotesk-Text-Pro-55-Regular.woff2',
    '/fonts/Neue-Haas-Grotesk-Text-Pro/Neue-Haas-Grotesk-Text-Pro-75-Bold.woff2',
    '/fonts/Neue-Haas-Grotesk-Display-Pro/Neue-Haas-Grotesk-Display-Pro-75-Bold.woff2'
];

const API_CACHE = 'fom-api-v1';
const API_MAX_AGE = 5 * 60 * 1000; // 5 minutes

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME && k !== API_CACHE).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // API calls: network-first with cache fallback (5 min TTL)
    if (url.hostname === 'www.mynewsdesk.com') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const clone = response.clone();
                    caches.open(API_CACHE).then(cache => {
                        const headers = new Headers(clone.headers);
                        headers.set('sw-cached-at', Date.now().toString());
                        const cachedResponse = new Response(clone.body, {
                            status: clone.status,
                            statusText: clone.statusText,
                            headers: headers
                        });
                        cache.put(event.request, cachedResponse);
                    });
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Clean article URLs: route unknown paths to artikel.html
    if (event.request.mode === 'navigate' && url.origin === self.location.origin) {
        const path = url.pathname.replace(/^\//, '').replace(/\/$/, '');
        if (path && !path.includes('.') && KNOWN_PAGES.indexOf(path) === -1) {
            // This is a clean article URL — serve artikel.html
            event.respondWith(
                caches.match('/artikel.html')
                    .then(cached => cached || fetch('/artikel.html'))
                    .then(response => {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put('/artikel.html', clone));
                        return response;
                    })
            );
            return;
        }
    }

    // HTML pages: network-first (always get fresh content, cache as fallback)
    if (event.request.method === 'GET' && (url.pathname.endsWith('.html') || url.pathname === '/' || !url.pathname.includes('.'))) {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    if (response.ok && url.origin === self.location.origin) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Static assets (fonts, images, JS): cache-first
    if (event.request.method === 'GET') {
        event.respondWith(
            caches.match(event.request).then(cached => {
                if (cached) return cached;
                return fetch(event.request).then(response => {
                    if (response.ok && url.origin === self.location.origin) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
    }
});
