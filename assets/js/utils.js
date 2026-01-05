/* utils.js - Fonctions utilitaires partagées */

// Importer les définitions de mots-clés
import { getReplacements } from './keywordReplacements.js';

// === CONSTANTS ===
export const BUNGIE_BASE_URL = 'https://www.bungie.net';

// Fichiers lourds nécessitant un loader
const HEAVY_FILES = [
  'data/fr/item_definitions.json',
  'data/en/item_definitions.json',
  'data/clarity.json'
];

// === DOM HELPERS ===

/**
 * Charge un fichier HTML et l'injecte dans un élément cible
 */
export async function loadHTML(url, target) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    if (typeof target === 'string') {
      target = document.getElementById(target);
    }
    if (target) {
      target.innerHTML = html;
    }
    return html;
  } catch (err) {
    console.error(`Erreur chargement HTML (${url}):`, err);
    return null;
  }
}

/**
 * Charge un fichier JSON avec gestion intelligente du cache
 * Utilise le dataManager si disponible, sinon fetch classique
 */
export async function loadJSON(url) {
  // Vérifier si dataManager est disponible
  if (window.D2DataManager?.loadJSONWithCache) {
    const isHeavy = HEAVY_FILES.some(f => url.includes(f));
    return window.D2DataManager.loadJSONWithCache(url, {
      showProgress: isHeavy,
      progressMessage: getLoadingMessage(url)
    });
  }

  // Fallback classique
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Erreur chargement JSON (${url}):`, err);
    return null;
  }
}

/**
 * Retourne un message de chargement adapté au fichier
 */
function getLoadingMessage(url) {
  if (url.includes('item_definitions')) return 'Chargement des définitions...';
  if (url.includes('clarity')) return 'Chargement des données Clarity...';
  if (url.includes('trait')) return 'Chargement des traits...';
  if (url.includes('modifier')) return 'Chargement des modificateurs...';
  if (url.includes('setarmor')) return 'Chargement des sets d\'armure...';
  if (url.includes('artefact')) return 'Chargement de l\'artefact...';
  return 'Chargement des données...';
}

/**
 * Échappe les caractères HTML
 */
export function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// === TEXT PROCESSING ===

/**
 * Traite la description pour le formatage
 */
export function processDescription(text) {
  if (!text) return '';
  return text
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '25')
    .replace(/ ?•/g, '<br>•')
    .replace(/\.\s*(?=[A-ZÉÈÀÂÎÔÙÜÇ])/g, '.<br>')
    .replace(/(<br>\s*){2,}/g, '<br>')
    .trim();
}

/**
 * Remplace les patterns numériques par du texte en gras
 */
export function boldPatterns(text) {
  if (!text) return '';
  text = text.replace(/[\u200B-\u200D\u2060\uFEFF]/g, '');
  const pattern = /(\d+(\.\d+)?)([x%])?/g;
  return text.replace(pattern, '<strong>$&</strong>');
}

/**
 * Parse les mots-clés Destiny 2 et les remplace par des icônes
 * @param {string} text - Texte à traiter
 * @param {string} lang - Langue ('fr' ou 'en')
 * @returns {string} Texte avec icônes
 */
export function parseKeywords(text, lang = null) {
  if (!text) return '';

  // Détecter la langue si non fournie
  if (!lang) {
    lang = window.D2Language?.getCurrentLanguage?.() || 'fr';
  }

  const replacements = getReplacements(lang);

  for (const [key, className] of Object.entries(replacements)) {
    const regex = new RegExp(`\\[${key}\\](\\s*)(\\w+)`, 'gi'); // Ajout du flag 'i' pour insensible à la casse
    text = text.replace(
      regex,
      `<span class="icon-word"><span class="${className}"></span>&nbsp;$2</span>`
    );
  }
  return text;
}

/**
 * Normalise un nom (retire espaces, accents, caractères spéciaux)
 */
export function normalizeName(name) {
  if (!name) return '';
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, '')
    .replace(/[^a-zA-Z0-9]/g, '');
}

// === URL HELPERS ===

/**
 * Récupère un paramètre de l'URL
 */
export function getUrlParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

/**
 * Met à jour un paramètre de l'URL sans recharger la page
 */
export function setUrlParam(param, value) {
  const url = new URL(window.location);
  if (value === null || value === undefined) {
    url.searchParams.delete(param);
  } else {
    url.searchParams.set(param, value);
  }
  history.replaceState(null, '', url);
}

/**
 * Supprime un paramètre de l'URL
 */
export function removeUrlParam(param) {
  setUrlParam(param, null);
}

/**
 * Récupère l'URL complète actuelle
 */
export function getCurrentUrl() {
  return window.location.href;
}

// === CLIPBOARD ===

/**
 * Copie du texte dans le presse-papier avec notification
 */
export async function copyToClipboard(text, successMessage = null) {
  try {
    await navigator.clipboard.writeText(text);
    if (successMessage) {
      alert(successMessage);
    }
    return true;
  } catch (err) {
    alert('Erreur lors de la copie : ' + err);
    return false;
  }
}

// === BUNGIE HELPERS ===

/**
 * Construit l'URL complète d'une icône Bungie
 */
export function getBungieIconUrl(iconPath) {
  if (!iconPath) return '';
  if (iconPath.startsWith('http')) return iconPath;
  return BUNGIE_BASE_URL + iconPath;
}

// === LANGUAGE DETECTION ===

/**
 * Détecte la langue du navigateur
 * @param {string[]} supportedLangs - Langues supportées
 * @param {string} defaultLang - Langue par défaut
 * @returns {string} Code de langue détecté
 */
export function detectLanguage(supportedLangs = ['fr', 'en'], defaultLang = 'fr') {
  // Si le module languageSelector est chargé, l'utiliser
  if (window.D2Language?.getCurrentLanguage) {
    return window.D2Language.getCurrentLanguage();
  }

  // Sinon, détection classique
  const browserLang = navigator.language.split('-')[0];
  return supportedLangs.includes(browserLang) ? browserLang : defaultLang;
}

// === EVENT HELPERS ===

/**
 * Ajoute un gestionnaire d'événement pour la touche Escape
 */
export function onEscapeKey(callback) {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') callback(e);
  });
}

/**
 * Debounce une fonction
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}