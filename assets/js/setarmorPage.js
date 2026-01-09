/* setarmorPage.js - Gestion de la page des sets d'armure avec recherche multilingue et DDCVacuum */
import {
  loadHTML,
  loadJSON,
  getUrlParam,
  setUrlParam,
  removeUrlParam,
  getCurrentUrl,
  copyToClipboard,
  processDescription,
  getBungieIconUrl,
  normalizeName,
  onEscapeKey,
  debounce
} from './utils.js';
import { Pagination } from './pagination.js';
import { createSearchIndex, searchWithIndex, loadOtherLanguageData } from './multilingualSearch.js';
import {
  loadDDCVacuumData,
  getDDCVacuumData,
  showDDCVacuumForItem,
  hideDDCVacuumSection,
  cleanupDDCVacuumListeners,
  setCurrentItemFrName
} from './popupitem.js';

export async function loadSetArmorPage({
  dataFile,
  containerId,
  inputId,
  itemsPerPage = 20
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  const resultCount = document.getElementById('result-count');
  const clearButton = document.getElementById('clear-button');
  const popupContainer = document.getElementById('popupitem-container');
  const banniereContainer = document.getElementById('banniere-container');

  let pagination = null;
  let allSets = [];
  let searchIndex = null;
  let currentData = null;
  let currentPerkFrName = null;

  /**
   * Récupère le nom français d'un perk de set d'armure
   */
  async function fetchFrenchPerkName(sandboxPerkHash, setData) {
    try {
      const currentLang = window.D2Language?.getCurrentLanguage?.() || 'fr';

      if (currentLang === 'fr') {
        const perk = setData.setPerks.find(p => String(p.sandboxPerkHash) === String(sandboxPerkHash));
        return perk?.displayProperties?.name || null;
      }

      const frDataUrl = `data/fr/setarmor_definitions_enriched.json`;
      let frData = window.D2DataManager?.getFromMemoryCache?.(frDataUrl);

      if (!frData) {
        const response = await fetch(frDataUrl);
        if (response.ok) {
          frData = await response.json();
        }
      }

      if (frData) {
        for (const [setId, frSetData] of Object.entries(frData)) {
          if (!frSetData.setPerks) continue;

          const frPerk = frSetData.setPerks.find(
            p => String(p.sandboxPerkHash) === String(sandboxPerkHash)
          );

          if (frPerk?.displayProperties?.name) {
            return frPerk.displayProperties.name;
          }
        }
      }

      return null;
    } catch (err) {
      console.warn('[SetArmorPage] Impossible de charger le nom français:', err);
      return null;
    }
  }

  // Fonctions de popup
  function closePopupItem() {
    const popup = document.getElementById('popupitem');
    if (popup) {
      popup.classList.remove('show');
      document.body.classList.remove('popupitem-open');
      removeUrlParam('id');
      currentPerkFrName = null;
      setCurrentItemFrName(null);
      cleanupDDCVacuumListeners();
    }
  }

  function sharePopupItem() {
    const url = getCurrentUrl();
    copyToClipboard(url, 'Lien copié dans le presse-papier :\n' + url);
  }

  function copyDiscordMarkdown() {
    const displayName = document.getElementById('popupitem-name')?.textContent.trim();
    const url = getCurrentUrl();
    const iconSwitch = document.getElementById('iconSwitch');
    const iconEnabled = iconSwitch?.checked;

    let markdown = `[${displayName}](<${url}>)`;

    if (iconEnabled && currentPerkFrName) {
      const cleanFrName = normalizeName(currentPerkFrName);
      markdown = `:${cleanFrName}: ${markdown}`;
    }

    copyToClipboard(markdown, 'Lien Discord copié dans le presse-papier:\n' + markdown);
  }

  // Exposer globalement
  window.closePopupItem = closePopupItem;
  window.sharePopupItem = sharePopupItem;
  window.copyDiscordMarkdown = copyDiscordMarkdown;

  onEscapeKey(closePopupItem);

  // Charger les composants HTML et DDCVacuum en parallèle
  await Promise.all([
    loadHTML('assets/html/popupitem.html', popupContainer),
    loadHTML('assets/html/banniere.html', banniereContainer),
    loadDDCVacuumData() // Précharger DDCVacuum
  ]);

  // Attacher les event listeners
  const discordBtn = document.getElementById('discord-btn');
  if (discordBtn) {
    discordBtn.onclick = null;
    discordBtn.addEventListener('click', copyDiscordMarkdown);
  }

  try {
    const filename = dataFile.split('/').pop();
    const currentLang = dataFile.includes('/fr/') ? 'fr' : 'en';

    const [data, otherLangData] = await Promise.all([
      loadJSON(dataFile),
      loadOtherLanguageData(currentLang, filename)
    ]);

    if (!data) throw new Error('Données non chargées');

    currentData = data;

    allSets = Object.entries(data)
      .map(([id, setData]) => ({
        id,
        hash: setData.hash,
        ...setData
      }))
      .filter(setData =>
        setData.displayProperties?.name &&
        setData.setPerks?.length > 0 &&
        setData.setPerks.some(p => p.displayProperties?.name)
      );

    console.log('[MultilingualSearch] Création de l\'index de recherche pour les sets...');

    const setsAsObject = {};
    allSets.forEach(set => {
      setsAsObject[set.id] = set;
    });

    const otherLangSetsObject = otherLangData ? Object.fromEntries(
      Object.entries(otherLangData).map(([id, setData]) => [id, setData])
    ) : null;

    searchIndex = createSearchIndex(setsAsObject, otherLangSetsObject);
    console.log(`[MultilingualSearch] Index créé avec ${searchIndex.size} entrées`);

    const renderSetCard = (setData) => {
      const card = document.createElement('div');
      card.className = 'card';

      const title = document.createElement('div');
      title.className = 'title';
      title.textContent = setData.displayProperties.name;

      const desc = document.createElement('div');
      desc.className = 'description';
      desc.textContent = setData.displayProperties.description || '';

      const grid = document.createElement('div');
      grid.className = 'grid';

      const armure2 = document.createElement('div');
      armure2.className = 'perk-section';
      armure2.innerHTML = '<div class="perk-title">Armure x2</div>';

      const armure4 = document.createElement('div');
      armure4.className = 'perk-section';
      armure4.innerHTML = '<div class="perk-title">Armure x4</div>';

      setData.setPerks
        .filter(perk => perk.displayProperties?.name)
        .forEach(perk => {
          const section = perk.requiredSetCount === 2 ? armure2 : armure4;
          section.appendChild(createPerkElement(perk, setData));
        });

      grid.appendChild(armure2);
      grid.appendChild(armure4);

      card.appendChild(title);
      if (setData.displayProperties.description) {
        card.appendChild(desc);
      }
      card.appendChild(grid);

      return card;
    };

    pagination = new Pagination({
      container,
      items: allSets,
      itemsPerPage,
      renderItem: renderSetCard
    });

    updateResultCount(allSets);
    pagination.render();

    const perkHash = getUrlParam('id');
    if (perkHash) {
      for (const setData of allSets) {
        const perk = setData.setPerks.find(p => String(p.sandboxPerkHash) === String(perkHash));
        if (perk) {
          await openPerkPopup(perk.sandboxPerkHash, perk, setData);
          break;
        }
      }
    }

    const handleSearch = debounce((query) => {
      if (!query) {
        updateResultCount(allSets);
        pagination.setItems(allSets);
        return;
      }

      const allMatches = searchWithIndex(query, searchIndex, setsAsObject);

      const filteredResults = allMatches
        .map(([id]) => allSets.find(set => set.id === id))
        .filter(Boolean);

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
      updateResultCount(allSets);
      pagination.setItems(allSets);
    });

    function createPerkElement(perk, setData) {
      const div = document.createElement('div');
      div.className = 'perk';

      const props = perk.displayProperties || {};
      const icon = props.icon || '';
      const name = props.name || 'Perk inconnu';

      div.innerHTML = `
        <img src="${getBungieIconUrl(icon)}" alt="${name}" loading="lazy"/>
        <span>${name}</span>
      `;
      div.onclick = () => openPerkPopup(perk.sandboxPerkHash, perk, setData);
      return div;
    }

    async function openPerkPopup(sandboxPerkHash, perk, setData) {
      const iconEl = document.getElementById('popupitem-icon');
      const nameEl = document.getElementById('popupitem-name');
      const descEl = document.getElementById('popupitem-description');
      const idEl = document.getElementById('popupitem-id');
      const popup = document.getElementById('popupitem');

      // Sections Set Armor
      const setarmorSeparator = document.getElementById('setarmor-separator');
      const setarmorContent = document.getElementById('popupitem-setarmor');
      setarmorSeparator?.classList.remove('hidden');
      setarmorContent?.classList.remove('hidden');

      const perkProps = perk.displayProperties;
      iconEl.src = getBungieIconUrl(perkProps.icon);
      iconEl.alt = `d2glossary - ${perkProps.name}`;
      nameEl.textContent = perkProps.name;
      descEl.innerHTML = processDescription(perkProps.description);
      descEl.style.display = 'block';
      idEl.textContent = `ID: ${sandboxPerkHash}`;

      renderPerkContent(perk, setData, setarmorContent);

      // Afficher DDCVacuum si disponible pour ce perk
      await showDDCVacuumForItem(sandboxPerkHash);

      // Récupérer le nom français pour l'emoji Discord
      currentPerkFrName = await fetchFrenchPerkName(sandboxPerkHash, setData);
      setCurrentItemFrName(currentPerkFrName);

      popup.classList.add('show');
      document.body.classList.add('popupitem-open');

      setUrlParam('id', sandboxPerkHash);

      popup.onclick = (e) => {
        if (e.target.id === 'popupitem') closePopupItem();
      };
    }

    function renderPerkContent(perk, setData, contentContainer) {
      contentContainer.innerHTML = '';

      const setNameDiv = document.createElement('div');
      setNameDiv.className = 'setarmor-set-name';
      setNameDiv.innerHTML = `<strong>Set :</strong> ${setData.displayProperties.name}`;
      contentContainer.appendChild(setNameDiv);

      const requiredCount = document.createElement('div');
      requiredCount.className = 'setarmor-required-count';
      requiredCount.innerHTML = `<strong>Pièces requises :</strong> ${perk.requiredSetCount} armures`;
      contentContainer.appendChild(requiredCount);

      const separator = document.createElement('hr');
      separator.className = 'setarmor-items-separator';
      contentContainer.appendChild(separator);

      const order = [3, 0, 2, 4, 1];

      const classesContainer = document.createElement('div');
      classesContainer.className = 'modal-classes';

      function createClassSection(title, baseIndex) {
        const section = document.createElement('div');
        section.className = 'class-section';

        const classTitle = document.createElement('div');
        classTitle.className = 'class-title';
        classTitle.textContent = title;
        section.appendChild(classTitle);

        const grid = document.createElement('div');
        grid.className = 'items-grid';

        order.forEach(i => {
          const item = setData.setItems[baseIndex + i];
          if (item) {
            const img = document.createElement('img');
            img.src = getBungieIconUrl(item.icon);
            img.alt = item.name;
            img.title = item.name;
            img.loading = 'lazy';
            grid.appendChild(img);
          }
        });

        section.appendChild(grid);
        return section;
      }

      classesContainer.appendChild(createClassSection('Chasseur', 0));
      classesContainer.appendChild(createClassSection('Titan', 5));
      classesContainer.appendChild(createClassSection('Arcaniste', 10));

      contentContainer.appendChild(classesContainer);
    }

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