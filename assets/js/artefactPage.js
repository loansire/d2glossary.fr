/* artefactPage.js - Gestion de la page artefact */
import {
  loadJSON,
  processDescription,
  parseKeywords,
  escapeHtml,
  getBungieIconUrl,
  copyToClipboard,
  getCurrentUrl
} from './utils.js';

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

  let artifactData = null;
  let selectedItems = new Set();
  let tierRequirements = [];
  let currentMode = 'consultation';

  initModeSwitch();
  await loadData();

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

  function displayArtifact(data) {
    const artifactId = Object.keys(data)[0];
    const artifact = data[artifactId];

    // Créer les marqueurs de tiers
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

    // Créer les colonnes
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
        html += `
          <div class="item-icon"
               data-item-id="${itemId}"
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

    // Event listeners
    document.querySelectorAll('.item-icon').forEach(icon => {
      icon.addEventListener('click', toggleSelection);
      icon.addEventListener('mouseenter', showTooltip);
      icon.addEventListener('mousemove', moveTooltip);
      icon.addEventListener('mouseleave', hideTooltip);
    });
  }

  function toggleSelection(event) {
    if (currentMode === 'consultation') return;

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
    // Nettoyer les sélections invalides
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

    // Mise à jour des marqueurs
    document.querySelectorAll('.tier-marker').forEach((marker, index) => {
      const requirement = parseInt(marker.dataset.requirement);
      marker.classList.remove('unlocked', 'next');

      if (index < tierRequirements.length - 1 && total >= tierRequirements[index + 1]) {
        marker.classList.add('unlocked');
      } else if (total >= requirement) {
        marker.classList.add('next');
      }
    });

    // Mise à jour des colonnes
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
    const el = e.currentTarget;
    tooltipName.textContent = el.dataset.name;
    tooltipDescription.innerHTML = parseKeywords(processDescription(el.dataset.description));
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