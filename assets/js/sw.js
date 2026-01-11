/* sw.js - Service Worker pour D2Glossary */

const CACHE_NAME = 'd2glossary-cache-v1';

// Fichiers critiques à cacher immédiatement lors de l'installation
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/assets/css/variables.css',
  '/assets/css/components.css',
  '/assets/css/d2elementstyles.css',
  '/assets/css/pagination.css',
  '/assets/css/popupitem.css',
  '/assets/css/loader.css',
  '/assets/js/utils.js',
  '/assets/js/dataManager.js',
  '/assets/js/pagination.js',
  '/assets/js/ddcvacuum.js',
  '/assets/js/popupitem.js',
  '/assets/js/itemListPage.js',
  '/assets/fonts/NeueHaasDisplayRoman.ttf',
  '/assets/fonts/Destiny2Class-ammo-activity.ttf',
  '/assets/fonts/destiny_symbols_common.otf',
  '/assets/src/ico/logo-d2glossaire.png',
  '/assets/html/banniere.html',
  '/assets/html/popupitem.html'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installation...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Mise en cache des assets critiques');
        return cache.addAll(CRITICAL_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch(err => console.error('[SW] Erreur installation:', err))
  );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', event => {
  console.log('[SW] Activation...');
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(name => name !== CACHE_NAME)
            .map(name => {
              console.log('[SW] Suppression ancien cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ne pas intercepter les requêtes externes (sauf Bungie)
  if (!url.origin.includes(self.location.origin) &&
      !url.origin.includes('bungie.net')) {
    return;
  }

  // Stratégie spéciale pour version.json : Network First
  if (url.pathname.endsWith('version.json')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Stratégie pour les fichiers JSON : Cache First
  if (url.pathname.endsWith('.json')) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Stratégie pour les autres assets : Cache First
  event.respondWith(cacheFirst(event.request));
});

// Stratégie Cache First
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    console.log('[SW] Cache hit:', request.url);
    return cached;
  }

  console.log('[SW] Cache miss, fetching:', request.url);
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    console.error('[SW] Fetch failed:', err);
    throw err;
  }
}

// Stratégie Network First (pour version.json)
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    console.log('[SW] Network failed, using cache:', request.url);
    const cached = await cache.match(request);
    if (cached) return cached;
    throw err;
  }
}

// Écoute les messages du client
self.addEventListener('message', event => {
  if (event.data.type === 'CLEAR_CACHE') {
    console.log('[SW] Clearing cache...');
    caches.delete(CACHE_NAME).then(() => {
      caches.open(CACHE_NAME).then(cache => {
        cache.addAll(CRITICAL_ASSETS);
      });
    });
    event.ports[0].postMessage({ success: true });
  }

  if (event.data.type === 'CACHE_FILE') {
    const url = event.data.url;
    caches.open(CACHE_NAME).then(cache => {
      fetch(url).then(response => {
        if (response.ok) {
          cache.put(url, response);
        }
      });
    });
  }
});