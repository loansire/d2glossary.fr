function parseDescription(text) {
  const replacements = {
    '\\[Solaire\\]': '<span class="solar"></span>',
    '\\[Filobscur\\]': '<span class="strand"></span>',
    '\\[Chancellement\\]': '<span class="unstoppable"></span>',
    '\\[Perforation de bouclier\\]': '<span class="barrier"></span>',
    '\\[Perturbation\\]': '<span class="overload"></span>',
    '\\[Stase\\]': '<span class="stasis"></span>',
    '\\[Abyssal\\]': '<span class="void"></span>',
    '\\[Cryo-électrique\\]': '<span class="arc"></span>',
    '\\[Primaire\\]': '<span class="primary"></span>',
    '\\[Spéciale\\]': '<span class="special"></span>',
    '\\[Lourde\\]': '<span class="heavy"></span>',
    '\\[PVE\\]': '<span class="pve"></span>',
    '\\[PVP\\]': '<span class="pvp"></span>',
    '\\[Chasseur\\]': '<span class="hunter"></span>',
    '\\[Arcaniste\\]': '<span class="warlock"></span>',
    '\\[Titan\\]': '<span class="titan"></span>'
  };

  for (const [key, value] of Object.entries(replacements)) {
    const regex = new RegExp(key, 'g');
    text = text.replace(regex, value);
  }

  return text;
}

function replaceVariablesInDescription(description) {
  // Remplacer toutes les occurrences de {var:xxxxx} par "25"
  const regex = /\{var:([a-zA-Z0-9_]+)\}/g; // Recherche du pattern {var:xxxxx}
  return description.replace(regex, '25'); // Remplace par "25"
}


function openPopupItem(id, item) {
  const props = item.displayProperties;

  document.getElementById('popupitem-icon').src = "https://www.bungie.net" + props.icon;
  document.getElementById('popupitem-name').textContent = props.name;
  const modifiedDescription = replaceVariablesInDescription(props.description);
  document.getElementById('popupitem-description').innerHTML = parseDescription(modifiedDescription);
  document.getElementById('popupitem-id').textContent = `ID: ${id}`;

  document.getElementById('popupitem').classList.add('show');
  document.body.classList.add('popupitem-open');

  const url = new URL(window.location);
  url.searchParams.set('id', id);
  history.replaceState(null, '', url);

  document.getElementById('popupitem').onclick = (e) => {
    if (e.target.id === 'popupitem') closePopupItem();
  };

  // Ajouter l'event listener pour le bouton de partage
  document.querySelector('.share-btn').addEventListener('click', sharePopupItem);

  // Écouter l'événement "keydown" pour fermer la popup avec la touche Échap
  document.addEventListener('keydown', handleEscapeKey);
}

// Ferme la popup et nettoie l'URL
function closePopupItem() {
  document.getElementById('popupitem').classList.remove('show');
  document.body.classList.remove('popupitem-open');

  const url = new URL(window.location);
  url.searchParams.delete('id');
  history.replaceState(null, '', url);

  // Retirer l'événement "keydown" une fois que la popup est fermée
  document.removeEventListener('keydown', handleEscapeKey);

  // Retirer l'event listener pour le bouton partager
  document.querySelector('.share-btn').removeEventListener('click', sharePopupItem);
}

// Fonction qui gère la touche "Échap"
function handleEscapeKey(e) {
  if (e.key === 'Escape') {
    closePopupItem();
  }
}

function sharePopupItem() {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  alert("Lien copié dans le presse-papier :\n" + url);
}
