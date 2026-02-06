/* subclassPage.js - Page Subclass avec disposition visuelle unique */
import {
  loadHTML,
  loadJSON,
  getUrlParam,
  setUrlParam,
  removeUrlParam,
  getShareableUrl,
  copyToClipboard,
  processDescription,
  parseKeywords,
  normalizeName,
  getBungieIconUrl,
  onEscapeKey,
  debounce
} from './utils.js';
import { setCurrentItemFrName } from './popupitem.js';
import {
  loadDDCVacuumData,
  showDDCVacuumForItem,
  cleanupDDCVacuumListeners
} from './ddcvacuum.js';
import { createSearchIndex, searchWithIndex, loadOtherLanguageData } from './multilingualSearch.js';
import { getNestedValue } from './itemListPage.js';

// =========================================================================
// CONFIGURATION DES SUBCLASSES
// =========================================================================

const SUBCLASS_PLUG_CATEGORIES = [
  // Arc
  'hunter.arc.aspects', 'hunter.arc.class_abilities', 'hunter.arc.melee',
  'hunter.arc.movement', 'hunter.arc.supers',
  'titan.arc.aspects', 'titan.arc.class_abilities', 'titan.arc.melee',
  'titan.arc.movement', 'titan.arc.supers',
  'warlock.arc.aspects', 'warlock.arc.class_abilities', 'warlock.arc.melee',
  'warlock.arc.movement', 'warlock.arc.supers',
  'shared.arc.fragments', 'shared.arc.grenades',
  // Void
  'hunter.void.aspects', 'hunter.void.class_abilities', 'hunter.void.melee',
  'hunter.void.movement', 'hunter.void.supers',
  'titan.void.aspects', 'titan.void.class_abilities', 'titan.void.melee',
  'titan.void.movement', 'titan.void.supers',
  'warlock.void.aspects', 'warlock.void.class_abilities', 'warlock.void.melee',
  'warlock.void.movement', 'warlock.void.supers',
  'shared.void.fragments', 'shared.void.grenades',
  // Solar
  'hunter.solar.aspects', 'hunter.solar.class_abilities', 'hunter.solar.melee',
  'hunter.solar.movement', 'hunter.solar.supers',
  'titan.solar.aspects', 'titan.solar.class_abilities', 'titan.solar.melee',
  'titan.solar.movement', 'titan.solar.supers',
  'warlock.solar.aspects', 'warlock.solar.class_abilities', 'warlock.solar.melee',
  'warlock.solar.movement', 'warlock.solar.supers',
  'shared.solar.fragments', 'shared.solar.grenades',
  // Stasis
  'hunter.stasis.totems', 'hunter.stasis.class_abilities', 'hunter.stasis.melee',
  'hunter.stasis.movement', 'hunter.stasis.supers',
  'titan.stasis.totems', 'titan.stasis.class_abilities', 'titan.stasis.melee',
  'titan.stasis.movement', 'titan.stasis.supers',
  'warlock.stasis.totems', 'warlock.stasis.class_abilities', 'warlock.stasis.melee',
  'warlock.stasis.movement', 'warlock.stasis.supers',
  'shared.stasis.trinkets', 'shared.stasis.grenades',
  // Strand
  'hunter.strand.aspects', 'hunter.strand.class_abilities', 'hunter.strand.melee',
  'hunter.strand.movement', 'hunter.strand.supers',
  'titan.strand.aspects', 'titan.strand.class_abilities', 'titan.strand.melee',
  'titan.strand.movement', 'titan.strand.supers',
  'warlock.strand.aspects', 'warlock.strand.class_abilities', 'warlock.strand.melee',
  'warlock.strand.movement', 'warlock.strand.supers',
  'shared.strand.fragments', 'shared.strand.grenades',
  // Prismatic (grenades par classe, pas shared)
  'hunter.prism.aspects', 'hunter.prism.class_abilities', 'hunter.prism.melee',
  'hunter.prism.movement', 'hunter.prism.supers', 'hunter.prism.grenades',
  'titan.prism.aspects', 'titan.prism.class_abilities', 'titan.prism.melee',
  'titan.prism.movement', 'titan.prism.supers', 'titan.prism.grenades',
  'warlock.prism.aspects', 'warlock.prism.class_abilities', 'warlock.prism.melee',
  'warlock.prism.movement', 'warlock.prism.supers', 'warlock.prism.grenades',
  'shared.prism.fragments',
];

const ELEMENTS = ['solar', 'arc', 'void', 'stasis', 'strand', 'prism'];

const ELEMENT_LABELS = {
  solar:  { fr: 'Solaire', en: 'Solar' },
  arc:    { fr: 'Cryo-électrique', en: 'Arc' },
  void:   { fr: 'Abyssale', en: 'Void' },
  stasis: { fr: 'Stase', en: 'Stasis' },
  strand: { fr: 'Filobscure', en: 'Strand' },
  prism:  { fr: 'Prismatique', en: 'Prismatic' },
};

const PLAYER_CLASSES = ['hunter', 'titan', 'warlock'];

const CLASS_LABELS = {
  hunter:  { fr: 'Chasseur', en: 'Hunter' },
  titan:   { fr: 'Titan', en: 'Titan' },
  warlock: { fr: 'Arcaniste', en: 'Warlock' },
};

const ABILITY_LABELS = {
  supers:          { fr: 'Supers', en: 'Supers' },
  aspects:         { fr: 'Aspects', en: 'Aspects' },
  totems:          { fr: 'Aspects', en: 'Aspects' },
  melee:           { fr: 'Mêlée', en: 'Melee' },
  grenades:        { fr: 'Grenades', en: 'Grenades' },
  class_abilities: { fr: 'Compétence de classe', en: 'Class Ability' },
  movement:        { fr: 'Saut', en: 'Jump' },
  fragments:       { fr: 'Fragments', en: 'Fragments' },
  trinkets:        { fr: 'Fragments', en: 'Fragments' },
};

// =========================================================================
// FONCTIONS UTILITAIRES
// =========================================================================

function getElementFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  const parts = plugCatId.split('.');
  return parts.length >= 2 ? parts[1] : null;
}

function getClassFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  return plugCatId.split('.')[0] || null;
}

function getAbilityTypeFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  const parts = plugCatId.split('.');
  return parts.length >= 3 ? parts[2] : null;
}

/**
 * Groupe les items par élément → classe → type d'ability
 */
function groupItemsByElement(items) {
  const grouped = {};

  for (const [id, item] of items) {
    const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
    if (!plugCatId) continue;

    const element = getElementFromPlugCategory(plugCatId);
    const cls = getClassFromPlugCategory(plugCatId);
    const abilityType = getAbilityTypeFromPlugCategory(plugCatId);

    if (!element || !cls || !abilityType) continue;

    if (!grouped[element]) grouped[element] = {};
    if (!grouped[element][cls]) grouped[element][cls] = {};
    if (!grouped[element][cls][abilityType]) grouped[element][cls][abilityType] = [];

    grouped[element][cls][abilityType].push([id, item]);
  }

  return grouped;
}

// =========================================================================
// COMPOSANTS DE RENDU - BLOCS D'ABILITY
// =========================================================================

/**
 * Crée un bloc d'icône cliquable
 */
function createAbilityBlock(id, item, onItemClick) {
  const props = item.displayProperties;
  const block = document.createElement('div');
  block.className = 'subclass-ability-block';
  block.title = props.name;
  block.dataset.itemId = id;

  block.innerHTML = `
    <img src="${getBungieIconUrl(props.icon)}" alt="${props.name}" loading="lazy" />
  `;

  if (onItemClick) {
    block.onclick = () => onItemClick(id, item);
  }

  return block;
}

/**
 * Section Supers - Disposition en losange (4 items max)
 */
function createSupersSection(items, onItemClick) {
  const section = document.createElement('div');
  section.className = 'subclass-supers-section';

  const container = document.createElement('div');
  // Si 4 items exactement, disposition losange, sinon grille simple
  container.className = items.length === 4
    ? 'subclass-supers-diamond'
    : 'subclass-supers-grid';

  items.forEach(([id, item], index) => {
    const block = createAbilityBlock(id, item, onItemClick);
    if (items.length === 4) {
      block.classList.add(`diamond-pos-${index}`);
    }
    container.appendChild(block);
  });

  section.appendChild(container);
  return section;
}

/**
 * Section Core Abilities - Mêlées + Class Abilities (+ Grenades si pas partagées)
 * @param {Object} classData - Données de la classe
 * @param {boolean} includeGrenades - true si les grenades sont par classe (ex: Prismatique)
 */
function createCoreAbilitiesSection(classData, onItemClick, includeGrenades = false) {
  const section = document.createElement('div');
  section.className = 'subclass-core-section';

  // Types à afficher (grenades seulement si includeGrenades)
  const types = [
    ...(includeGrenades ? [{ key: 'grenades', className: 'grenades' }] : []),
    { key: 'melee', className: 'melee' },
    { key: 'class_abilities', className: 'class-abilities' }
  ];

  types.forEach(({ key, className }) => {
    const items = classData[key] || [];
    if (items.length === 0) return;

    const column = document.createElement('div');
    column.className = `subclass-core-column subclass-core-${className}`;

    items.forEach(([id, item]) => {
      column.appendChild(createAbilityBlock(id, item, onItemClick));
    });

    section.appendChild(column);
  });

  return section;
}

/**
 * Section Movement/Sauts
 */
function createMovementSection(items, onItemClick) {
  const section = document.createElement('div');
  section.className = 'subclass-movement-section';

  items.forEach(([id, item]) => {
    section.appendChild(createAbilityBlock(id, item, onItemClick));
  });

  return section;
}

/**
 * Section Aspects - Grille 2x2
 */
function createAspectsSection(items, onItemClick) {
  const section = document.createElement('div');
  section.className = 'subclass-aspects-section';

  items.forEach(([id, item]) => {
    section.appendChild(createAbilityBlock(id, item, onItemClick));
  });

  return section;
}

/**
 * Section Fragments - Grille horizontale
 */
function createFragmentsSection(items, onItemClick) {
  const section = document.createElement('div');
  section.className = 'subclass-fragments-section';

  items.forEach(([id, item]) => {
    section.appendChild(createAbilityBlock(id, item, onItemClick));
  });

  return section;
}

// =========================================================================
// COMPOSANT PRINCIPAL - BLOC DE CLASSE
// =========================================================================

/**
 * Crée le bloc complet d'une classe (Hunter/Titan/Warlock)
 * @param {string} classKey - 'hunter', 'titan', 'warlock'
 * @param {Object} classData - Données de la classe
 * @param {string} lang - 'fr' ou 'en'
 * @param {Function} onItemClick - Callback
 * @param {boolean} hasClassGrenades - true si grenades par classe (Prismatique)
 */
function createSubclassClassBlock(classKey, classData, lang, onItemClick, hasClassGrenades = false) {
  const block = document.createElement('div');
  block.className = `subclass-class-block subclass-class-${classKey}`;
  block.dataset.class = classKey;

  // Header avec nom de la classe
  const header = document.createElement('div');
  header.className = 'subclass-class-header';
  header.innerHTML = `
    <span class="subclass-class-name">${CLASS_LABELS[classKey]?.[lang] || classKey}</span>
  `;
  block.appendChild(header);

  // Container principal
  const content = document.createElement('div');
  content.className = 'subclass-class-content';

  // === SUPERS (losange jaune) ===
  const supers = classData.supers || [];
  if (supers.length > 0) {
    content.appendChild(createSupersSection(supers, onItemClick));
  }

  // === CORE ABILITIES (Grenades si pas partagées + Mêlées + Class) ===
  const hasCoreAbilities = (hasClassGrenades && classData.grenades?.length) ||
                           classData.melee?.length ||
                           classData.class_abilities?.length;
  if (hasCoreAbilities) {
    content.appendChild(createCoreAbilitiesSection(classData, onItemClick, hasClassGrenades));
  }

  // === MOVEMENT/SAUTS ===
  const movement = classData.movement || [];
  if (movement.length > 0) {
    content.appendChild(createMovementSection(movement, onItemClick));
  }

  // === ASPECTS (rouge) ===
  const aspects = classData.aspects || classData.totems || [];
  if (aspects.length > 0) {
    content.appendChild(createAspectsSection(aspects, onItemClick));
  }

  block.appendChild(content);
  return block;
}

// =========================================================================
// VUE ÉLÉMENT COMPLÈTE
// =========================================================================

/**
 * Crée la vue complète d'un élément (Solar, Arc, etc.)
 * avec les 3 classes côte à côte + fragments partagés
 */
function createSubclassElementView(elementKey, elementData, lang, onItemClick) {
  const container = document.createElement('div');
  container.className = `subclass-element-view subclass-element-${elementKey}`;
  container.dataset.element = elementKey;

  // Header de l'élément
  const header = document.createElement('div');
  header.className = 'subclass-element-header';
  header.innerHTML = `
    <h2 class="subclass-element-title element-${elementKey}">
      ${ELEMENT_LABELS[elementKey]?.[lang] || elementKey}
    </h2>
  `;
  container.appendChild(header);

  // Détecter si les grenades sont par classe (pas de shared.grenades)
  const hasClassGrenades = !elementData.shared?.grenades?.length &&
    PLAYER_CLASSES.some(cls => elementData[cls]?.grenades?.length > 0);

  // Grille des 3 classes
  const classesGrid = document.createElement('div');
  classesGrid.className = 'subclass-classes-grid';

  PLAYER_CLASSES.forEach(cls => {
    if (elementData[cls]) {
      classesGrid.appendChild(
        createSubclassClassBlock(cls, elementData[cls], lang, onItemClick, hasClassGrenades)
      );
    }
  });

  container.appendChild(classesGrid);

  // Section partagée (grenades partagées + fragments)
  const shared = elementData.shared;
  if (shared) {
    const grenades = shared.grenades || [];
    const fragments = shared.fragments || shared.trinkets || [];

    if (grenades.length > 0 || fragments.length > 0) {
      const sharedSection = document.createElement('div');
      sharedSection.className = 'subclass-shared-section';

      // Grenades partagées (seulement si présentes dans shared)
      if (grenades.length > 0) {
        const grenadesContainer = document.createElement('div');
        grenadesContainer.className = 'subclass-shared-grenades';
        grenadesContainer.innerHTML = `<h4>${ABILITY_LABELS.grenades[lang]}</h4>`;

        const grid = document.createElement('div');
        grid.className = 'subclass-shared-grid';
        grenades.forEach(([id, item]) => {
          grid.appendChild(createAbilityBlock(id, item, onItemClick));
        });
        grenadesContainer.appendChild(grid);
        sharedSection.appendChild(grenadesContainer);
      }

      // Fragments partagés
      if (fragments.length > 0) {
        const fragmentsContainer = document.createElement('div');
        fragmentsContainer.className = 'subclass-shared-fragments';
        fragmentsContainer.innerHTML = `<h4>${ABILITY_LABELS.fragments[lang]}</h4>`;
        fragmentsContainer.appendChild(createFragmentsSection(fragments, onItemClick));
        sharedSection.appendChild(fragmentsContainer);
      }

      container.appendChild(sharedSection);
    }
  }

  return container;
}

// =========================================================================
// RENDU PRINCIPAL
// =========================================================================

/**
 * Rend tout le contenu groupé par éléments
 */
function renderGroupedContent(grouped, container, lang, onItemClick) {
  container.innerHTML = '';
  const fragment = document.createDocumentFragment();

  for (const element of ELEMENTS) {
    if (!grouped[element]) continue;
    fragment.appendChild(createSubclassElementView(element, grouped[element], lang, onItemClick));
  }

  container.appendChild(fragment);
}

/**
 * Rend les résultats de recherche (grille simple)
 */
function renderSearchResults(items, container, onItemClick) {
  container.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'subclass-search-results';

  items.forEach(([id, item]) => {
    const props = item.displayProperties;
    const card = document.createElement('div');
    card.className = 'card-item';
    card.title = props.name;
    card.innerHTML = `
      <img src="${getBungieIconUrl(props.icon)}" alt="${props.name}" loading="lazy" />
      <div>${props.name}</div>
    `;
    card.onclick = () => onItemClick(id, item);
    grid.appendChild(card);
  });

  container.appendChild(grid);
}

// =========================================================================
// FILTRE PAR ÉLÉMENTS
// =========================================================================

function createElementFilters(container, lang, onFilterChange) {
  const filterBar = document.createElement('div');
  filterBar.className = 'subclass-filter-bar';

  // Bouton "Tous"
  const allBtn = document.createElement('button');
  allBtn.className = 'subclass-filter-btn active';
  allBtn.dataset.element = 'all';
  allBtn.textContent = lang === 'fr' ? 'Tous' : 'All';
  allBtn.onclick = () => {
    filterBar.querySelectorAll('.subclass-filter-btn').forEach(b => b.classList.remove('active'));
    allBtn.classList.add('active');
    onFilterChange('all');
  };
  filterBar.appendChild(allBtn);

  // Boutons par élément
  for (const element of ELEMENTS) {
    const btn = document.createElement('button');
    btn.className = `subclass-filter-btn element-filter-${element}`;
    btn.dataset.element = element;
    btn.textContent = ELEMENT_LABELS[element]?.[lang] || element;
    btn.onclick = () => {
      filterBar.querySelectorAll('.subclass-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      onFilterChange(element);
    };
    filterBar.appendChild(btn);
  }

  container.appendChild(filterBar);
  return filterBar;
}

// =========================================================================
// POINT D'ENTRÉE PRINCIPAL
// =========================================================================

export async function loadSubclassPage({
  dataFile,
  containerId,
  inputId,
  excludedIds = [],
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  const resultCount = document.getElementById('result-count');
  const clearButton = document.getElementById('clear-button');
  const popupContainer = document.getElementById('popupitem-container');
  const banniereContainer = document.getElementById('banniere-container');
  const filterContainer = document.getElementById('subclass-filters');

  let allFilteredItems = [];
  let grouped = {};
  let searchIndex = null;
  let currentData = null;
  let activeElement = 'all';
  let currentLang = 'fr';

  // Charger les composants HTML et DDCVacuum
  await Promise.all([
    loadHTML('assets/html/popupitem.html', popupContainer),
    loadHTML('assets/html/banniere.html', banniereContainer),
    loadDDCVacuumData()
  ]);

  // Callback pour ouvrir le popup
  const handleItemClick = (id, item) => {
    openPopupItem(id, item);
  };

  // Mise à jour du compteur
  const updateResultCount = (items) => {
    if (resultCount) {
      resultCount.textContent = `${items.length} résultat${items.length > 1 ? 's' : ''}`;
    }
  };

  try {
    const filename = dataFile.split('/').pop();
    currentLang = dataFile.includes('/fr/') ? 'fr' : 'en';

    // Charger les données
    const [data, otherLangData] = await Promise.all([
      loadJSON(dataFile),
      loadOtherLanguageData(currentLang, filename)
    ]);

    if (!data) throw new Error('Données non chargées');

    currentData = data;

    // Filtrer les items
    allFilteredItems = Object.entries(data).filter(([id, item]) => {
      const props = item.displayProperties;
      if (!props?.name || !props?.icon) return false;
      if (excludedIds.includes(id)) return false;

      const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
      return plugCatId && SUBCLASS_PLUG_CATEGORIES.includes(plugCatId);
    });

    // Grouper par élément
    grouped = groupItemsByElement(allFilteredItems);

    // Index de recherche
    const filteredData = Object.fromEntries(allFilteredItems);
    const filteredOtherLang = otherLangData
      ? Object.fromEntries(allFilteredItems.map(([id]) => [id, otherLangData[id]]).filter(([, v]) => v))
      : null;

    searchIndex = createSearchIndex(filteredData, filteredOtherLang);
    console.log(`[Subclass] ${allFilteredItems.length} items, index: ${searchIndex.size} entrées`);

    // Créer les filtres
    if (filterContainer) {
      createElementFilters(filterContainer, currentLang, (element) => {
        activeElement = element;
        applyFilters();
      });
    }

    // Rendu initial
    updateResultCount(allFilteredItems);
    renderGroupedContent(grouped, container, currentLang, handleItemClick);

    // Deep link
    const itemId = getUrlParam('id');
    if (itemId && data[itemId]) {
      openPopupItem(itemId, data[itemId]);
    }

    // Application des filtres
    function applyFilters(searchQuery = null) {
      const query = searchQuery ?? input?.value?.toLowerCase() ?? '';

      let itemsToDisplay = allFilteredItems;

      // Filtre par recherche
      if (query) {
        const matches = searchWithIndex(query, searchIndex, currentData);
        itemsToDisplay = matches.filter(([id]) =>
          allFilteredItems.some(([filteredId]) => filteredId === id)
        );
      }

      // Filtre par élément
      if (activeElement !== 'all') {
        itemsToDisplay = itemsToDisplay.filter(([id, item]) => {
          const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
          return getElementFromPlugCategory(plugCatId) === activeElement;
        });
      }

      updateResultCount(itemsToDisplay);

      // Affichage
      if (query) {
        // Mode recherche : grille simple
        renderSearchResults(itemsToDisplay, container, handleItemClick);
      } else if (activeElement !== 'all') {
        // Mode filtre élément : vue groupée filtrée
        const filteredGrouped = { [activeElement]: grouped[activeElement] };
        renderGroupedContent(filteredGrouped, container, currentLang, handleItemClick);
      } else {
        // Mode par défaut : tout afficher groupé
        renderGroupedContent(grouped, container, currentLang, handleItemClick);
      }
    }

    // Gestion de la recherche
    const handleSearch = debounce((query) => {
      applyFilters(query || null);
    }, 150);

    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      handleSearch(query);
      clearButton.style.display = e.target.value ? 'block' : 'none';
    });

    clearButton?.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      applyFilters();
      input.focus();
    });

  } catch (error) {
    console.error('[Subclass] Erreur:', error);
    container.innerHTML = `<p style="color:red;">Erreur: ${error.message}</p>`;
  }
}