/* keywordReplacements.js - Définitions multilingues des mots-clés */

export const KEYWORD_REPLACEMENTS = {
  fr: {
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
  },
  en: {
    'Solar': 'solar',
    'Strand': 'strand',
    'Unstoppable': 'unstoppable',
    'stagger': 'unstoppable',
    'Barrier': 'barrier',
    'Shield-Piercing': 'barrier',
    'Overload': 'overload',
    'Disruption': 'overload',
    'Stasis': 'stasis',
    'Void': 'void',
    'Arc': 'arc',
    'Primary': 'primary',
    'Special': 'special',
    'Heavy': 'heavy',
    'PVE': 'pve',
    'PVP': 'pvp',
    'Hunter': 'hunter',
    'Warlock': 'warlock',
    'Titan': 'titan'
  }
};

/**
 * Récupère les remplacements pour la langue courante
 * @param {string} lang - Code de langue ('fr' ou 'en')
 * @returns {Object} Dictionnaire de remplacements
 */
export function getReplacements(lang = 'fr') {
  return KEYWORD_REPLACEMENTS[lang] || KEYWORD_REPLACEMENTS.fr;
}