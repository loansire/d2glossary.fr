export async function loadArtefactPage({
  dataFile,
  containerId,
  tooltipId
}) {
  const BUNGIE_BASE_URL = 'https://www.bungie.net';
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
  let perksPerTier = [];
  let currentMode = 'consultation';

  // Charger les composants HTML (bannière déjà chargée par le HTML principal)

  // Initialiser le mode switch
  initModeSwitch();

  // Charger les données
  await loadJsonData();

  function initModeSwitch() {
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        switchMode(mode);
      });
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
      document.querySelectorAll('.item-icon.selected').forEach(element => {
        element.classList.remove('selected');
      });
    } else {
      document.body.classList.remove('consultation-mode');
      document.body.classList.add('configuration-mode');
      updateProgress();
    }
  }

  async function loadJsonData() {
    try {
      const response = await fetch(dataFile);
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      const data = await response.json();
      artifactData = data;
      displayArtifact(data);
      loadSelectionFromURL();
      if (currentMode === 'configuration') {
        updateProgress();
      }
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
      content.innerHTML = `
        <div class="error-message">
          <h3>⚠️ Erreur de chargement</h3>
          <p>Impossible de charger les données de l'artefact</p>
          <p style="font-size: 0.85em; margin-top: 10px; opacity: 0.7;">${error.message}</p>
        </div>
      `;
    }
  }

  function displayArtifact(data) {
    const artifactId = Object.keys(data)[0];
    const artifact = data[artifactId];

    // Compter les perks par tier
    perksPerTier = artifact.tiers.map(tier => {
      const lastSevenItems = tier.items.slice(-7);
      return lastSevenItems.filter(item =>
        item.name && item.name.trim() !== '' && item.icon
      ).length;
    });

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
        <div class="tier-marker" data-tier="${index}" data-requirement="${requirement}" style="flex: ${sectionSize} 0 0;">
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

      const lastSevenItems = tier.items.slice(-7);
      const validItems = lastSevenItems.filter(item =>
        item.name && item.name.trim() !== '' && item.icon
      );

      validItems.forEach(item => {
        const iconUrl = item.icon ? `${BUNGIE_BASE_URL}${item.icon}` : '';
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

      html += `
          </div>
        </div>
      `;
    });

    html += '</div>';
    content.innerHTML = html;

    // Ajouter les event listeners
    document.querySelectorAll('.item-icon').forEach(icon => {
      icon.addEventListener('click', toggleSelection);
      icon.addEventListener('mouseenter', showTooltip);
      icon.addEventListener('mousemove', moveTooltip);
      icon.addEventListener('mouseleave', hideTooltip);
    });
  }

  function toggleSelection(event) {
    if (currentMode === 'consultation') {
      return;
    }

    const element = event.currentTarget;
    const itemId = element.dataset.itemId;

    if (selectedItems.has(itemId)) {
      selectedItems.delete(itemId);
      element.classList.remove('selected');
    } else {
      if (selectedItems.size < MAX_SELECTIONS) {
        selectedItems.add(itemId);
        element.classList.add('selected');
      } else {
        alert(`Vous ne pouvez sélectionner que ${MAX_SELECTIONS} items maximum !`);
        return;
      }
    }

    updateProgress();
  }

  function updateProgress() {
    const totalSelections = selectedItems.size;

    const itemsToRemove = [];
    selectedItems.forEach(itemId => {
      const tierIndex = parseInt(itemId.split('-')[0]);
      const requirement = tierRequirements[tierIndex] || 0;

      if (totalSelections < requirement) {
        itemsToRemove.push(itemId);
        const element = document.querySelector(`[data-item-id="${itemId}"]`);
        if (element) {
          element.classList.remove('selected');
        }
      }
    });

    itemsToRemove.forEach(itemId => selectedItems.delete(itemId));

    const cleanedTotal = selectedItems.size;

    progressCounter.textContent = `${cleanedTotal}/${MAX_SELECTIONS}`;

    const progressPercent = (cleanedTotal / MAX_SELECTIONS) * 100;
    progressBar.style.width = `${progressPercent}%`;

    document.querySelectorAll('.tier-marker').forEach((marker, index) => {
      const requirement = parseInt(marker.dataset.requirement);
      marker.classList.remove('unlocked', 'next');

      if (index < tierRequirements.length - 1 && cleanedTotal >= tierRequirements[index + 1]) {
        marker.classList.add('unlocked');
      }
      else if (cleanedTotal >= requirement) {
        marker.classList.add('next');
      }
    });

    document.querySelectorAll('.tier-column').forEach(column => {
      const tier = parseInt(column.dataset.tier);
      const requirement = tierRequirements[tier] || 0;

      if (cleanedTotal >= requirement) {
        column.classList.remove('locked');
      } else {
        column.classList.add('locked');
      }
    });
  }

  function loadSelectionFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const selection = urlParams.get('selection');

    if (selection) {
      try {
        const items = selection.split(',');
        items.forEach(itemId => {
          if (itemId && selectedItems.size < MAX_SELECTIONS) {
            selectedItems.add(itemId);
            const element = document.querySelector(`[data-item-id="${itemId}"]`);
            if (element) {
              element.classList.add('selected');
            }
          }
        });
      } catch (error) {
        console.error('Erreur lors du chargement de la sélection:', error);
      }
    }
  }

  shareBtn.addEventListener('click', () => {
    if (selectedItems.size === 0) {
      alert('Aucune sélection à partager !');
      return;
    }

    const selectionString = Array.from(selectedItems).join(',');
    const url = new URL(window.location.href);
    url.searchParams.set('selection', selectionString);

    navigator.clipboard.writeText(url.toString())
      .then(() => alert('Lien copié dans le presse-papier !\n' + url.toString()))
      .catch(err => alert('Erreur lors de la copie : ' + err));
  });

  resetBtn.addEventListener('click', () => {
    if (confirm('Voulez-vous réinitialiser votre sélection ?')) {
      selectedItems.clear();
      document.querySelectorAll('.item-icon.selected').forEach(element => {
        element.classList.remove('selected');
      });
      updateProgress();

      const url = new URL(window.location.href);
      url.searchParams.delete('selection');
      history.replaceState(null, '', url);
    }
  });

  function showTooltip(event) {
    const element = event.currentTarget;
    tooltipName.textContent = element.dataset.name;

    const processedDesc = processDescription(element.dataset.description);
    const finalDesc = parseKeywords(processedDesc);
    tooltipDescription.innerHTML = finalDesc;

    tooltipIcon.src = element.dataset.icon;
    tooltip.classList.add('visible');
    moveTooltip(event);
  }

  function moveTooltip(event) {
    const tooltipRect = tooltip.getBoundingClientRect();
    let x = event.clientX + 20;
    let y = event.clientY + 20;

    if (x + tooltipRect.width > window.innerWidth) {
      x = event.clientX - tooltipRect.width - 20;
    }
    if (y + tooltipRect.height > window.innerHeight) {
      y = event.clientY - tooltipRect.height - 20;
    }

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function hideTooltip() {
    tooltip.classList.remove('visible');
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function processDescription(text) {
    if (!text) return '';
    return text
      .replace(/\{var:[a-zA-Z0-9_]+\}/g, '25')
      .replace(/ ?•/g, '<br>•')
      .replace(/\.\s*(?=[A-ZÉÈÀÂÎÔÙÜÇ])/g, '.<br>')
      .replace(/(<br>\s*){2,}/g, '<br>')
      .trim();
  }

  function parseKeywords(text) {
    const replacements = {
      'Solaire': 'solar',
      'Filobscur': 'strand',
      'Chancellement': 'unstoppable',
      'Perforation de bouclier': 'barrier',
      'Perturbation': 'overload',
      'Stase': 'stasis',
      'Abyssal': 'void',
      'Cryo-électrique': 'arc',
      'Primaire': 'primary',
      'Spéciale': 'special',
      'Lourde': 'heavy',
      'PVE': 'pve',
      'PVP': 'pvp',
      'Chasseur': 'hunter',
      'Arcaniste': 'warlock',
      'Titan': 'titan'
    };

    for (const [key, className] of Object.entries(replacements)) {
      const regex = new RegExp(`\\[${key}\\](\\s*)(\\w+)`, 'g');
      text = text.replace(
        regex,
        `<span class="icon-word"><span class="${className}"></span>&nbsp;$2</span>`
      );
    }
    return text;
  }
}