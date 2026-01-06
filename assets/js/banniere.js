/* banniere.js - Gestion de la navigation active */

/**
 * Initialise la navigation en marquant la page active
 */
export function initBanniereNavigation() {
  // Attendre un peu pour s'assurer que le DOM est prêt
  setTimeout(setActiveNav, 100);
}

/**
 * Marque le lien de navigation actif selon la page courante
 */
function setActiveNav() {
  // Récupérer le nom de la page courante (sans extension)
  const currentPage = getCurrentPageName();
  
  console.log('[Navigation] Page courante détectée:', currentPage);

  if (!currentPage) {
    console.log('[Navigation] Aucune page détectée, abandon');
    return;
  }

  // Trouver et activer le lien correspondant
  const navLinks = document.querySelectorAll('.banniere-nav .nav-link');
  
  console.log('[Navigation] Nombre de liens trouvés:', navLinks.length);

  navLinks.forEach(link => {
    const pageName = link.dataset.page;
    console.log('[Navigation] Vérification lien:', pageName, 'vs', currentPage);

    if (pageName === currentPage) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
      console.log('[Navigation] ✅ Lien activé:', pageName);
    } else {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    }
  });
}

/**
 * Récupère le nom de la page courante
 * @returns {string} Nom de la page sans extension (ex: "perk", "setarmor")
 */
function getCurrentPageName() {
  const pathname = window.location.pathname;
  console.log('[Navigation] Pathname complet:', pathname);

  // Extraire le nom du fichier
  const filename = pathname.split('/').pop();
  console.log('[Navigation] Filename extrait:', filename);

  // Si c'est index.html ou vide, pas de page active
  if (!filename || filename === 'index.html') {
    return null;
  }

  // Retirer l'extension .html
  const pageName = filename.replace('.html', '');
  console.log('[Navigation] Page name final:', pageName);
  
  return pageName;
}

/**
 * Alternative: marquer la page active manuellement (si besoin)
 * @param {string} pageName - Nom de la page à activer
 */
export function setActivePage(pageName) {
  const navLinks = document.querySelectorAll('.banniere-nav .nav-link');

  navLinks.forEach(link => {
    if (link.dataset.page === pageName) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    } else {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    }
  });
}

// Export pour usage global
window.D2Navigation = {
  initBanniereNavigation,
  setActivePage
};