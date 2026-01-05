/* languageSelector.js - Gestion du sélecteur de langue */

const LANG_STORAGE_KEY = 'd2glossary_language';
const SUPPORTED_LANGUAGES = ['fr', 'en'];
const LANGUAGE_NAMES = {
  'fr': 'FR',
  'en': 'EN'
};

/**
 * Récupère la langue active (stockée ou détectée)
 */
export function getCurrentLanguage() {
  // 1. Vérifier le localStorage
  const stored = localStorage.getItem(LANG_STORAGE_KEY);
  if (stored && SUPPORTED_LANGUAGES.includes(stored)) {
    return stored;
  }

  // 2. Détecter depuis le navigateur
  const browserLang = navigator.language.split('-')[0];
  const detected = SUPPORTED_LANGUAGES.includes(browserLang) ? browserLang : 'fr';

  // Sauvegarder la détection
  localStorage.setItem(LANG_STORAGE_KEY, detected);
  return detected;
}

/**
 * Change la langue active
 */
export function setCurrentLanguage(lang) {
  if (!SUPPORTED_LANGUAGES.includes(lang)) {
    console.error(`Langue non supportée: ${lang}`);
    return false;
  }

  localStorage.setItem(LANG_STORAGE_KEY, lang);
  console.log(`[Language] Langue changée: ${lang.toUpperCase()}`);

  // Recharger la page pour appliquer la nouvelle langue
  window.location.reload();
  return true;
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
 */
export function initLanguageSystem() {
  const currentLang = getCurrentLanguage();
  console.log(`[Language] Langue active: ${currentLang.toUpperCase()}`);

  // Créer le sélecteur si le container existe
  if (document.getElementById('language-selector-container')) {
    createLanguageSelector();
  }

  return currentLang;
}

// Export pour usage global
window.D2Language = {
  getCurrentLanguage,
  setCurrentLanguage,
  createLanguageSelector,
  initLanguageSystem
};