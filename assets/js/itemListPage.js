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
        props?.icon &&  // Retirer la vérification de hasIcon ici
        !excludedIds.includes(id) &&
        matchesCategoryHash() &&
        (filterOptions.itemType === undefined || item.itemType === filterOptions.itemType) &&
        (filterOptions.itemSubType === undefined || item.itemSubType === filterOptions.itemSubType) &&
        (filterOptions.classType === undefined || item.classType === filterOptions.classType) &&
        (filterOptions.breakerType === undefined || item.breakerType === filterOptions.breakerType)
      );
    });

    // Display total number of results on initial page load
    updateResultCount(filtered);

    // Appeler la fonction pour rendre les éléments filtrés
    renderItems(filtered);

    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');
    if (itemId && data[itemId]) openPopupItem(itemId, data[itemId]);

    // Ajouter l'écouteur pour la recherche
    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const filteredResults = filtered.filter(([_, item]) =>
        item.displayProperties.name.toLowerCase().includes(query)
      );
      updateResultCount(filteredResults); // Update result count on search
      renderItems(filteredResults);

      // Afficher ou masquer le bouton clear
      if (e.target.value) {
        clearButton.style.display = 'block'; // Afficher le bouton clear
      } else {
        clearButton.style.display = 'none'; // Cacher le bouton clear
      }
    });

    // Ajouter un gestionnaire d'événement pour effacer l'input
    clearButton?.addEventListener('click', () => {
      input.value = '';  // Effacer le texte
      clearButton.style.display = 'none';  // Cacher le bouton clear
      updateResultCount(filtered);  // Réinitialiser le comptage des résultats
      renderItems(filtered);  // Réafficher les éléments
    });

    // Fonction pour afficher les éléments
    function renderItems(list) {
      // Mélange des éléments
      const shuffledList = list.sort(() => Math.random() - 0.5); // Mélange aléatoire

      container.innerHTML = '';
      shuffledList.forEach(([id, item], index) => {
        const props = item.displayProperties;
        const card = document.createElement('div');
        card.className = 'card-item animate__animated animate__fadeInUp'; // Animation Animate.css

        const delay = Math.min(index * 0.05, 3); // Maximum 3s de délai
        card.style.animationDelay = `${delay}s`;

        card.title = props.name;

        card.innerHTML = `
          <img src="https://www.bungie.net${props.icon}" alt="d2glossary - ${props.name}" />
          <div>${props.name}</div>
        `;
        card.onclick = () => openPopupItem(id, item);
        container.appendChild(card);
      });
    }

    // Function to update the result count
    function updateResultCount(list) {
      resultCount.textContent = `Résultats trouvés: ${list.length}`;
    }

  } catch (err) {
    console.error("Erreur lors du chargement des données :", err);
  }
}
