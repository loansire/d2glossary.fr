export async function loadItemListPage({
  dataFile,
  excludedIds = [],
  containerId,
  inputId
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
      return (
        props?.name &&
        props?.description &&
        props?.hasIcon &&
        props?.icon &&
        !excludedIds.includes(id)
      );
    });

    renderItems(filtered);

    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');
    if (itemId && data[itemId]) openPopupItem(itemId);

    input?.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const filteredResults = filtered.filter(([_, item]) =>
        item.displayProperties.name.toLowerCase().includes(query)
      );
      renderItems(filteredResults);
    });

    function renderItems(list) {
      container.innerHTML = '';
      for (const [id, item] of list) {
        const props = item.displayProperties;
        const card = document.createElement('div');
        card.className = 'trait-card';
        card.innerHTML = `
          <img src="https://www.bungie.net${props.icon}" alt="${props.name}" />
          <div>${props.name}</div>
        `;
        card.onclick = () => openPopupItem(id);
        container.appendChild(card);
      }
    }

  } catch (err) {
    console.error("Erreur lors du chargement des données :", err);
  }
}
