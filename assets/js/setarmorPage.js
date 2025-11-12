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

  const prefix = "https://www.bungie.net";

  // Charger les composants HTML
  async function loadHTML(url, target) {
    const res = await fetch(url);
    const html = await res.text();
    target.innerHTML = html;
  }

  await loadHTML('assets/html/popupitem.html', popupContainer);
  await loadHTML('assets/html/banniere.html', banniereContainer);

  try {
    const res = await fetch(dataFile);
    const data = await res.json();
    const dataArray = Object.entries(data).map(([id, setData]) => ({
      id,
      hash: setData.hash,
      ...setData
    }));

    updateResultCount(dataArray);
    renderSets(dataArray);

    // Gestion de l'URL avec ID (recherche par sandboxPerkHash)
    const urlParams = new URLSearchParams(window.location.search);
    const perkHash = urlParams.get('id');
    if (perkHash) {
      // Trouver le set et le perk correspondant
      for (const setData of dataArray) {
        const perk = setData.setPerks.find(p => p.sandboxPerkHash == perkHash);
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

      if (e.target.value) {
        clearButton.style.display = 'block';
      } else {
        clearButton.style.display = 'none';
      }
    });

    // Bouton clear
    clearButton?.addEventListener('click', () => {
      input.value = '';
      clearButton.style.display = 'none';
      updateResultCount(dataArray);
      renderSets(dataArray);
    });

    function renderSets(list) {
      const shuffledList = list.sort(() => Math.random() - 0.5);
      container.innerHTML = '';

      shuffledList.forEach((setData, index) => {
        const card = createSetCard(setData);
        card.classList.add('animate__animated', 'animate__fadeInUp');
        const delay = Math.min(index * 0.05, 3);
        card.style.animationDelay = `${delay}s`;
        container.appendChild(card);
      });
    }

    function createSetCard(setData) {
      const card = document.createElement("div");
      card.className = "card";

      const title = document.createElement("div");
      title.className = "title";
      title.textContent = setData.displayProperties.name;

      const desc = document.createElement("div");
      desc.className = "description";
      desc.textContent = setData.displayProperties.description || "";

      const grid = document.createElement("div");
      grid.className = "grid";

      const armure2 = document.createElement("div");
      armure2.className = "perk-section";
      armure2.innerHTML = `<div class="perk-title">Armure x2</div>`;

      const armure4 = document.createElement("div");
      armure4.className = "perk-section";
      armure4.innerHTML = `<div class="perk-title">Armure x4</div>`;

      setData.setPerks.forEach(perk => {
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
      const div = document.createElement("div");
      div.className = "perk";
      div.innerHTML = `
        <img src="${prefix + perk.displayProperties.icon}" alt="${perk.displayProperties.name}"/>
        <span>${perk.displayProperties.name}</span>
      `;
      // Chaque perk ouvre sa propre popup
      div.onclick = () => openPerkPopup(perk.sandboxPerkHash, perk, setData);
      return div;
    }

    function openPerkPopup(sandboxPerkHash, perk, setData) {
      const iconEl = document.getElementById('popupitem-icon');
      const nameEl = document.getElementById('popupitem-name');
      const descEl = document.getElementById('popupitem-description');
      const idEl = document.getElementById('popupitem-id');
      const popup = document.getElementById('popupitem');

      // Masquer le clarity separator et clarity content
      document.getElementById('clarity-separator').classList.add('hidden');
      document.getElementById('popupitem-clarity').classList.add('hidden');

      // Afficher le setarmor separator et content
      const setarmorSeparator = document.getElementById('setarmor-separator');
      const setarmorContent = document.getElementById('popupitem-setarmor');
      setarmorSeparator.classList.remove('hidden');
      setarmorContent.classList.remove('hidden');

      // Remplir les infos du header avec les données du perk
      const perkProps = perk.displayProperties;

      iconEl.src = prefix + perkProps.icon;
      iconEl.alt = `d2glossary - ${perkProps.name}`;
      nameEl.textContent = perkProps.name;

      // Description du perk
      descEl.innerHTML = processDescription(perkProps.description);
      descEl.style.display = 'block';

      idEl.textContent = `ID: ${sandboxPerkHash}`;

      // Construire le contenu avec le nom du set et les items
      renderPerkContent(perk, setData, setarmorContent);

      popup.classList.add('show');
      document.body.classList.add('popupitem-open');

      const url = new URL(window.location);
      url.searchParams.set('id', sandboxPerkHash);
      history.replaceState(null, '', url);

      popup.onclick = (e) => {
        if (e.target.id === 'popupitem') closePerkPopup();
      };
    }

    function renderPerkContent(perk, setData, container) {
      container.innerHTML = '';

      // Afficher le nom du set
      const setNameDiv = document.createElement('div');
      setNameDiv.className = 'setarmor-set-name';
      setNameDiv.innerHTML = `<strong>Set :</strong> ${setData.displayProperties.name}`;
      container.appendChild(setNameDiv);

      // Afficher le compteur requis
      const requiredCount = document.createElement('div');
      requiredCount.className = 'setarmor-required-count';
      requiredCount.innerHTML = `<strong>Pièces requises :</strong> ${perk.requiredSetCount} armures`;
      container.appendChild(requiredCount);

      // Séparateur
      const separator = document.createElement('hr');
      separator.className = 'setarmor-items-separator';
      container.appendChild(separator);

      // Section des items par classe
      const order = [3, 0, 2, 4, 1]; // casque, gants, plastron, jambes, marque

      const classesContainer = document.createElement("div");
      classesContainer.className = "modal-classes";

      function createClassSection(title, baseIndex) {
        const section = document.createElement("div");
        section.className = "class-section";

        const classTitle = document.createElement("div");
        classTitle.className = "class-title";
        classTitle.textContent = title;
        section.appendChild(classTitle);

        const grid = document.createElement("div");
        grid.className = "items-grid";

        order.forEach(i => {
          const item = setData.setItems[baseIndex + i];
          if (item) {
            const img = document.createElement("img");
            img.src = prefix + item.icon;
            img.alt = item.name;
            img.title = item.name;
            grid.appendChild(img);
          }
        });

        section.appendChild(grid);
        return section;
      }

      classesContainer.appendChild(createClassSection("Chasseur", 0));
      classesContainer.appendChild(createClassSection("Titan", 5));
      classesContainer.appendChild(createClassSection("Arcaniste", 10));

      container.appendChild(classesContainer);
    }

    function closePerkPopup() {
      const popup = document.getElementById('popupitem');
      popup.classList.remove('show');
      document.body.classList.remove('popupitem-open');

      const url = new URL(window.location);
      url.searchParams.delete('id');
      history.replaceState(null, '', url);
    }

    // Rendre closePerkPopup accessible globalement
    window.closePerkPopup = closePerkPopup;
    // Alias pour compatibilité avec popupitem.js
    window.closePopupItem = closePerkPopup;

    function updateResultCount(list) {
      resultCount.textContent = `Résultats trouvés: ${list.length}`;
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

  } catch (err) {
    console.error("Erreur lors du chargement des données :", err);
  }
}