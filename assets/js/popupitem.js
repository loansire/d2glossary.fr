<!-- popupitem.js -->
function processDescription(text) {
  return text
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '25') // Remplacer {var:xxx}
    .replace(/ ?•/g, '<br>•') // Sauts avant chaque puce
    .replace(/\.\s*(?=[A-ZÉÈÀÂÎÔÙÜÇ])/g, '.<br>') // Sauts après points
    .replace(/(<br>\s*){2,}/g, '<br>') // Nettoyer doubles sauts
    .trim();
}

function boldPatterns(text) {
    if (!text) return "";
    text = text.replace(/[\u200B-\u200D\u2060\uFEFF]/g, '');
    const pattern = /(\d+(\.\d+)?)([x%])?/g;
    return text.replace(pattern, '<strong>$&</strong>');
}

function renderClarityInPopup(item) {
    const clarityEl = document.getElementById('popupitem-clarity');
    const claritySeparator = document.getElementById('clarity-separator');

    // Réinitialiser les éléments
    clarityEl.innerHTML = '';

    // Vérifie si l'élément 'descriptions' existe et contient du contenu
    if (!item || !item.descriptions || !item.descriptions.en || item.descriptions.en.length === 0) {
        // Si les données sont vides, cacher le séparateur et la zone de Clarity
        clarityEl.classList.add('hidden');
        claritySeparator.classList.add('hidden');
        return;
    }

    // Si le contenu existe, afficher les éléments
    item.descriptions.en.forEach(section => {
        if (section.linesContent) {
            const p = document.createElement('p');
            section.linesContent.forEach(line => {
                let element;

                if (line.link) {
                    element = document.createElement('a');
                    element.href = line.link;
                    element.target = '_blank';
                    element.innerHTML = boldPatterns(line.text || "");
                } else if (line.text) {
                    element = document.createElement('span');
                    element.innerHTML = boldPatterns(line.text);
                } else {
                    element = document.createElement('span');
                    element.textContent = "";
                }

                if (line.classNames) {
                    line.classNames.forEach(cls => {
                        element.classList.add(cls);
                    });
                }

                p.appendChild(element);
                p.append(' ');
            });
            clarityEl.appendChild(p);
        } else if (section.classNames && section.classNames.includes('spacer')) {
            const spacer = document.createElement('div');
            spacer.style.margin = '1rem 0';
            clarityEl.appendChild(spacer);
        }
    });

    // Afficher les éléments seulement si le contenu est trouvé
    clarityEl.classList.remove('hidden');
    claritySeparator.classList.remove('hidden');
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
  const clarityEl = document.getElementById('popupitem-clarity');
  const claritySeparator = document.getElementById('clarity-separator');

  fetch('data/clarity.json')
      .then(res => res.json())
      .then(data => {
          const itemClarity = data[id];
          renderClarityInPopup(itemClarity);
      })
      .catch(err => {
          console.error('Erreur Clarity JSON:', err);
          document.getElementById('popupitem-clarity').classList.add('hidden');
          document.getElementById('clarity-separator').classList.add('hidden');
      });
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

function sharePopupItem() {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  alert("Lien copié dans le presse-papier :\n" + url);
}
