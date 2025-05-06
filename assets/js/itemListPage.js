export async function loadItemListPage({
  dataFile,
  excludedIds = [],
  containerId,
  inputId,
  filterOptions = {}
}) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
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

        // Un seul hash à vérifier
        if (typeof filterHash === 'number') {
          return item.itemCategoryHashes.includes(filterHash);
        }

        // Tous les hash du filtre doivent être présents
        if (Array.isArray(filterHash)) {
          return filterHash.every(hash => item.itemCategoryHashes.includes(hash));
        }

        return false;
      };

      return (
        props?.name &&
        props?.description &&
        props?.hasIcon &&
        props?.icon &&
        !excludedIds.includes(id) &&
        matchesCategoryHash() &&
        (filterOptions.itemType === undefined || item.itemType === filterOptions.itemType) &&
        (filterOptions.itemSubType === undefined || item.itemSubType === filterOptions.itemSubType) &&
        (filterOptions.classType === undefined || item.classType === filterOptions.classType) &&
        (filterOptions.breakerType === undefined || item.breakerType === filterOptions.breakerType)
      );
    });



    renderItems(filtered);

    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');
    if (itemId && data[itemId]) openPopupItem(itemId, data[itemId]);

    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const filteredResults = filtered.filter(([_, item]) =>
        item.displayProperties.name.toLowerCase().includes(query)
      );
      renderItems(filteredResults);
    });

    function renderItems(list) {
      container.innerHTML = '';
      list.forEach(([id, item], index) => {
        const props = item.displayProperties;
        const card = document.createElement('div');
        card.className = 'card-item animate__animated animate__fadeInUp'; // Animation Animate.css

        // Appliquer un délai progressif
        const delay = Math.min(index * 0.05, 3); // Maximum 1s de délai
        card.style.animationDelay = `${delay}s`;

        // Ajouter le titre avec le nom de l'item
        card.title = props.name; // Ici, on ajoute le titre avec le nom de l'item

        card.innerHTML = `
          <img src="https://www.bungie.net${props.icon}" alt="d2glossary - ${props.name}" />
          <div>${props.name}</div>
        `;
        card.onclick = () => openPopupItem(id, item);
        container.appendChild(card);
      });
    }

  } catch (err) {
    console.error("Erreur lors du chargement des données :", err);
  }
}
