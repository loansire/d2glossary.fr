async function loadBanniere() {
  try {
    const res = await fetch('assets/html/banniere.html');
    if (!res.ok) throw new Error('Erreur lors du chargement de la bannière.');
    const html = await res.text();
    document.getElementById('banniere-container').innerHTML = html;
  } catch (err) {
    console.error(err);
    document.getElementById('banniere-container').innerHTML = "<p>Bannière non disponible</p>";
  }
}

const subfolders = [
  {
    name: "Traits",
    path: "trait",
    image: "assets/src/Traits_thumb.jpg",
    subtitle: "Définition des termes de doctrines de Destiny 2"
  },
  {
    name: "Champions",
    path: "breaker",
    image: "assets/src/Champions_thumb.jpg",
    subtitle: "Définition des termes de Champions"
  },
  {
    name: "Dégâts",
    path: "damagetype",
    image: "assets/src/Doctrine_thumb.jpg",
    subtitle: "Définition des termes de dégâts en jeu"
  },
  {
    name: "Modificateurs",
    path: "modifier",
    image: "assets/src/modifier_thumb.jpg",
    subtitle: "Définition des modificateurs en jeu"
  },
];

const container = document.getElementById("nav-list");

subfolders.forEach((entry, index) => {
  const card = document.createElement("a");
  card.className = "nav-card animate__animated animate__fadeInUp";  // Ajout de l'animation

  // Calculer le délai en fonction de l'index (pour que les cartes apparaissent en cascade)
  const delay = index * 0.05;  // Délai entre chaque carte (0.2s)
  card.style.animationDelay = `${delay}s`;

  card.href = `${entry.path}.html`;
  card.title = entry.name;

  card.innerHTML = `
    <img src="${entry.image}" class="nav-image" alt="${entry.name}">
    <div class="nav-content">
      <div class="nav-title">${entry.name}</div>
      <div class="nav-subtitle">${entry.subtitle}</div>
    </div>
  `;

  // Ajouter la carte au conteneur
  container.appendChild(card);
});

loadBanniere();
