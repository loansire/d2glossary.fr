/* itemListPage.js - Gestion des pages de liste d'items avec recherche multilingue */
import {
  loadHTML,
  loadJSON,
  getUrlParam,
  getBungieIconUrl,
  debounce
} from './utils.js';
import { openPopupItem } from './popupitem.js';
import { loadDDCVacuumData } from './ddcvacuum.js';
import { Pagination } from './pagination.js';
import { createSearchIndex, searchWithIndex, loadOtherLanguageData } from './multilingualSearch.js';

/**
 * Accède à une valeur imbriquée via dot notation
 * Ex: getNestedValue(item, 'plug.plugCategoryIdentifier')
 *     → item.plug.plugCategoryIdentifier
 * @param {Object} obj - Objet source
 * @param {string} path - Chemin en dot notation
 * @returns {*} Valeur trouvée ou undefined
 */
function getNestedValue(obj, path) {
  if (!obj || !path) return undefined;
  // Clé directe (pas de point) → accès simple, plus rapide
  if (!path.includes('.')) return obj[path];
  return path.split('.').reduce((acc, key) => acc?.[key], obj);
}

export async function loadItemListPage({
  dataFile,
  excludedIds = [],
  containerId,
  inputId,
  filterOptions = {},
  excludeOptions = {},
  itemsPerPage = 50
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  const resultCount = document.getElementById('result-count');
  const clearButton = document.getElementById('clear-button');
  const popupContainer = document.getElementById('popupitem-container');
  const banniereContainer = document.getElementById('banniere-container');

  let pagination = null;
  let allFilteredItems = [];
  let searchIndex = null;
  let currentData = null;

  // Charger les composants HTML et DDCVacuum en parallèle
  await Promise.all([
    loadHTML('assets/html/popupitem.html', popupContainer),
    loadHTML('assets/html/banniere.html', banniereContainer),
    loadDDCVacuumData()
  ]);

  try {
    const filename = dataFile.split('/').pop();
    const currentLang = dataFile.includes('/fr/') ? 'fr' : 'en';

    // Charger les données principales ET l'autre langue en parallèle
    const [data, otherLangData] = await Promise.all([
      loadJSON(dataFile),
      loadOtherLanguageData(currentLang, filename)
    ]);

    if (!data) throw new Error('Données non chargées');

    currentData = data;

    // Créer l'index de recherche multilingue
    console.log('[MultilingualSearch] Création de l\'index de recherche...');
    searchIndex = createSearchIndex(data, otherLangData);
    console.log(`[MultilingualSearch] Index créé avec ${searchIndex.size} entrées`);

    // Filtrer les items une seule fois
    allFilteredItems = Object.entries(data).filter(([id, item]) => {
      const props = item.displayProperties;

      // === FILTER OPTIONS (inclusion) ===
      const matchesCategoryHash = () => {
        const filterHash = filterOptions.itemCategoryHash;
        if (!filterHash) return true;
        if (!Array.isArray(item.itemCategoryHashes)) return false;

        if (typeof filterHash === 'number') {
          return item.itemCategoryHashes.includes(filterHash);
        }

        if (Array.isArray(filterHash)) {
          return filterHash.every(hash => item.itemCategoryHashes.includes(hash));
        }

        return false;
      };

      // === FILTRAGE GÉNÉRIQUE PAR CLÉS (supporte dot notation) ===
      const matchesGenericFilters = () => {
        for (const [key, expected] of Object.entries(filterOptions)) {
          // Ignorer itemCategoryHash, traité séparément
          if (key === 'itemCategoryHash') continue;

          const value = getNestedValue(item, key);

          // Si expected est un array → la valeur doit être dedans (OR)
          if (Array.isArray(expected)) {
            if (!expected.includes(value)) return false;
          } else {
            if (value !== expected) return false;
          }
        }
        return true;
      };

      // === EXCLUDE OPTIONS (exclusion) ===
      const passesExcludeOptions = () => {
        // excludeIfExists: exclure si la clé existe (supporte dot notation)
        if (excludeOptions.excludeIfExists) {
          const keysToCheck = Array.isArray(excludeOptions.excludeIfExists)
            ? excludeOptions.excludeIfExists
            : [excludeOptions.excludeIfExists];

          for (const key of keysToCheck) {
            const val = getNestedValue(item, key);
            if (val !== undefined && val !== null) {
              return false;
            }
          }
        }

        // excludeIfEquals: exclure si la clé a une valeur spécifique (supporte dot notation)
        if (excludeOptions.excludeIfEquals) {
          for (const [key, value] of Object.entries(excludeOptions.excludeIfEquals)) {
            if (getNestedValue(item, key) === value) {
              return false;
            }
          }
        }

        // excludeIfIncludes: exclure si un array contient une valeur (supporte dot notation)
        if (excludeOptions.excludeIfIncludes) {
          for (const [key, values] of Object.entries(excludeOptions.excludeIfIncludes)) {
            const itemArray = getNestedValue(item, key);
            if (!Array.isArray(itemArray)) continue;

            const valuesToCheck = Array.isArray(values) ? values : [values];
            for (const val of valuesToCheck) {
              if (itemArray.includes(val)) {
                return false;
              }
            }
          }
        }

        // excludeIfNotEquals: exclure si la clé N'A PAS une valeur (supporte dot notation)
        if (excludeOptions.excludeIfNotEquals) {
          for (const [key, value] of Object.entries(excludeOptions.excludeIfNotEquals)) {
            if (getNestedValue(item, key) !== value) {
              return false;
            }
          }
        }

        return true;
      };

      return (
        props?.name &&
        props?.description &&
        props?.icon &&
        !excludedIds.includes(id) &&
        matchesCategoryHash() &&
        matchesGenericFilters() &&
        passesExcludeOptions()
      );
    });

    // Créer le renderer d'item
    const renderItem = ([id, item]) => {
      const props = item.displayProperties;
      const card = document.createElement('div');
      card.className = 'card-item';
      card.title = props.name;

      card.innerHTML = `
        <img src="${getBungieIconUrl(props.icon)}" alt="d2glossary - ${props.name}" loading="lazy" />
        <div>${props.name}</div>
      `;
      card.onclick = () => openPopupItem(id, item);
      return card;
    };

    // Initialiser la pagination
    pagination = new Pagination({
      container,
      items: allFilteredItems,
      itemsPerPage,
      renderItem
    });

    updateResultCount(allFilteredItems);
    pagination.render();

    // Gestion de l'URL avec ID
    const itemId = getUrlParam('id');
    if (itemId && data[itemId]) {
      openPopupItem(itemId, data[itemId]);
    }

    // Gestion de la recherche MULTILINGUE avec debounce
    const handleSearch = debounce((query) => {
      if (!query) {
        updateResultCount(allFilteredItems);
        pagination.setItems(allFilteredItems);
        return;
      }

      const allMatches = searchWithIndex(query, searchIndex, currentData);

      const filteredResults = allMatches.filter(([id]) =>
        allFilteredItems.some(([filteredId]) => filteredId === id)
      );

      updateResultCount(filteredResults);
      pagination.setItems(filteredResults);
    }, 150);

    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      handleSearch(query);
      clearButton.style.display = e.target.value ? 'block' : 'none';
    });

    clearButton?.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      updateResultCount(allFilteredItems);
      pagination.setItems(allFilteredItems);
    });

    function updateResultCount(list) {
      resultCount.textContent = `Résultats trouvés: ${list.length}`;
    }

  } catch (err) {
    console.error('Erreur lors du chargement des données:', err);
    container.innerHTML = `
      <div class="error-message">
        <h3>⚠️ Erreur de chargement</h3>
        <p>${err.message}</p>
      </div>
    `;
  }
}

// Export de getNestedValue pour réutilisation dans d'autres modules
export { getNestedValue };