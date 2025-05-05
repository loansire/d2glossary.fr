<!-- popupitem.js -->
function processDescription(text) {
  return text
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '25') // Remplacer {var:xxx}
    .replace(/ ?•/g, '<br>•') // Sauts avant chaque puce
    .replace(/\.\s*(?=[A-ZÉÈÀÂÎÔÙÜÇ])/g, '.<br>') // Sauts après points
    .replace(/(<br>\s*){2,}/g, '<br>') // Nettoyer doubles sauts
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

function openPopupItem(id, item) {
  const iconEl = document.getElementById('popupitem-icon');
  const nameEl = document.getElementById('popupitem-name');
  const descEl = document.getElementById('popupitem-description');
  const idEl = document.getElementById('popupitem-id');
  const popup = document.getElementById('popupitem');

  const props = item.displayProperties;
  iconEl.src = "https://www.bungie.net" + props.icon;
  iconEl.alt = `d2glossary - ${props.name}`;
  nameEl.textContent = props.name;

  const finalDescription = parseKeywords(processDescription(props.description));
  descEl.innerHTML = finalDescription;
  idEl.textContent = `ID: ${id}`;

  popup.classList.add('show');
  document.body.classList.add('popupitem-open');

  const url = new URL(window.location);
  url.searchParams.set('id', id);
  history.replaceState(null, '', url);

  popup.onclick = (e) => {
    if (e.target.id === 'popupitem') closePopupItem();
  };
}

function closePopupItem() {
  const popup = document.getElementById('popupitem');
  popup.classList.remove('show');
  document.body.classList.remove('popupitem-open');

  const url = new URL(window.location);
  url.searchParams.delete('id');
  history.replaceState(null, '', url);
}

// Gestion globale
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closePopupItem();
});

document.querySelector('.share-btn').addEventListener('click', sharePopupItem, { once: true });

function sharePopupItem() {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  alert("Lien copié dans le presse-papier :\n" + url);
}
