/* setarmorPage.js - Gestion de la page des sets d'armure */
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
  shuffleArray,
  normalizeName,
  onEscapeKey
} from './utils.js';

export async function loadSetArmorPage({
  dataFile,
  containerId,
  inputId
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  const resultCount = document.getElementById('result-count');
  const clearButton = document.getElementById('clear-button');
  const popupContainer = document.getElementById('popupitem-container');
  const banniereContainer = document.getElementById('banniere-container');

  // Fonctions de popup définies en premier
  function closePopupItem() {
    const popup = document.getElementById('popupitem');
    if (popup) {
      popup.classList.remove('show');
      document.body.classList.remove('popupitem-open');
      removeUrlParam('id');
    }
  }

  function sharePopupItem() {
    const url = getCurrentUrl();
    copyToClipboard(url, 'Lien copié dans le presse-papier :\n' + url);
  }

  function copyDiscordMarkdown() {
    const name = document.getElementById('popupitem-name')?.textContent.trim();
    const url = getCurrentUrl();
    const iconSwitch = document.getElementById('iconSwitch');
    const iconEnabled = iconSwitch?.checked;

    let markdown = `[${name}](<${url}>)`;

    if (iconEnabled && name) {
      const cleanName = normalizeName(name);
      markdown = `:${cleanName}: ${markdown}`;
    }

    copyToClipboard(markdown, 'Lien Discord copié dans le presse-papier:\n' + markdown);
  }

  // Exposer globalement AVANT le chargement du HTML
  window.closePopupItem = closePopupItem;
  window.sharePopupItem = sharePopupItem;
  window.copyDiscordMarkdown = copyDiscordMarkdown;

  // Escape key handler
  onEscapeKey(closePopupItem);

  // Charger les composants HTML
  await loadHTML('assets/html/popupitem.html', popupContainer);
  await loadHTML('assets/html/banniere.html', banniereContainer);

  // Attacher les event listeners après chargement du HTML
  const discordBtn = document.getElementById('discord-btn');
  if (discordBtn) {
    // Supprimer l'ancien onclick s'il existe et ajouter le listener
    discordBtn.onclick = null;
    discordBtn.addEventListener('click', copyDiscordMarkdown);
  }

  try {
    const data = await loadJSON(dataFile);
    if (!data) throw new Error('Données non chargées');

    const dataArray = Object.entries(data)
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

    updateResultCount(dataArray);
    renderSets(dataArray);

    // Gestion de l'URL avec ID
    const perkHash = getUrlParam('id');
    if (perkHash) {
      for (const setData of dataArray) {
        const perk = setData.setPerks.find(p => String(p.sandboxPerkHash) === String(perkHash));
        if (perk) {
          openPerkPopup(perk.sandboxPerkHash, perk, setData);
          break;
        }
      }
    }

    // Gestion de la recherche
    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const filteredResults = dataArray.filter(set =>
        set.displayProperties.name.toLowerCase().includes(query)
      );
      updateResultCount(filteredResults);
      renderSets(filteredResults);
      clearButton.style.display = e.target.value ? 'block' : 'none';
    });

    // Bouton clear
    clearButton?.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      updateResultCount(dataArray);
      renderSets(dataArray);
    });

    function renderSets(list) {
      const shuffledList = shuffleArray(list);
      container.innerHTML = '';

      shuffledList.forEach((setData, index) => {
        const card = createSetCard(setData);
        card.classList.add('animate__animated', 'animate__fadeInUp');
        card.style.animationDelay = `${Math.min(index * 0.05, 3)}s`;
        container.appendChild(card);
      });
    }

    function createSetCard(setData) {
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
    }

    function createPerkElement(perk, setData) {
      const div = document.createElement('div');
      div.className = 'perk';

      const props = perk.displayProperties || {};
      const icon = props.icon || '';
      const name = props.name || 'Perk inconnu';

      div.innerHTML = `
        <img src="${getBungieIconUrl(icon)}" alt="${name}"/>
        <span>${name}</span>
      `;
      div.onclick = () => openPerkPopup(perk.sandboxPerkHash, perk, setData);
      return div;
    }

    function openPerkPopup(sandboxPerkHash, perk, setData) {
      const iconEl = document.getElementById('popupitem-icon');
      const nameEl = document.getElementById('popupitem-name');
      const descEl = document.getElementById('popupitem-description');
      const idEl = document.getElementById('popupitem-id');
      const popup = document.getElementById('popupitem');

      // Masquer clarity, afficher setarmor
      document.getElementById('clarity-separator')?.classList.add('hidden');
      document.getElementById('popupitem-clarity')?.classList.add('hidden');

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

      popup.classList.add('show');
      document.body.classList.add('popupitem-open');

      setUrlParam('id', sandboxPerkHash);

      popup.onclick = (e) => {
        if (e.target.id === 'popupitem') closePopupItem();
      };
    }

    function renderPerkContent(perk, setData, contentContainer) {
      contentContainer.innerHTML = '';

      // Nom du set
      const setNameDiv = document.createElement('div');
      setNameDiv.className = 'setarmor-set-name';
      setNameDiv.innerHTML = `<strong>Set :</strong> ${setData.displayProperties.name}`;
      contentContainer.appendChild(setNameDiv);

      // Compteur requis
      const requiredCount = document.createElement('div');
      requiredCount.className = 'setarmor-required-count';
      requiredCount.innerHTML = `<strong>Pièces requises :</strong> ${perk.requiredSetCount} armures`;
      contentContainer.appendChild(requiredCount);

      // Séparateur
      const separator = document.createElement('hr');
      separator.className = 'setarmor-items-separator';
      contentContainer.appendChild(separator);

      // Section des items par classe
      const order = [3, 0, 2, 4, 1]; // casque, gants, plastron, jambes, marque

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
  }
}