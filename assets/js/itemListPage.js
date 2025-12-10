/* itemListPage.js - Gestion des pages de liste d'items */
import { 
  loadHTML, 
  loadJSON, 
  getUrlParam, 
  getBungieIconUrl,
  shuffleArray 
} from './utils.js';
import { openPopupItem } from './popupitem.js';

export async function loadItemListPage({
  dataFile,
  excludedIds = [],
  containerId,
  inputId,
  filterOptions = {}
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  const resultCount = document.getElementById('result-count');
  const clearButton = document.getElementById('clear-button');
  const popupContainer = document.getElementById('popupitem-container');
  const banniereContainer = document.getElementById('banniere-container');

  // Charger les composants HTML
  await loadHTML('assets/html/popupitem.html', popupContainer);
  await loadHTML('assets/html/banniere.html', banniereContainer);

  try {
    const data = await loadJSON(dataFile);
    if (!data) throw new Error('Données non chargées');

    const filtered = Object.entries(data).filter(([id, item]) => {
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

    updateResultCount(filtered);
    renderItems(filtered);

    // Gestion de l'URL avec ID
    const itemId = getUrlParam('id');
    if (itemId && data[itemId]) {
      openPopupItem(itemId, data[itemId]);
    }

    // Gestion de la recherche
    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const filteredResults = filtered.filter(([_, item]) =>
        item.displayProperties.name.toLowerCase().includes(query)
      );
      updateResultCount(filteredResults);
      renderItems(filteredResults);
      clearButton.style.display = e.target.value ? 'block' : 'none';
    });

    // Bouton clear
    clearButton?.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      updateResultCount(filtered);
      renderItems(filtered);
    });

    function renderItems(list) {
      const shuffledList = shuffleArray(list);
      container.innerHTML = '';

      shuffledList.forEach(([id, item], index) => {
        const props = item.displayProperties;
        const card = document.createElement('div');
        card.className = 'card-item animate__animated animate__fadeInUp';
        card.style.animationDelay = `${Math.min(index * 0.05, 3)}s`;
        card.title = props.name;

        card.innerHTML = `
          <img src="${getBungieIconUrl(props.icon)}" alt="d2glossary - ${props.name}" />
          <div>${props.name}</div>
        `;
        card.onclick = () => openPopupItem(id, item);
        container.appendChild(card);
      });
    }

    function updateResultCount(list) {
      resultCount.textContent = `Résultats trouvés: ${list.length}`;
    }

  } catch (err) {
    console.error('Erreur lors du chargement des données:', err);
  }
}