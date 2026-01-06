/* banniere.js - Gestion de la navigation active */

/**
 * Initialise la navigation en marquant la page active
 */
export function initBanniereNavigation() {
  // Attendre que le DOM soit prêt
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setActiveNav);
  } else {
    setActiveNav();
  }
}

/**
 * Marque le lien de navigation actif selon la page courante
 */
function setActiveNav() {
  // Récupérer le nom de la page courante (sans extension)
  const currentPage = getCurrentPageName();

  if (!currentPage) return;

  // Trouver et activer le lien correspondant
  const navLinks = document.querySelectorAll('.banniere-nav .nav-link');

  navLinks.forEach(link => {
    const pageName = link.dataset.page;

    if (pageName === currentPage) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
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

  // Extraire le nom du fichier
  const filename = pathname.split('/').pop();

  // Si c'est index.html ou vide, pas de page active
  if (!filename || filename === 'index.html') {
    return null;
  }

  // Retirer l'extension .html
  return filename.replace('.html', '');
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

// Auto-initialisation si le script est chargé
initBanniereNavigation();