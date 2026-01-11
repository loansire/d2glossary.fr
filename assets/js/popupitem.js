/* popupitem.js - Gestion des popups d'items */
import {
  processDescription,
  parseKeywords,
  normalizeName,
  setUrlParam,
  removeUrlParam,
  getCurrentUrl,
  copyToClipboard,
  getBungieIconUrl,
  onEscapeKey
} from './utils.js';
import {
  loadDDCVacuumData,
  getDDCVacuumData,
  renderDDCVacuumInPopup,
  hideDDCVacuumSection,
  showDDCVacuumForItem,
  cleanupDDCVacuumListeners
} from './ddcvacuum.js';

// Ré-exporter les fonctions DDCVacuum pour compatibilité avec les imports existants
export {
  loadDDCVacuumData,
  getDDCVacuumData,
  renderDDCVacuumInPopup,
  hideDDCVacuumSection,
  showDDCVacuumForItem,
  cleanupDDCVacuumListeners
} from './ddcvacuum.js';

// Stockage du nom FR pour l'emoji Discord
let currentItemFrName = null;

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