/* subclassPage.js - Page Subclass avec groupement par élément */
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

// Tous les plugCategoryIdentifier liés aux subclasses
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
  // Prismatic
  'hunter.prism.aspects', 'hunter.prism.class_abilities', 'hunter.prism.melee',
  'hunter.prism.movement', 'hunter.prism.supers',
  'titan.prism.aspects', 'titan.prism.class_abilities', 'titan.prism.melee',
  'titan.prism.movement', 'titan.prism.supers',
  'warlock.prism.aspects', 'warlock.prism.class_abilities', 'warlock.prism.melee',
  'warlock.prism.movement', 'warlock.prism.supers',
  'shared.prism.fragments', 'shared.prism.grenades',
];

// Éléments dans l'ordre d'affichage
const ELEMENTS = ['solar', 'arc', 'void', 'stasis', 'strand', 'prism'];

// Noms affichés par élément (FR/EN)
const ELEMENT_LABELS = {
  solar:     { fr: 'Solaire', en: 'Solar' },
  arc:       { fr: 'Cryo-électrique', en: 'Arc' },
  void:      { fr: 'Abyssale', en: 'Void' },
  stasis:    { fr: 'Stase', en: 'Stasis' },
  strand:    { fr: 'Filobscure', en: 'Strand' },
  prism: { fr: 'Prismatique', en: 'Prismatic' },
};

// Classes dans l'ordre d'affichage
const CLASSES = ['hunter', 'titan', 'warlock', 'shared'];

const CLASS_LABELS = {
  hunter:  { fr: 'Chasseur', en: 'Hunter' },
  titan:   { fr: 'Titan', en: 'Titan' },
  warlock: { fr: 'Arcaniste', en: 'Warlock' },
  shared:  { fr: 'Partagé', en: 'Shared' },
};

// Types d'ability dans l'ordre d'affichage
const ABILITY_TYPES = ['supers', 'aspects', 'melee', 'grenades', 'class_abilities', 'movement', 'fragments', 'totems', 'trinkets'];

const ABILITY_LABELS = {
  supers:          { fr: 'Supers', en: 'Supers' },
  aspects:         { fr: 'Aspects', en: 'Aspects' },
  totems:          { fr: 'Aspects', en: 'Aspects' },  // Stasis utilise "totems" pour les aspects
  melee:           { fr: 'Mêlée', en: 'Melee' },
  grenades:        { fr: 'Grenades', en: 'Grenades' },
  class_abilities: { fr: 'Compétence de classe', en: 'Class Ability' },
  movement:        { fr: 'Mouvement', en: 'Movement' },
  fragments:       { fr: 'Fragments', en: 'Fragments' },
  trinkets:        { fr: 'Fragments', en: 'Fragments' },  // Stasis utilise "trinkets" pour les fragments
};

// =========================================================================
// FONCTIONS UTILITAIRES
// =========================================================================

/**
 * Extrait l'élément depuis un plugCategoryIdentifier
 * Ex: "hunter.arc.aspects" → "arc"
 */
function getElementFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  const parts = plugCatId.split('.');
  return parts.length >= 2 ? parts[1] : null;
}

/**
 * Extrait la classe depuis un plugCategoryIdentifier
 * Ex: "hunter.arc.aspects" → "hunter"
 */
function getClassFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  return plugCatId.split('.')[0] || null;
}

/**
 * Extrait le type d'ability depuis un plugCategoryIdentifier
 * Ex: "hunter.arc.aspects" → "aspects"
 */
function getAbilityTypeFromPlugCategory(plugCatId) {
  if (!plugCatId) return null;
  const parts = plugCatId.split('.');
  return parts.length >= 3 ? parts[2] : null;
}

/**
 * Groupe les items par élément → classe → type d'ability
 * @returns {Object} { solar: { hunter: { supers: [[id, item], ...], ... }, ... }, ... }
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
// RENDU
// =========================================================================

/**
 * Crée une card d'item
 */
function createItemCard(id, item) {
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
}

/**
 * Rend une section de classe (Hunter/Titan/Warlock/Shared) dans un élément
 */
function renderClassSection(classKey, classData, lang) {
  const section = document.createElement('div');
  section.className = 'subclass-class-section';

  const classTitle = document.createElement('h3');
  classTitle.className = 'subclass-class-title';
  classTitle.textContent = CLASS_LABELS[classKey]?.[lang] || classKey;
  section.appendChild(classTitle);

  // Itérer les types d'ability dans l'ordre défini
  for (const abilityType of ABILITY_TYPES) {
    const items = classData[abilityType];
    if (!items || items.length === 0) continue;

    const abilitySection = document.createElement('div');
    abilitySection.className = 'subclass-ability-section';

    const abilityTitle = document.createElement('h4');
    abilityTitle.className = 'subclass-ability-title';
    abilityTitle.textContent = ABILITY_LABELS[abilityType]?.[lang] || abilityType;
    abilitySection.appendChild(abilityTitle);

    const grid = document.createElement('div');
    grid.className = 'grid subclass-ability-grid';

    items.forEach(([id, item]) => {
      grid.appendChild(createItemCard(id, item));
    });

    abilitySection.appendChild(grid);
    section.appendChild(abilitySection);
  }

  return section;
}

/**
 * Rend une section d'élément complète (Solar, Arc, etc.)
 */
function renderElementSection(elementKey, elementData, lang) {
  const section = document.createElement('div');
  section.className = `subclass-element-section subclass-element-${elementKey}`;
  section.dataset.element = elementKey;

  const header = document.createElement('div');
  header.className = 'subclass-element-header';

  const title = document.createElement('h2');
  title.className = `subclass-element-title element-${elementKey}`;
  title.textContent = ELEMENT_LABELS[elementKey]?.[lang] || elementKey;
  header.appendChild(title);

  section.appendChild(header);

  const content = document.createElement('div');
  content.className = 'subclass-element-content';

  // Itérer les classes dans l'ordre défini
  for (const cls of CLASSES) {
    if (!elementData[cls]) continue;
    content.appendChild(renderClassSection(cls, elementData[cls], lang));
  }

  section.appendChild(content);
  return section;
}

/**
 * Rend tout le contenu groupé par éléments
 */
function renderGroupedContent(grouped, container, lang) {
  container.innerHTML = '';
  const fragment = document.createDocumentFragment();

  for (const element of ELEMENTS) {
    if (!grouped[element]) continue;
    fragment.appendChild(renderElementSection(element, grouped[element], lang));
  }

  container.appendChild(fragment);
}

/**
 * Rend les résultats de recherche (flat grid, sans groupement)
 */
function renderSearchResults(items, container) {
  container.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'grid';

  items.forEach(([id, item]) => {
    grid.appendChild(createItemCard(id, item));
  });

  container.appendChild(grid);
}

// =========================================================================
// FILTRE PAR ÉLÉMENTS (tabs/boutons)
// =========================================================================

/**
 * Crée les boutons de filtre par élément
 */
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

    // Filtrer les items (le fichier enrichi ne contient que des subclass,
    // mais on garde le filtre pour les excludedIds et la validation)
    allFilteredItems = Object.entries(data).filter(([id, item]) => {
      const props = item.displayProperties;
      if (!props?.name || !props?.icon) return false;
      if (excludedIds.includes(id)) return false;

      const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
      return plugCatId && SUBCLASS_PLUG_CATEGORIES.includes(plugCatId);
    });

    // Grouper par élément
    grouped = groupItemsByElement(allFilteredItems);

    // Créer l'index de recherche multilingue (sur les items filtrés uniquement)
    const filteredData = Object.fromEntries(allFilteredItems);
    const filteredOtherLang = otherLangData
      ? Object.fromEntries(allFilteredItems.map(([id]) => [id, otherLangData[id]]).filter(([, v]) => v))
      : null;

    searchIndex = createSearchIndex(filteredData, filteredOtherLang);
    console.log(`[Subclass] ${allFilteredItems.length} items trouvés, index: ${searchIndex.size} entrées`);

    // Créer les filtres par élément
    if (filterContainer) {
      createElementFilters(filterContainer, currentLang, (element) => {
        activeElement = element;
        applyFilters();
      });
    }

    // Rendu initial groupé
    updateResultCount(allFilteredItems);
    renderGroupedContent(grouped, container, currentLang);

    // Gestion de l'URL avec ID (deep link)
    const itemId = getUrlParam('id');
    if (itemId && data[itemId]) {
      openPopupItem(itemId, data[itemId]);
    }

    // Fonction d'application des filtres (recherche + élément)
    function applyFilters(searchQuery = null) {
      const query = searchQuery ?? input?.value?.toLowerCase() ?? '';

      if (query) {
        // Mode recherche : grille plate filtrée
        let results = searchWithIndex(query, searchIndex, filteredData);

        // Filtrer par élément actif
        if (activeElement !== 'all') {
          results = results.filter(([id, item]) => {
            const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
            return getElementFromPlugCategory(plugCatId) === activeElement;
          });
        }

        updateResultCount(results);
        renderSearchResults(results, container);
      } else {
        // Mode normal : affichage groupé
        if (activeElement === 'all') {
          updateResultCount(allFilteredItems);
          renderGroupedContent(grouped, container, currentLang);
        } else {
          // Grouper seulement l'élément sélectionné
          const filteredGrouped = { [activeElement]: grouped[activeElement] };
          const count = allFilteredItems.filter(([id, item]) => {
            const plugCatId = getNestedValue(item, 'plug.plugCategoryIdentifier');
            return getElementFromPlugCategory(plugCatId) === activeElement;
          });
          updateResultCount(count);
          renderGroupedContent(filteredGrouped, container, currentLang);
        }
      }
    }

    // Gestion de la recherche avec debounce
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
      applyFilters(null);
    });

    function updateResultCount(list) {
      resultCount.textContent = `Résultats trouvés: ${list.length}`;
    }

  } catch (err) {
    console.error('[Subclass] Erreur lors du chargement:', err);
    container.innerHTML = `
      <div class="error-message">
        <h3>⚠️ Erreur de chargement</h3>
        <p>${err.message}</p>
      </div>
    `;
  }
}