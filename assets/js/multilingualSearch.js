/* multilingualSearch.js - Système de recherche multilingue */

/**
 * Crée un index de recherche multilingue
 * @param {Object} currentLangData - Données dans la langue active
 * @param {Object} otherLangData - Données dans l'autre langue (optionnel)
 * @returns {Map} Index avec clés = termes de recherche, valeurs = IDs
 */
export function createSearchIndex(currentLangData, otherLangData = null) {
  const searchIndex = new Map();

  // Fonction pour normaliser le texte de recherche
  const normalize = (text) => {
    if (!text) return '';
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Retire les accents
      .trim();
  };

  // Indexer les données de la langue courante
  Object.entries(currentLangData).forEach(([id, item]) => {
    const name = item.displayProperties?.name;
    if (!name) return;

    const normalizedName = normalize(name);

    // Ajouter le nom complet
    if (!searchIndex.has(normalizedName)) {
      searchIndex.set(normalizedName, new Set());
    }
    searchIndex.get(normalizedName).add(id);

    // Ajouter aussi les mots individuels (pour recherche partielle)
    const words = normalizedName.split(/\s+/);
    words.forEach(word => {
      if (word.length > 2) { // Ignorer les mots trop courts
        if (!searchIndex.has(word)) {
          searchIndex.set(word, new Set());
        }
        searchIndex.get(word).add(id);
      }
    });
  });

  // Indexer aussi l'autre langue si disponible
  if (otherLangData) {
    Object.entries(otherLangData).forEach(([id, item]) => {
      const name = item.displayProperties?.name;
      if (!name || !currentLangData[id]) return; // Ne garder que les IDs présents dans la langue courante

      const normalizedName = normalize(name);

      // Ajouter le nom complet
      if (!searchIndex.has(normalizedName)) {
        searchIndex.set(normalizedName, new Set());
      }
      searchIndex.get(normalizedName).add(id);

      // Ajouter aussi les mots individuels
      const words = normalizedName.split(/\s+/);
      words.forEach(word => {
        if (word.length > 2) {
          if (!searchIndex.has(word)) {
            searchIndex.set(word, new Set());
          }
          searchIndex.get(word).add(id);
        }
      });
    });
  }

  return searchIndex;
}

/**
 * Recherche des éléments en utilisant l'index multilingue
 * @param {string} query - Texte de recherche
 * @param {Map} searchIndex - Index de recherche
 * @param {Object} data - Données complètes dans la langue active
 * @returns {Array} Liste d'éléments [id, item] correspondant à la recherche
 */
export function searchWithIndex(query, searchIndex, data) {
  if (!query || !query.trim()) {
    return Object.entries(data);
  }

  // Normaliser la requête
  const normalize = (text) => {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  };

  const normalizedQuery = normalize(query);
  const queryWords = normalizedQuery.split(/\s+/);

  // Collecter tous les IDs qui matchent
  const matchingIds = new Set();

  // 1. Chercher les correspondances exactes
  if (searchIndex.has(normalizedQuery)) {
    searchIndex.get(normalizedQuery).forEach(id => matchingIds.add(id));
  }

  // 2. Chercher les correspondances partielles (chaque mot)
  queryWords.forEach(word => {
    if (word.length > 2) {
      // Chercher les clés qui contiennent le mot
      for (const [key, ids] of searchIndex.entries()) {
        if (key.includes(word)) {
          ids.forEach(id => matchingIds.add(id));
        }
      }
    }
  });

  // 3. Fallback : recherche classique dans les données si aucun résultat
  if (matchingIds.size === 0) {
    return Object.entries(data).filter(([_, item]) => {
      const name = item.displayProperties?.name;
      if (!name) return false;
      return normalize(name).includes(normalizedQuery);
    });
  }

  // Convertir les IDs en entrées [id, item]
  return Array.from(matchingIds)
    .filter(id => data[id])
    .map(id => [id, data[id]]);
}

/**
 * Charge les données de l'autre langue pour l'index de recherche
 * @param {string} currentLang - Langue courante
 * @param {string} filename - Nom du fichier (ex: 'item_definitions.json')
 * @returns {Promise<Object>} Données dans l'autre langue
 */
export async function loadOtherLanguageData(currentLang, filename) {
  const otherLang = currentLang === 'fr' ? 'en' : 'fr';
  const url = `data/${otherLang}/${filename}`;

  try {
    // Charger sans loader (en arrière-plan)
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.warn(`[MultilingualSearch] Impossible de charger ${url}:`, err);
    return null;
  }
}

// Export pour usage global
window.D2MultilingualSearch = {
  createSearchIndex,
  searchWithIndex,
  loadOtherLanguageData
};