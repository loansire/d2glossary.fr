/* languageSelector.js - Gestion du sélecteur de langue avec support QueryParam */

const LANG_STORAGE_KEY = 'd2glossary_language';
const LANG_QUERY_PARAM = 'lang';
const SUPPORTED_LANGUAGES = ['fr', 'en'];
const DEFAULT_LANGUAGE = 'fr';
const LANGUAGE_NAMES = {
  'fr': 'FR',
  'en': 'EN'
};

/**
 * Récupère la langue depuis le queryParam ?lang=
 * @returns {string|null} Code langue ou null si non présent/invalide
 */
function getLanguageFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const langParam = urlParams.get(LANG_QUERY_PARAM);

  if (langParam && SUPPORTED_LANGUAGES.includes(langParam.toLowerCase())) {
    return langParam.toLowerCase();
  }
  return null;
}

/**
 * Met à jour l'URL avec le paramètre lang (ou le retire si FR)
 * @param {string} lang - Code de langue
 */
function updateUrlLanguageParam(lang) {
  const url = new URL(window.location);

  if (lang === DEFAULT_LANGUAGE) {
    // Retirer le param si c'est la langue par défaut (FR)
    url.searchParams.delete(LANG_QUERY_PARAM);
  } else {
    url.searchParams.set(LANG_QUERY_PARAM, lang);
  }

  // Mettre à jour l'URL sans recharger
  history.replaceState(null, '', url);
}

/**
 * Récupère la langue active (queryParam > stockée > détectée)
 * Priorité: 1. QueryParam ?lang= 2. localStorage 3. Navigateur 4. Défaut (fr)
 */
export function getCurrentLanguage() {
  // 1. Vérifier le queryParam en priorité
  const urlLang = getLanguageFromUrl();
  if (urlLang) {
    // Sauvegarder dans le localStorage pour les futures visites
    localStorage.setItem(LANG_STORAGE_KEY, urlLang);
    return urlLang;
  }

  // 2. Vérifier le localStorage
  const stored = localStorage.getItem(LANG_STORAGE_KEY);
  if (stored && SUPPORTED_LANGUAGES.includes(stored)) {
    return stored;
  }

  // 3. Détecter depuis le navigateur
  const browserLang = navigator.language.split('-')[0];
  const detected = SUPPORTED_LANGUAGES.includes(browserLang) ? browserLang : DEFAULT_LANGUAGE;

  // Sauvegarder la détection
  localStorage.setItem(LANG_STORAGE_KEY, detected);
  return detected;
}

/**
 * Change la langue active
 * @param {string} lang - Code de langue ('fr' ou 'en')
 * @param {boolean} reload - Recharger la page après changement (défaut: true)
 */
export function setCurrentLanguage(lang, reload = true) {
  if (!SUPPORTED_LANGUAGES.includes(lang)) {
    console.error(`Langue non supportée: ${lang}`);
    return false;
  }

  localStorage.setItem(LANG_STORAGE_KEY, lang);
  console.log(`[Language] Langue changée: ${lang.toUpperCase()}`);

  // Mettre à jour l'URL
  updateUrlLanguageParam(lang);

  if (reload) {
    // Recharger la page pour appliquer la nouvelle langue
    window.location.reload();
  }

  return true;
}

/**
 * Construit une URL avec le paramètre lang approprié
 * @param {string} baseUrl - URL de base
 * @param {string} lang - Code de langue (optionnel, utilise la langue courante)
 * @returns {string} URL avec paramètre lang si nécessaire
 */
export function buildUrlWithLang(baseUrl, lang = null) {
  const targetLang = lang || getCurrentLanguage();
  const url = new URL(baseUrl, window.location.origin);

  if (targetLang !== DEFAULT_LANGUAGE) {
    url.searchParams.set(LANG_QUERY_PARAM, targetLang);
  } else {
    url.searchParams.delete(LANG_QUERY_PARAM);
  }

  return url.toString();
}

/**
 * Crée le sélecteur de langue dans le DOM
 */
export function createLanguageSelector(containerId = 'language-selector-container') {
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn('Container du sélecteur de langue introuvable');
    return;
  }

  const currentLang = getCurrentLanguage();

  const selector = document.createElement('div');
  selector.className = 'language-selector';

  SUPPORTED_LANGUAGES.forEach(lang => {
    const btn = document.createElement('button');
    btn.className = `language-btn ${lang === currentLang ? 'active' : ''}`;
    btn.textContent = LANGUAGE_NAMES[lang];
    btn.title = `Changer en ${LANGUAGE_NAMES[lang]}`;
    btn.onclick = () => setCurrentLanguage(lang);
    selector.appendChild(btn);
  });

  container.appendChild(selector);
}

/**
 * Initialise le système de langue
 * - Détecte la langue (queryParam > cache > navigateur)
 * - Met à jour l'URL si nécessaire
 * - Crée le sélecteur si le container existe
 */
export function initLanguageSystem() {
  const currentLang = getCurrentLanguage();
  console.log(`[Language] Langue active: ${currentLang.toUpperCase()}`);

  // S'assurer que l'URL reflète la langue (retirer ?lang=fr si présent)
  updateUrlLanguageParam(currentLang);

  // Créer le sélecteur si le container existe
  if (document.getElementById('language-selector-container')) {
    createLanguageSelector();
  }

  return currentLang;
}

/**
 * Retourne la langue par défaut
 */
export function getDefaultLanguage() {
  return DEFAULT_LANGUAGE;
}

/**
 * Retourne les langues supportées
 */
export function getSupportedLanguages() {
  return [...SUPPORTED_LANGUAGES];
}

// Export pour usage global
window.D2Language = {
  getCurrentLanguage,
  setCurrentLanguage,
  createLanguageSelector,
  initLanguageSystem,
  buildUrlWithLang,
  getDefaultLanguage,
  getSupportedLanguages,
  LANG_QUERY_PARAM
};