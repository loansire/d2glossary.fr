/* popupitem.js - Gestion des popups d'items */
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
  onEscapeKey
} from './utils.js';

const CLARITY_URL = 'data/clarity.json';

// Stockage du nom FR pour l'emoji Discord
let currentItemFrName = null;

/**
 * Récupère les données Clarity depuis le cache mémoire
 */
function getClarityData() {
  if (window.D2DataManager?.getFromMemoryCache) {
    return window.D2DataManager.getFromMemoryCache(CLARITY_URL);
  }
  return null;
}

// === CLARITY RENDERING ===
function renderClarityInPopup(item) {
  const clarityEl = document.getElementById('popupitem-clarity');
  const clarityWrapper = document.getElementById('clarity-wrapper');
  const claritySeparator = document.getElementById('clarity-separator');

  clarityEl.innerHTML = '';

  if (!item?.descriptions?.en?.length) {
    clarityWrapper.classList.add('hidden');
    claritySeparator.classList.add('hidden');
    return;
  }

  // Header avec lien D2Clarity
  const header = document.createElement('div');
  header.style.cssText = 'display:flex;align-items:center;margin-bottom:1rem;color:#aaa';
  header.innerHTML = `
    <p style="margin:0">
      Informations délivrées par
      <a href="https://www.d2clarity.com" target="_blank" style="display:inline-flex;align-items:center;vertical-align:middle">
        <img src="https://www.d2clarity.com/web/image/website/1/favicon?unique=0d61ed2" alt="D2Clarity" style="height:25px;width:25px;margin:0 0.1rem">
        D2Clarity
      </a>
      (Anglais uniquement)
    </p>
  `;
  clarityEl.appendChild(header);

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
      clarityEl.appendChild(p);
    } else if (section.classNames?.includes('spacer')) {
      const spacer = document.createElement('div');
      spacer.style.margin = '1rem 0';
      clarityEl.appendChild(spacer);
    }
  });

  clarityWrapper.classList.remove('hidden');
  claritySeparator.classList.remove('hidden');
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

  // Charger les données Clarity depuis le cache mémoire
  const clarityData = getClarityData();
  if (clarityData) {
    renderClarityInPopup(clarityData[id]);
  } else {
    document.getElementById('clarity-wrapper')?.classList.add('hidden');
    document.getElementById('clarity-separator')?.classList.add('hidden');
  }

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

// === GLOBAL BINDINGS ===
window.openPopupItem = openPopupItem;
window.closePopupItem = closePopupItem;
window.sharePopupItem = sharePopupItem;
window.copyDiscordMarkdown = copyDiscordMarkdown;

onEscapeKey(closePopupItem);

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('discord-btn')?.addEventListener('click', copyDiscordMarkdown);
});