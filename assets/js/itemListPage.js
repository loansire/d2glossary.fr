/* itemListPage.js - Gestion des pages de liste d'items */
import { 
  loadHTML, 
  loadJSON, 
  getUrlParam, 
  getBungieIconUrl,
  debounce
} from './utils.js';
import { openPopupItem } from './popupitem.js';
import { Pagination } from './pagination.js';

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

  // Charger les composants HTML en parallèle
  await Promise.all([
    loadHTML('assets/html/popupitem.html', popupContainer),
    loadHTML('assets/html/banniere.html', banniereContainer)
  ]);

  try {
    // Charger les données principales ET clarity.json en parallèle
    const [data] = await Promise.all([
      loadJSON(dataFile),
      loadJSON('data/clarity.json') // Précharge clarity pour les popups
    ]);

    if (!data) throw new Error('Données non chargées');

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

    // Gestion de la recherche avec debounce
    const handleSearch = debounce((query) => {
      const filteredResults = query
        ? allFilteredItems.filter(([_, item]) =>
            item.displayProperties.name.toLowerCase().includes(query)
          )
        : allFilteredItems;

      updateResultCount(filteredResults);
      pagination.setItems(filteredResults);
    }, 150);

    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      handleSearch(query);
      clearButton.style.display = e.target.value ? 'block' : 'none';
    });

    // Bouton clear
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