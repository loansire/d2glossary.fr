/* ddcvacuum.js - Gestion des données DDCVacuum (Destiny Data Compendium) */
import { loadJSON, boldPatterns } from './utils.js';

const DDCVACUUM_URL = 'data/ddcvacuum.json';

// Cache DDCVacuum
let ddcvacuumCache = null;

// === DATA FUNCTIONS ===

/**
 * Transforme la structure par catégories en index par hash
 * @param {Object} rawData - Données brutes avec catégories (WeaponPerks, WeaponMods, etc.)
 * @returns {Object} Index avec hash comme clé
 */
function indexByHash(rawData) {
  const indexed = {};

  // Parcourir toutes les catégories
  for (const category of Object.values(rawData)) {
    // Vérifier que c'est un tableau
    if (!Array.isArray(category)) continue;

    // Indexer chaque item par son hash
    for (const item of category) {
      if (item.hash) {
        indexed[String(item.hash)] = item;
      }
    }
  }

  console.log(`[DDCVacuum] Index créé avec ${Object.keys(indexed).length} entrées`);
  return indexed;
}

/**
 * Charge les données DDCVacuum (avec cache)
 */
export async function loadDDCVacuumData() {
  if (ddcvacuumCache) return ddcvacuumCache;

  // Essayer le cache mémoire du dataManager d'abord
  if (window.D2DataManager?.getFromMemoryCache) {
    const cached = window.D2DataManager.getFromMemoryCache(DDCVACUUM_URL);
    if (cached) {
      // Transformer si nécessaire (si c'est la nouvelle structure)
      ddcvacuumCache = isNewStructure(cached) ? indexByHash(cached) : cached;
      return ddcvacuumCache;
    }
  }

  // Sinon charger
  const rawData = await loadJSON(DDCVACUUM_URL);
  if (rawData) {
    // Transformer si c'est la nouvelle structure
    ddcvacuumCache = isNewStructure(rawData) ? indexByHash(rawData) : rawData;
  }
  return ddcvacuumCache;
}

/**
 * Vérifie si les données utilisent la nouvelle structure (par catégories)
 */
function isNewStructure(data) {
  if (!data) return false;
  // Nouvelle structure : contient des clés comme "WeaponPerks", "WeaponMods" avec des tableaux
  const firstKey = Object.keys(data)[0];
  return Array.isArray(data[firstKey]);
}

/**
 * Récupère les données DDCVacuum depuis le cache
 */
export function getDDCVacuumData() {
  if (ddcvacuumCache) return ddcvacuumCache;

  if (window.D2DataManager?.getFromMemoryCache) {
    const cached = window.D2DataManager.getFromMemoryCache(DDCVACUUM_URL);
    if (cached) {
      // Transformer si nécessaire
      ddcvacuumCache = isNewStructure(cached) ? indexByHash(cached) : cached;
      return ddcvacuumCache;
    }
  }
  return null;
}

// === SCROLL/UI FUNCTIONS ===

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

// === RENDER FUNCTIONS ===

/**
 * Rendu de la section DDCVacuum dans le popup
 * @param {Object} item - Données DDCVacuum de l'item
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
  header.style.cssText = 'align-items:center;margin-bottom:1rem;color:#aaa';
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

  // Convertir l'ID en string pour la recherche
  const idStr = String(id);

  if (ddcvacuumData && ddcvacuumData[idStr]) {
    renderDDCVacuumInPopup(ddcvacuumData[idStr]);
  } else {
    hideDDCVacuumSection();
  }
}