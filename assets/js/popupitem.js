/* popupitem.js - Gestion des popups d'items avec DDCVacuum */
import {
  processDescription,
  parseKeywords,
  boldPatterns,
  normalizeName,
  setUrlParam,
  removeUrlParam,
  getCurrentUrl,
  copyToClipboard,
  getBungieIconUrl,
  onEscapeKey,
  loadJSON
} from './utils.js';

const DDCVACUUM_URL = 'data/ddcvacuum.json';

// Stockage du nom FR pour l'emoji Discord
let currentItemFrName = null;

// Cache DDCVacuum
let ddcvacuumCache = null;

// === DDCVACUUM FUNCTIONS (exportées pour réutilisation) ===

/**
 * Charge les données DDCVacuum (avec cache)
 */
export async function loadDDCVacuumData() {
  if (ddcvacuumCache) return ddcvacuumCache;

  // Essayer le cache mémoire du dataManager d'abord
  if (window.D2DataManager?.getFromMemoryCache) {
    const cached = window.D2DataManager.getFromMemoryCache(DDCVACUUM_URL);
    if (cached) {
      ddcvacuumCache = cached;
      return ddcvacuumCache;
    }
  }

  // Sinon charger
  ddcvacuumCache = await loadJSON(DDCVACUUM_URL);
  return ddcvacuumCache;
}

/**
 * Récupère les données DDCVacuum depuis le cache
 */
export function getDDCVacuumData() {
  if (ddcvacuumCache) return ddcvacuumCache;

  if (window.D2DataManager?.getFromMemoryCache) {
    return window.D2DataManager.getFromMemoryCache(DDCVACUUM_URL);
  }
  return null;
}

/**
 * Gère l'affichage des fades selon la position du scroll
 */
export function updateDDCVacuumFades() {
  const ddcvacuumEl = document.getElementById('popupitem-ddcvacuum');
  const wrapper = document.getElementById('ddcvacuum-wrapper');

  if (!ddcvacuumEl || !wrapper) return;

  const scrollTop = ddcvacuumEl.scrollTop;
  const scrollHeight = ddcvacuumEl.scrollHeight;
  const clientHeight = ddcvacuumEl.clientHeight;
  const scrollBottom = scrollHeight - scrollTop - clientHeight;
  const threshold = 5;

  wrapper.classList.toggle('can-scroll-up', scrollTop > threshold);
  wrapper.classList.toggle('can-scroll-down', scrollBottom > threshold);
}

/**
 * Initialise les listeners pour le scroll de DDCVacuum
 */
export function initDDCVacuumScrollListeners() {
  const ddcvacuumEl = document.getElementById('popupitem-ddcvacuum');
  if (!ddcvacuumEl) return;

  ddcvacuumEl.addEventListener('scroll', updateDDCVacuumFades);
  setTimeout(updateDDCVacuumFades, 100);
}

/**
 * Nettoie les listeners DDCVacuum
 */
export function cleanupDDCVacuumListeners() {
  const ddcvacuumEl = document.getElementById('popupitem-ddcvacuum');
  if (ddcvacuumEl) {
    ddcvacuumEl.removeEventListener('scroll', updateDDCVacuumFades);
  }
}

/**
 * Rendu de la section DDCVacuum dans le popup
 * @param {Object} item - Données DDCVacuum de l'item (ddcvacuum[id])
 */
export function renderDDCVacuumInPopup(item) {
  const ddcvacuumEl = document.getElementById('popupitem-ddcvacuum');
  const ddcvacuumWrapper = document.getElementById('ddcvacuum-wrapper');
  const ddcvacuumSeparator = document.getElementById('ddcvacuum-separator');

  if (!ddcvacuumEl || !ddcvacuumWrapper || !ddcvacuumSeparator) return;

  ddcvacuumEl.innerHTML = '';

  if (!item?.descriptions?.en?.length) {
    ddcvacuumWrapper.classList.add('hidden');
    ddcvacuumSeparator.classList.add('hidden');
    return;
  }

  // Header avec lien D2DDCVacuum
  const header = document.createElement('div');
  header.style.cssText = 'display:flex;align-items:center;margin-bottom:1rem;color:#aaa';
  header.innerHTML = `
    <p style="margin:0">
      Informations exportées depuis
      <a href="https://docs.google.com/spreadsheets/d/1WaxvbLx7UoSZaBqdFr1u32F2uWVLo-CJunJB4nlGUE4" target="_blank" style="display:inline-flex;align-items:center;vertical-align:middle">
        <img src="https://ssl.gstatic.com/docs/doclist/images/mediatype/icon_1_spreadsheet_x16.png" alt="Google Sheets" style="height:16px;width:16px;margin:0 0.25rem">
        Destiny Data Compendium
      </a>
      (Anglais uniquement)
    </p>
  `;
  ddcvacuumEl.appendChild(header);

  // Contenu
  item.descriptions.en.forEach(section => {
    if (section.linesContent) {
      const p = document.createElement('p');
      section.linesContent.forEach(line => {
        let el;
        if (line.link) {
          el = document.createElement('a');
          el.href = line.link;
          el.target = '_blank';
          el.innerHTML = boldPatterns(line.text || '');
        } else {
          el = document.createElement('span');
          el.innerHTML = boldPatterns(line.text || '');
        }
        line.classNames?.forEach(cls => el.classList.add(cls));
        p.appendChild(el);
        p.append(' ');
      });
      ddcvacuumEl.appendChild(p);
    } else if (section.classNames?.includes('spacer')) {
      const spacer = document.createElement('div');
      spacer.style.margin = '0.8rem 0';
      ddcvacuumEl.appendChild(spacer);
    }
  });

  ddcvacuumWrapper.classList.remove('hidden');
  ddcvacuumSeparator.classList.remove('hidden');

  // Initialiser les listeners de scroll après le rendu
  setTimeout(initDDCVacuumScrollListeners, 50);
}

/**
 * Masque la section DDCVacuum
 */
export function hideDDCVacuumSection() {
  document.getElementById('ddcvacuum-wrapper')?.classList.add('hidden');
  document.getElementById('ddcvacuum-separator')?.classList.add('hidden');
}

/**
 * Affiche DDCVacuum pour un ID donné (charge les données si nécessaire)
 * @param {string} id - ID de l'item
 */
export async function showDDCVacuumForItem(id) {
  let ddcvacuumData = getDDCVacuumData();

  // Si pas en cache, essayer de charger
  if (!ddcvacuumData) {
    ddcvacuumData = await loadDDCVacuumData();
  }

  if (ddcvacuumData && ddcvacuumData[id]) {
    renderDDCVacuumInPopup(ddcvacuumData[id]);
  } else {
    hideDDCVacuumSection();
  }
}

/**
 * Récupère le nom français d'un item pour l'emoji Discord
 */
async function fetchFrenchName(id) {
  try {
    const frDataUrl = `data/fr/item_definitions.json`;
    let frData = window.D2DataManager?.getFromMemoryCache?.(frDataUrl);

    if (!frData) {
      const response = await fetch(frDataUrl);
      if (response.ok) {
        frData = await response.json();
      }
    }

    if (frData?.[id]?.displayProperties?.name) {
      return frData[id].displayProperties.name;
    }

    return null;
  } catch (err) {
    console.warn('[PopupItem] Impossible de charger le nom français:', err);
    return null;
  }
}

// === POPUP FUNCTIONS ===
export async function openPopupItem(id, item) {
  const iconEl = document.getElementById('popupitem-icon');
  const nameEl = document.getElementById('popupitem-name');
  const descEl = document.getElementById('popupitem-description');
  const idEl = document.getElementById('popupitem-id');
  const popup = document.getElementById('popupitem');

  // Masquer la section setarmor par défaut
  document.getElementById('setarmor-separator')?.classList.add('hidden');
  document.getElementById('popupitem-setarmor')?.classList.add('hidden');

  const props = item.displayProperties;
  iconEl.src = getBungieIconUrl(props.icon);
  iconEl.alt = `d2glossary - ${props.name}`;
  nameEl.textContent = props.name;

  // Détecter la langue et traiter la description
  const currentLang = window.D2Language?.getCurrentLanguage?.() || 'fr';
  const finalDescription = parseKeywords(
    processDescription(props.description),
    currentLang
  );
  descEl.innerHTML = finalDescription;

  // Afficher DDCVacuum si disponible
  await showDDCVacuumForItem(id);

  idEl.textContent = `ID: ${id}`;

  // Récupérer le nom français pour l'emoji Discord
  if (currentLang === 'en') {
    currentItemFrName = await fetchFrenchName(id);
  } else {
    currentItemFrName = props.name;
  }

  popup.classList.add('show');
  document.body.classList.add('popupitem-open');

  setUrlParam('id', id);

  popup.onclick = (e) => {
    if (e.target.id === 'popupitem') closePopupItem();
  };
}

export function closePopupItem() {
  const popup = document.getElementById('popupitem');
  popup?.classList.remove('show');
  document.body.classList.remove('popupitem-open');
  removeUrlParam('id');
  currentItemFrName = null;

  // Nettoyer les listeners
  cleanupDDCVacuumListeners();
}

// === SHARE FUNCTIONS ===
export function sharePopupItem() {
  const url = getCurrentUrl();
  copyToClipboard(url, 'Lien copié dans le presse-papier :\n' + url);
}

export function copyDiscordMarkdown() {
  const displayName = document.getElementById('popupitem-name')?.textContent.trim();
  const url = getCurrentUrl();
  const iconSwitch = document.getElementById('iconSwitch');
  const iconEnabled = iconSwitch?.checked;

  let markdown = `[${displayName}](<${url}>)`;

  if (iconEnabled && currentItemFrName) {
    const cleanFrName = normalizeName(currentItemFrName);
    markdown = `:${cleanFrName}: ${markdown}`;
  }

  copyToClipboard(markdown, 'Lien Discord copié dans le presse-papier:\n' + markdown);
}

/**
 * Met à jour le nom FR stocké (pour les pages qui gèrent leur propre popup)
 */
export function setCurrentItemFrName(name) {
  currentItemFrName = name;
}

/**
 * Récupère le nom FR stocké
 */
export function getCurrentItemFrName() {
  return currentItemFrName;
}

// === GLOBAL BINDINGS ===
window.openPopupItem = openPopupItem;
window.closePopupItem = closePopupItem;
window.sharePopupItem = sharePopupItem;
window.copyDiscordMarkdown = copyDiscordMarkdown;

onEscapeKey(closePopupItem);

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('discord-btn')?.addEventListener('click', copyDiscordMarkdown);
});