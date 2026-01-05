/* dataManager.js - Gestion centralisée du cache et chargement des données */

const VERSION_URL = 'data/version.json';
const CACHE_VERSION_KEY = 'd2glossary_version';
const CACHE_NAME = 'd2glossary-cache-v1';

// État global
let currentVersion = null;
let versionChecked = false;

// Cache mémoire pour les données JSON (évite de relire le cache disque)
const memoryCache = new Map();

/**
 * Vérifie la version et invalide le cache si nécessaire
 */
export async function checkVersion() {
  if (versionChecked) return currentVersion;

  try {
    // Toujours fetcher version.json depuis le réseau
    const response = await fetch(VERSION_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('Version fetch failed');

    const versionData = await response.json();
    const newVersion = versionData.version;
    const cachedVersion = localStorage.getItem(CACHE_VERSION_KEY);

    console.log('[DataManager] Version serveur:', newVersion);
    console.log('[DataManager] Version cache:', cachedVersion);

    if (cachedVersion !== newVersion) {
      console.log('[DataManager] Nouvelle version détectée, invalidation du cache...');
      await clearDataCache();
      localStorage.setItem(CACHE_VERSION_KEY, newVersion);
    }

    currentVersion = versionData;
    versionChecked = true;
    return versionData;
  } catch (err) {
    console.error('[DataManager] Erreur vérification version:', err);
    versionChecked = true;
    return null;
  }
}

/**
 * Vide le cache des données JSON uniquement
 */
async function clearDataCache() {
  if ('caches' in window) {
    const cache = await caches.open(CACHE_NAME);
    const keys = await cache.keys();

    for (const request of keys) {
      if (request.url.includes('/data/') && request.url.endsWith('.json')) {
        console.log('[DataManager] Suppression cache:', request.url);
        await cache.delete(request);
      }
    }
  }
}

/**
 * Affiche le loader
 */
export function showLoader(message = 'Chargement des données...') {
  let loader = document.getElementById('data-loader');

  if (!loader) {
    loader = document.createElement('div');
    loader.id = 'data-loader';
    loader.className = 'data-loader';
    loader.innerHTML = `
      <div class="loader-content">
        <img src="assets/src/ico/logo-d2glossaire.png" alt="D2Glossary" class="loader-logo">
        <div class="loader-message">${message}</div>
        <div class="loader-progress-container">
          <div class="loader-progress-bar" id="loader-progress-bar"></div>
        </div>
        <div class="loader-percentage" id="loader-percentage">0%</div>
      </div>
    `;
    document.body.appendChild(loader);
  } else {
    loader.querySelector('.loader-message').textContent = message;
    loader.style.display = 'flex';
  }

  // Empêcher le scroll
  document.body.classList.add('loader-active');

  return {
    updateProgress: (percent) => {
      const bar = document.getElementById('loader-progress-bar');
      const text = document.getElementById('loader-percentage');
      if (bar) bar.style.width = `${percent}%`;
      if (text) text.textContent = `${Math.round(percent)}%`;
    },
    updateMessage: (msg) => {
      const msgEl = loader.querySelector('.loader-message');
      if (msgEl) msgEl.textContent = msg;
    },
    hide: () => {
      loader.style.display = 'none';
      document.body.classList.remove('loader-active');
    }
  };
}

/**
 * Charge un fichier JSON avec gestion du cache et loader
 * Le loader ne s'affiche QUE si le fichier n'est pas en cache
 */
export async function loadJSONWithCache(url, options = {}) {
  const {
    showProgress = false,
    progressMessage = 'Chargement des données...'
  } = options;

  // Vérifier la version d'abord
  await checkVersion();

  // Vérifier le cache mémoire en premier (le plus rapide)
  if (memoryCache.has(url)) {
    console.log('[DataManager] Chargement depuis cache mémoire:', url);
    return memoryCache.get(url);
  }

  // Vérifier le cache disque (Service Worker)
  const isCached = await isInCache(url);

  // Si en cache disque, charger et mettre en cache mémoire
  if (isCached) {
    console.log('[DataManager] Chargement depuis cache disque:', url);
    try {
      const cache = await caches.open(CACHE_NAME);
      const response = await cache.match(url);
      if (response) {
        const data = await response.json();
        memoryCache.set(url, data);
        return data;
      }
    } catch (err) {
      console.warn('[DataManager] Erreur lecture cache, fallback fetch:', err);
    }
  }

  // Pas en cache : afficher le loader si demandé
  let loader = null;
  if (showProgress) {
    loader = showLoader(progressMessage);
  }

  try {
    const response = await fetchWithProgress(url, (progress) => {
      if (loader) loader.updateProgress(progress);
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    // Cloner la réponse pour la mettre en cache
    const responseClone = response.clone();
    const data = await response.json();

    // Mettre en cache mémoire
    memoryCache.set(url, data);

    // Mettre en cache disque
    if ('caches' in window) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(url, responseClone);
    }

    if (loader) {
      loader.updateProgress(100);
      await new Promise(r => setTimeout(r, 200));
      loader.hide();
    }

    return data;
  } catch (err) {
    if (loader) loader.hide();
    console.error(`[DataManager] Erreur chargement ${url}:`, err);
    throw err;
  }
}

/**
 * Récupère des données depuis le cache mémoire (synchrone, pour les popups)
 * Retourne null si pas en cache
 */
export function getFromMemoryCache(url) {
  return memoryCache.get(url) || null;
}

/**
 * Vérifie si un fichier est en cache
 */
async function isInCache(url) {
  if (!('caches' in window)) return false;

  try {
    const cache = await caches.open(CACHE_NAME);
    const response = await cache.match(url);
    return !!response;
  } catch {
    return false;
  }
}

/**
 * Fetch avec suivi de progression
 */
async function fetchWithProgress(url, onProgress) {
  const response = await fetch(url);

  if (!response.body) {
    onProgress(100);
    return response;
  }

  const contentLength = response.headers.get('content-length');

  if (!contentLength) {
    onProgress(50); // Pas de content-length, on estime
    const blob = await response.blob();
    onProgress(100);
    return new Response(blob, {
      headers: response.headers,
      status: response.status,
      statusText: response.statusText
    });
  }

  const total = parseInt(contentLength, 10);
  let loaded = 0;

  const reader = response.body.getReader();
  const chunks = [];

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    chunks.push(value);
    loaded += value.length;
    onProgress((loaded / total) * 100);
  }

  const blob = new Blob(chunks);
  return new Response(blob, {
    headers: response.headers,
    status: response.status,
    statusText: response.statusText
  });
}

/**
 * Précharge les fichiers légers en arrière-plan
 * @param {string} lang - Langue à précharger (par défaut: 'fr')
 */
export async function preloadLightFiles(lang = 'fr') {
  await checkVersion();

  if (!currentVersion?.files?.languages?.[lang]) {
    console.warn(`[DataManager] Langue ${lang} non trouvée dans version.json`);
    return;
  }

  const lightFiles = currentVersion.files.languages[lang].light;
  if (!lightFiles?.length) return;

  console.log(`[DataManager] Préchargement des fichiers légers [${lang.toUpperCase()}]...`);

  const promises = lightFiles.map(async (url) => {
    const isCached = await isInCache(url);
    if (!isCached) {
      console.log('[DataManager] Préchargement:', url);
      try {
        await fetch(url);
      } catch (err) {
        console.warn('[DataManager] Échec préchargement:', url, err);
      }
    }
  });

  await Promise.all(promises);
  console.log(`[DataManager] Préchargement terminé [${lang.toUpperCase()}]`);
}

/**
 * Force le rechargement des données
 */
export async function forceRefresh() {
  localStorage.removeItem(CACHE_VERSION_KEY);
  await clearDataCache();
  memoryCache.clear();
  versionChecked = false;
  currentVersion = null;
  window.location.reload();
}

// Export pour usage global
window.D2DataManager = {
  checkVersion,
  loadJSONWithCache,
  getFromMemoryCache,
  preloadLightFiles,
  forceRefresh,
  showLoader,
  getSupportedLanguages: () => {
    return currentVersion?.files?.languages
      ? Object.keys(currentVersion.files.languages)
      : ['fr'];
  }
};