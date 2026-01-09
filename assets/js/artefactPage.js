/* artefactPage.js - Gestion de la page artefact */
import {
  loadHTML,
  loadJSON,
  processDescription,
  parseKeywords,
  escapeHtml,
  getBungieIconUrl,
  copyToClipboard,
  getCurrentUrl,
  setUrlParam,
  removeUrlParam,
  normalizeName,
  onEscapeKey
} from './utils.js';
import {
  loadClarityData,
  getClarityData,
  renderClarityInPopup,
  hideClaritySection,
  cleanupClarityListeners,
  setCurrentItemFrName
} from './popupitem.js';

export async function loadArtefactPage({
  dataFile,
  containerId,
  tooltipId
}) {
  const MAX_SELECTIONS = 12;

  const content = document.getElementById(containerId);
  const tooltip = document.getElementById(tooltipId);
  const tooltipIcon = document.getElementById('tooltipIcon');
  const tooltipName = document.getElementById('tooltipName');
  const tooltipDescription = document.getElementById('tooltipDescription');
  const shareBtn = document.getElementById('shareBtn');
  const resetBtn = document.getElementById('resetBtn');
  const progressBar = document.getElementById('progressBar');
  const progressCounter = document.getElementById('progressCounter');
  const tierMarkers = document.getElementById('tierMarkers');
  const popupContainer = document.getElementById('popupitem-container');

  let artifactData = null;
  let selectedItems = new Set();
  let tierRequirements = [];
  let currentMode = 'consultation';
  let currentItemFrName = null;

  // Charger le popup HTML et Clarity en parallèle
  await Promise.all([
    loadHTML('assets/html/popupitem.html', popupContainer),
    loadClarityData()
  ]);

  initModeSwitch();
  await loadData();
  initPopupListeners();

  function initModeSwitch() {
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });
  }

  function switchMode(mode) {
    currentMode = mode;

    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    if (mode === 'consultation') {
      document.body.classList.add('consultation-mode');
      document.body.classList.remove('configuration-mode');
      selectedItems.clear();
      document.querySelectorAll('.item-icon.selected').forEach(el => el.classList.remove('selected'));
    } else {
      document.body.classList.remove('consultation-mode');
      document.body.classList.add('configuration-mode');
      updateProgress();
    }
  }

  async function loadData() {
    try {
      const data = await loadJSON(dataFile);
      if (!data) throw new Error('Données non chargées');
      artifactData = data;
      displayArtifact(data);
      loadSelectionFromURL();
      if (currentMode === 'configuration') updateProgress();

      const perkHash = new URLSearchParams(window.location.search).get('id');
      if (perkHash) {
        openPerkFromHash(perkHash);
      }
    } catch (error) {
      console.error('Erreur:', error);
      content.innerHTML = `
        <div class="error-message">
          <h3>⚠️ Erreur de chargement</h3>
          <p>Impossible de charger les données de l'artefact</p>
          <p style="font-size:0.85em;margin-top:10px;opacity:0.7">${error.message}</p>
        </div>
      `;
    }
  }

  function openPerkFromHash(perkHash) {
    const artifactId = Object.keys(artifactData)[0];
    const artifact = artifactData[artifactId];

    for (const tier of artifact.tiers) {
      const item = tier.items.find(i =>
        String(i.perkHash) === String(perkHash) ||
        String(i.itemHash) === String(perkHash)
      );
      if (item) {
        openPopupItem(perkHash, item);
        break;
      }
    }
  }

  function displayArtifact(data) {
    const artifactId = Object.keys(data)[0];
    const artifact = data[artifactId];

    let markersHtml = '';
    artifact.tiers.forEach((tier, index) => {
      const requirement = tier.minimumUnlockPointsUsedRequirement || 0;
      tierRequirements.push(requirement);

      let sectionSize;
      if (index === 0) {
        sectionSize = artifact.tiers[1].minimumUnlockPointsUsedRequirement;
      } else if (index < artifact.tiers.length - 1) {
        sectionSize = artifact.tiers[index + 1].minimumUnlockPointsUsedRequirement - requirement;
      } else {
        sectionSize = MAX_SELECTIONS - requirement;
      }

      markersHtml += `
        <div class="tier-marker" data-tier="${index}" data-requirement="${requirement}" style="flex:${sectionSize} 0 0">
          <div class="tier-marker-label">${tier.displayTitle}</div>
        </div>
      `;
    });
    tierMarkers.innerHTML = markersHtml;

    let html = '<div class="grid">';

    artifact.tiers.forEach((tier, tierIndex) => {
      html += `
        <div class="tier-column" data-tier="${tierIndex}">
          <div class="tier-header">
            <div class="tier-title">${tier.displayTitle}</div>
          </div>
          <div class="items-container">
      `;

      const validItems = tier.items.slice(-7).filter(item =>
        item.name?.trim() && item.icon
      );

      validItems.forEach(item => {
        const iconUrl = getBungieIconUrl(item.icon);
        const itemId = `${tierIndex}-${item.perkHash || item.itemHash}`;
        const perkHash = item.perkHash || item.itemHash;
        html += `
          <div class="item-icon"
               data-item-id="${itemId}"
               data-perk-hash="${perkHash}"
               data-tier="${tierIndex}"
               data-name="${escapeHtml(item.name)}"
               data-description="${escapeHtml(item.description)}"
               data-icon="${iconUrl}">
            <img src="${iconUrl}" alt="${escapeHtml(item.name)}">
          </div>
        `;
      });

      html += '</div></div>';
    });

    html += '</div>';
    content.innerHTML = html;

    document.querySelectorAll('.item-icon').forEach(icon => {
      icon.addEventListener('click', handleItemClick);
      icon.addEventListener('mouseenter', showTooltip);
      icon.addEventListener('mousemove', moveTooltip);
      icon.addEventListener('mouseleave', hideTooltip);
    });
  }

  function handleItemClick(event) {
    const el = event.currentTarget;

    if (currentMode === 'consultation') {
      const perkHash = el.dataset.perkHash;
      const item = {
        name: el.dataset.name,
        description: el.dataset.description,
        icon: el.dataset.icon.replace(getBungieIconUrl(''), '')
      };
      openPopupItem(perkHash, item);
    } else {
      toggleSelection(event);
    }
  }

  function toggleSelection(event) {
    const el = event.currentTarget;
    const itemId = el.dataset.itemId;

    if (selectedItems.has(itemId)) {
      selectedItems.delete(itemId);
      el.classList.remove('selected');
    } else if (selectedItems.size < MAX_SELECTIONS) {
      selectedItems.add(itemId);
      el.classList.add('selected');
    } else {
      alert(`Maximum ${MAX_SELECTIONS} items !`);
      return;
    }

    updateProgress();
  }

  function updateProgress() {
    const itemsToRemove = [];
    selectedItems.forEach(itemId => {
      const tierIndex = parseInt(itemId.split('-')[0]);
      const requirement = tierRequirements[tierIndex] || 0;
      if (selectedItems.size < requirement) {
        itemsToRemove.push(itemId);
        document.querySelector(`[data-item-id="${itemId}"]`)?.classList.remove('selected');
      }
    });
    itemsToRemove.forEach(id => selectedItems.delete(id));

    const total = selectedItems.size;
    progressCounter.textContent = `${total}/${MAX_SELECTIONS}`;
    progressBar.style.width = `${(total / MAX_SELECTIONS) * 100}%`;

    document.querySelectorAll('.tier-marker').forEach((marker, index) => {
      const requirement = parseInt(marker.dataset.requirement);
      marker.classList.remove('unlocked', 'next');

      if (index < tierRequirements.length - 1 && total >= tierRequirements[index + 1]) {
        marker.classList.add('unlocked');
      } else if (total >= requirement) {
        marker.classList.add('next');
      }
    });

    document.querySelectorAll('.tier-column').forEach(col => {
      const tier = parseInt(col.dataset.tier);
      const requirement = tierRequirements[tier] || 0;
      col.classList.toggle('locked', total < requirement);
    });
  }

  function loadSelectionFromURL() {
    const selection = new URLSearchParams(window.location.search).get('selection');
    if (!selection) return;

    try {
      selection.split(',').forEach(itemId => {
        if (itemId && selectedItems.size < MAX_SELECTIONS) {
          selectedItems.add(itemId);
          document.querySelector(`[data-item-id="${itemId}"]`)?.classList.add('selected');
        }
      });
    } catch (e) {
      console.error('Erreur chargement sélection:', e);
    }
  }

  // === POPUP FUNCTIONS ===
  async function fetchFrenchName(perkHash) {
    try {
      const currentLang = window.D2Language?.getCurrentLanguage?.() || 'fr';

      // Si déjà en français, chercher dans les données actuelles
      if (currentLang === 'fr' && artifactData) {
        const artifactId = Object.keys(artifactData)[0];
        const artifact = artifactData[artifactId];
        for (const tier of artifact.tiers) {
          const item = tier.items.find(i =>
            String(i.perkHash) === String(perkHash) ||
            String(i.itemHash) === String(perkHash)
          );
          if (item?.name) return item.name;
        }
      }

      const frDataUrl = `data/fr/artefact_definitions_enriched.json`;
      let frData = window.D2DataManager?.getFromMemoryCache?.(frDataUrl);

      if (!frData) {
        const response = await fetch(frDataUrl);
        if (response.ok) frData = await response.json();
      }

      if (frData) {
        const artifactId = Object.keys(frData)[0];
        const artifact = frData[artifactId];
        for (const tier of artifact.tiers) {
          const item = tier.items.find(i =>
            String(i.perkHash) === String(perkHash) ||
            String(i.itemHash) === String(perkHash)
          );
          if (item?.name) return item.name;
        }
      }
      return null;
    } catch (err) {
      console.warn('[ArtefactPage] Impossible de charger le nom français:', err);
      return null;
    }
  }

  async function openPopupItem(perkHash, item) {
    const iconEl = document.getElementById('popupitem-icon');
    const nameEl = document.getElementById('popupitem-name');
    const descEl = document.getElementById('popupitem-description');
    const idEl = document.getElementById('popupitem-id');
    const popup = document.getElementById('popupitem');

    // Masquer les sections non utilisées
    document.getElementById('setarmor-separator')?.classList.add('hidden');
    document.getElementById('popupitem-setarmor')?.classList.add('hidden');

    const currentLang = window.D2Language?.getCurrentLanguage?.() || 'fr';

    iconEl.src = getBungieIconUrl(item.icon);
    iconEl.alt = `d2glossary - ${item.name}`;
    nameEl.textContent = item.name;

    const finalDescription = parseKeywords(
      processDescription(item.description),
      currentLang
    );
    descEl.innerHTML = finalDescription;

    // Utiliser les fonctions Clarity centralisées
    const clarityData = getClarityData();
    if (clarityData && clarityData[perkHash]) {
      renderClarityInPopup(clarityData[perkHash]);
    } else {
      hideClaritySection();
    }

    idEl.textContent = `ID: ${perkHash}`;

    // Récupérer le nom français pour l'emoji Discord
    currentItemFrName = await fetchFrenchName(perkHash);
    if (currentLang === 'fr' && !currentItemFrName) {
      currentItemFrName = item.name;
    }
    setCurrentItemFrName(currentItemFrName);

    popup.classList.add('show');
    document.body.classList.add('popupitem-open');
    setUrlParam('id', perkHash);

    popup.onclick = (e) => {
      if (e.target.id === 'popupitem') closePopupItem();
    };
  }

  function closePopupItem() {
    const popup = document.getElementById('popupitem');
    popup?.classList.remove('show');
    document.body.classList.remove('popupitem-open');
    removeUrlParam('id');
    currentItemFrName = null;
    setCurrentItemFrName(null);
    cleanupClarityListeners();
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

    if (iconEnabled && currentItemFrName) {
      const cleanFrName = normalizeName(currentItemFrName);
      markdown = `:${cleanFrName}: ${markdown}`;
    }

    copyToClipboard(markdown, 'Lien Discord copié dans le presse-papier:\n' + markdown);
  }

  function initPopupListeners() {
    window.closePopupItem = closePopupItem;
    window.sharePopupItem = sharePopupItem;
    window.copyDiscordMarkdown = copyDiscordMarkdown;

    onEscapeKey(closePopupItem);

    const discordBtn = document.getElementById('discord-btn');
    if (discordBtn) {
      discordBtn.onclick = null;
      discordBtn.addEventListener('click', copyDiscordMarkdown);
    }
  }

  // Share & Reset buttons
  shareBtn.addEventListener('click', () => {
    if (!selectedItems.size) {
      alert('Aucune sélection à partager !');
      return;
    }
    const url = new URL(getCurrentUrl());
    url.searchParams.set('selection', Array.from(selectedItems).join(','));
    copyToClipboard(url.toString(), 'Lien copié !\n' + url.toString());
  });

  resetBtn.addEventListener('click', () => {
    if (!confirm('Réinitialiser la sélection ?')) return;
    selectedItems.clear();
    document.querySelectorAll('.item-icon.selected').forEach(el => el.classList.remove('selected'));
    updateProgress();
    const url = new URL(getCurrentUrl());
    url.searchParams.delete('selection');
    history.replaceState(null, '', url);
  });

  // Tooltip functions
  function showTooltip(e) {
    if (document.body.classList.contains('popupitem-open')) return;

    const el = e.currentTarget;
    const currentLang = window.D2Language?.getCurrentLanguage?.() || 'fr';

    tooltipName.textContent = el.dataset.name;
    tooltipDescription.innerHTML = parseKeywords(
      processDescription(el.dataset.description),
      currentLang
    );
    tooltipIcon.src = el.dataset.icon;
    tooltip.classList.add('visible');
    moveTooltip(e);
  }

  function moveTooltip(e) {
    const rect = tooltip.getBoundingClientRect();
    let x = e.clientX + 20;
    let y = e.clientY + 20;

    if (x + rect.width > window.innerWidth) x = e.clientX - rect.width - 20;
    if (y + rect.height > window.innerHeight) y = e.clientY - rect.height - 20;

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function hideTooltip() {
    tooltip.classList.remove('visible');
  }
}