/* itemListPage.js - Gestion des pages de liste d'items avec recherche multilingue */
import {
  loadHTML,
  loadJSON,
  getUrlParam,
  getBungieIconUrl,
  debounce
} from './utils.js';
import { openPopupItem, loadDDCVacuumData } from './popupitem.js';
import { Pagination } from './pagination.js';
import { createSearchIndex, searchWithIndex, loadOtherLanguageData } from './multilingualSearch.js';

export async function loadItemListPage({
  dataFile,
  excludedIds = [],
  containerId,
  inputId,
  filterOptions = {},
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
    loadDDCVacuumData() // Précharger DDCVacuum via la fonction centralisée
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

      return (
        props?.name &&
        props?.description &&
        props?.icon &&
        !excludedIds.includes(id) &&
        matchesCategoryHash() &&
        (filterOptions.itemType === undefined || item.itemType === filterOptions.itemType) &&
        (filterOptions.itemSubType === undefined || item.itemSubType === filterOptions.itemSubType) &&
        (filterOptions.classType === undefined || item.classType === filterOptions.classType) &&
        (filterOptions.breakerType === undefined || item.breakerType === filterOptions.breakerType)
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