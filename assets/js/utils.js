/* utils.js - Fonctions utilitaires partagées */

// === CONSTANTS ===
export const BUNGIE_BASE_URL = 'https://www.bungie.net';

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
 * Charge un fichier JSON
 */
export async function loadJSON(url) {
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
 * - Remplace {var:xxx} par 25
 * - Ajoute des sauts de ligne avant les puces
 * - Ajoute des sauts de ligne après les points suivis de majuscules
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
 */
export function parseKeywords(text) {
  if (!text) return '';

  const replacements = {
    'Solaire': 'solar',
    'Filobscur': 'strand',
    'Chancellement': 'unstoppable',
    'Perforation de bouclier': 'barrier',
    'Perturbation': 'overload',
    'Stase': 'stasis',
    'Abyssal': 'void',
    'Cryo-électrique': 'arc',
    'Primaire': 'primary',
    'Spéciale': 'special',
    'Lourde': 'heavy',
    'PVE': 'pve',
    'PVP': 'pvp',
    'Chasseur': 'hunter',
    'Arcaniste': 'warlock',
    'Titan': 'titan'
  };

  for (const [key, className] of Object.entries(replacements)) {
    const regex = new RegExp(`\\[${key}\\](\\s*)(\\w+)`, 'g');
    text = text.replace(
      regex,
      `<span class="icon-word"><span class="${className}"></span>&nbsp;$2</span>`
    );
  }
  return text;
}

/**
 * Normalise un nom (retire espaces, accents, caractères spéciaux)
 * Utile pour les emojis Discord
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

// === ARRAY HELPERS ===

/**
 * Mélange un tableau de façon aléatoire
 */
export function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
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