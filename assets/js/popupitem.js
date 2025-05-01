function openPopupItem(id, item) {
  const props = item.displayProperties;

  document.getElementById('popupitem-icon').src = "https://www.bungie.net" + props.icon;
  document.getElementById('popupitem-name').textContent = props.name;
  document.getElementById('popupitem-description').textContent = props.description;

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
