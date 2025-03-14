// Service Worker for PRISM-lite (Production Root Issue Sorting Mechanism) PWA

const CACHE_NAME = 'prism-lite-app-v1';
const urlsToCache = [
  '/',
  '/static/css/custom.css',
  '/static/js/main.js',
  '/static/manifest.json',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.discordapp.com/attachments/1005416721835900990/1348753341655552080/breez.blox_vector_logo_of_a_prism_depicting_the_letter_P_in_mon_c9346d2b-23db-4903-88b5-aa9e1cb461e4.png?ex=67d09bef&is=67cf4a6f&hm=b777f1d157278f3cdbcaec5220d3dc12410f86d5e6fc10096c382a84be903423&'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request because it's a one-time use
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(
          response => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response because it's a one-time use
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                // Don't cache API responses or potentially dynamic content
                if (!event.request.url.includes('/get_issues') && 
                    !event.request.url.includes('/submit_issue') &&
                    !event.request.url.includes('/contest_issue') &&
                    !event.request.url.includes('/export_csv') &&
                    !event.request.url.includes('/clear_data')) {
                  cache.put(event.request, responseToCache);
                }
              });

            return response;
          }
        );
      })
      .catch(() => {
        // If both cache and network fail, show a fallback page for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
        return new Response('Network error occurred', {
          status: 408,
          headers: { 'Content-Type': 'text/plain' }
        });
      })
  );
});

self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// We have duplicate event listeners for 'fetch'
// Remove this second one as it's causing errors
// The first fetch event listener above (line 26) already handles offline functionality