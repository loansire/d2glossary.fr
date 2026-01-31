/**
 * Cloudflare Worker pour D2Glossary - Embeds Discord
 * Supporte le paramètre ?lang= pour les contenus multilingues
 */

// Configuration
const SITE_URL = 'https://d2glossary.fr';
const BUNGIE_BASE_URL = 'https://www.bungie.net';
const DATA_BASE_URL = 'https://d2glossary.fr/data';
const DDCVACUUM_URL = 'https://d2glossary.fr/data/ddcvacuum.json';
const DEFAULT_LANGUAGE = 'fr';
const SUPPORTED_LANGUAGES = ['fr', 'en'];

// User agent Discord
const DISCORD_BOT = 'discordbot';

// Mapping des pages avec leurs configurations
const PAGE_CONFIG = {
  'perk': { file: 'item_definitions.json', label: 'Perk', labelEn: 'Perk' },
  'trait': { file: 'trait_definitions.json', label: 'Trait', labelEn: 'Trait' },
  'breaker': { file: 'breaker_definitions.json', label: 'Champion', labelEn: 'Champion' },
  'damagetype': { file: 'damagetype_definitions.json', label: 'Dégât', labelEn: 'Damage Type' },
  'modifier': { file: 'modifier_definitions.json', label: 'Modificateur', labelEn: 'Modifier' },
  'setarmor': { file: 'setarmor_definitions_enriched.json', label: 'Set d\'armure', labelEn: 'Armor Set', type: 'setarmor' },
  'artefact': { file: 'artefact_definitions_enriched.json', label: 'Artefact', labelEn: 'Artifact', type: 'artefact' }
};

// Configuration du fallback générique par page
const PAGE_FALLBACK = {
  'index': {
    title: 'D2Glossary - Glossaire Destiny 2',
    titleEn: 'D2Glossary - Destiny 2 Glossary',
    description: 'Dictionnaire bilingue des termes de Destiny 2. Perks, traits, modificateurs, sets d\'armure et plus encore.',
    descriptionEn: 'Bilingual dictionary of Destiny 2 terms. Perks, traits, modifiers, armor sets and more.',
    icon: `${SITE_URL}/assets/src/ico/logo-d2glossaire.png`
  },
  'perk': {
    title: 'D2Glossary - Perks d\'armes',
    titleEn: 'D2Glossary - Weapon Perks',
    description: 'Catalogue complet des perks d\'armes de Destiny 2 avec descriptions détaillées.',
    descriptionEn: 'Complete catalog of Destiny 2 weapon perks with detailed descriptions.',
    icon: `${SITE_URL}/assets/src/Perks_thumb.jpg`
  },
  'trait': {
    title: 'D2Glossary - Traits élémentaires',
    titleEn: 'D2Glossary - Elemental Traits',
    description: 'Découvrez tous les traits et verbes élémentaires de Destiny 2.',
    descriptionEn: 'Discover all elemental traits and verbs of Destiny 2.',
    icon: `${SITE_URL}/assets/src/Traits_thumb.jpg`
  },
  'breaker': {
    title: 'D2Glossary - Champions',
    titleEn: 'D2Glossary - Champions',
    description: 'Guide des types de champions et leurs contres dans Destiny 2.',
    descriptionEn: 'Guide to champion types and their counters in Destiny 2.',
    icon: `${SITE_URL}/assets/src/Champions_thumb.jpg`
  },
  'damagetype': {
    title: 'D2Glossary - Types de dégâts',
    titleEn: 'D2Glossary - Damage Types',
    description: 'Tous les types de dégâts élémentaires de Destiny 2.',
    descriptionEn: 'All elemental damage types in Destiny 2.',
    icon: `${SITE_URL}/assets/src/Doctrine_thumb.jpg`
  },
  'modifier': {
    title: 'D2Glossary - Modificateurs',
    titleEn: 'D2Glossary - Modifiers',
    description: 'Liste complète des modificateurs d\'activités de Destiny 2.',
    descriptionEn: 'Complete list of Destiny 2 activity modifiers.',
    icon: `${SITE_URL}/assets/src/modifier_thumb.jpg`
  },
  'setarmor': {
    title: 'D2Glossary - Sets d\'armure',
    titleEn: 'D2Glossary - Armor Sets',
    description: 'Tous les sets d\'armure et leurs bonus dans Destiny 2.',
    descriptionEn: 'All armor sets and their bonuses in Destiny 2.',
    icon: `${SITE_URL}/assets/src/Setarmor_thumb.jpg`
  },
  'artefact': {
    title: 'D2Glossary - Artefact saisonnier',
    titleEn: 'D2Glossary - Seasonal Artifact',
    description: 'Détails de l\'artefact saisonnier actuel de Destiny 2.',
    descriptionEn: 'Details of the current Destiny 2 seasonal artifact.',
    icon: `${SITE_URL}/assets/src/artefact_thumb.jpg`
  }
};

// Cache pour DDCVacuum (indexé par hash)
let ddcvacuumCache = null;

/**
 * Vérifie si c'est le bot Discord
 */
function isDiscordBot(userAgent) {
  if (!userAgent) return false;
  return userAgent.toLowerCase().includes(DISCORD_BOT);
}

/**
 * Valide et normalise le paramètre de langue
 */
function getValidLanguage(langParam) {
  if (!langParam) return DEFAULT_LANGUAGE;
  const lang = langParam.toLowerCase();
  return SUPPORTED_LANGUAGES.includes(lang) ? lang : DEFAULT_LANGUAGE;
}

/**
 * Récupère le label selon la langue
 */
function getLocalizedLabel(config, lang) {
  return lang === 'en' ? (config.labelEn || config.label) : config.label;
}

/**
 * Charge les données JSON
 */
async function loadData(lang, filename) {
  try {
    const url = `${DATA_BASE_URL}/${lang}/${filename}`;
    const response = await fetch(url, { cf: { cacheTtl: 3600 } });
    if (!response.ok) return null;
    return await response.json();
  } catch (e) {
    console.error(`Erreur chargement:`, e);
    return null;
  }
}

/**
 * Transforme la structure par catégories en index par hash
 */
function indexByHash(rawData) {
  const indexed = {};
  for (const category of Object.values(rawData)) {
    if (!Array.isArray(category)) continue;
    for (const item of category) {
      if (item.hash) {
        indexed[String(item.hash)] = item;
      }
    }
  }
  return indexed;
}

/**
 * Vérifie si les données utilisent la nouvelle structure (par catégories)
 */
function isNewStructure(data) {
  if (!data) return false;
  const firstKey = Object.keys(data)[0];
  return Array.isArray(data[firstKey]);
}

/**
 * Charge les données DDCVacuum et les indexe par hash
 */
async function loadDDCVacuum() {
  if (ddcvacuumCache) return ddcvacuumCache;
  try {
    const response = await fetch(DDCVACUUM_URL, { cf: { cacheTtl: 3600 } });
    if (!response.ok) return null;
    const rawData = await response.json();
    ddcvacuumCache = isNewStructure(rawData) ? indexByHash(rawData) : rawData;
    return ddcvacuumCache;
  } catch (e) {
    console.error(`Erreur chargement DDCVacuum:`, e);
    return null;
  }
}

/**
 * Vérifie si un item a des données DDCVacuum
 */
async function hasDDCVacuum(id) {
  const ddcvacuum = await loadDDCVacuum();
  if (!ddcvacuum) return false;
  return ddcvacuum[String(id)] !== undefined;
}

/**
 * Récupère les infos d'un item standard
 */
async function getItemInfo(id, lang, filename) {
  const data = await loadData(lang, filename);
  if (!data || !data[id]) return null;

  const item = data[id];
  const props = item.displayProperties;
  if (!props) return null;

  return {
    name: props.name || 'Inconnu',
    description: props.description || '',
    icon: props.icon ? `${BUNGIE_BASE_URL}${props.icon}` : null
  };
}

/**
 * Récupère les infos d'un perk de set d'armure
 */
async function getSetArmorPerkInfo(id, lang) {
  const data = await loadData(lang, 'setarmor_definitions_enriched.json');
  if (!data) return null;

  for (const [setId, setData] of Object.entries(data)) {
    if (!setData.setPerks) continue;
    const perk = setData.setPerks.find(p => String(p.sandboxPerkHash) === String(id));
    if (perk && perk.displayProperties) {
      return {
        name: perk.displayProperties.name || 'Inconnu',
        description: perk.displayProperties.description || '',
        icon: perk.displayProperties.icon
          ? `${BUNGIE_BASE_URL}${perk.displayProperties.icon}`
          : null,
        requiredCount: perk.requiredSetCount || null
      };
    }
  }
  return null;
}

/**
 * Récupère les infos d'un perk d'artefact
 */
async function getArtefactPerkInfo(id, lang) {
  const data = await loadData(lang, 'artefact_definitions_enriched.json');
  if (!data) return null;

  for (const [artifactId, artifact] of Object.entries(data)) {
    if (!artifact.tiers) continue;
    for (const tier of artifact.tiers) {
      if (!tier.items) continue;
      const item = tier.items.find(i =>
        String(i.perkHash) === String(id) ||
        String(i.itemHash) === String(id)
      );
      if (item && item.name) {
        return {
          name: item.name,
          description: item.description || '',
          icon: item.icon ? `${BUNGIE_BASE_URL}${item.icon}` : null,
          tierIndex: artifact.tiers.indexOf(tier)
        };
      }
    }
  }
  return null;
}

/**
 * Nettoie la description en retirant le texte entre crochets [xxx]
 * et en remplaçant les variables {var:xxx} par une valeur par défaut
 */
function cleanDescription(text) {
  if (!text) return '';
  return text
    // Retirer les textes entre crochets [xxx] (valeurs PVP, etc.)
    .replace(/\[[^\]]*\]/g, '')
    // Remplacer les variables {var:xxx} par 25 (valeur par défaut)
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '25')
    // Nettoyer les espaces multiples
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Échappe les caractères HTML
 */
function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Génère le titre selon le type de page et la langue
 */
function generateTitle(info, pageLabel, pageType, lang) {
  if (pageType === 'setarmor' && info.requiredCount) {
    const prefix = lang === 'en' ? `Armor Set ${info.requiredCount}x` : `Set d'armure ${info.requiredCount}x`;
    return `${prefix} - ${info.name}`;
  }
  if (pageType === 'artefact' && info.tierIndex !== undefined) {
    const prefix = lang === 'en'
      ? `Seasonal Artifact - column ${info.tierIndex + 1}`
      : `Artefact saisonnier - colonne ${info.tierIndex + 1}`;
    return `${prefix} - ${info.name}`;
  }
  return `${pageLabel} - ${info.name}`;
}

/**
 * Génère le HTML avec métadonnées pour Discord (embed spécifique à un item)
 */
function generateDiscordEmbed(info, pageLabel, pageUrl, pageType, showDDCVacuumFooter, lang) {
  const title = generateTitle(info, pageLabel, pageType, lang);
  const description = cleanDescription(info.description);

  let fullDescription = description;
  if (showDDCVacuumFooter) {
    const footer = lang === 'en'
      ? 'Click for Destiny Data Compendium details.'
      : 'Cliquez pour obtenir les détails de Destiny Data Compendium.';
    fullDescription = description ? `${description}\n\n${footer}` : footer;
  }

  return generateHtmlResponse(title, fullDescription, info.icon, pageUrl);
}

/**
 * Génère le fallback générique pour une page sans ID
 */
function generateFallbackEmbed(pageName, pageUrl, lang) {
  const fallback = PAGE_FALLBACK[pageName] || PAGE_FALLBACK['index'];

  const title = lang === 'en' ? (fallback.titleEn || fallback.title) : fallback.title;
  const description = lang === 'en' ? (fallback.descriptionEn || fallback.description) : fallback.description;
  const icon = fallback.icon;

  return generateHtmlResponse(title, description, icon, pageUrl);
}

/**
 * Génère la réponse HTML commune
 */
function generateHtmlResponse(title, description, icon, pageUrl) {
  const iconMeta = icon ? `<meta property="og:image" content="${icon}">` : '';

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">

  <!-- Discord Embed -->
  <meta property="og:site_name" content="D2Glossary.fr - Glossaire des termes de Destiny 2">
  <meta property="og:title" content="${escapeHtml(title)}">
  <meta property="og:description" content="${escapeHtml(description)}">
  ${iconMeta}
  <meta property="og:url" content="${pageUrl}">
  <meta property="og:type" content="website">

  <!-- Couleur Discord (jaune D2Glossary) -->
  <meta name="theme-color" content="#F3CF55">

  <!-- Redirection immédiate pour les vrais utilisateurs -->
  <meta http-equiv="refresh" content="0;url=${pageUrl}">
</head>
<body>
  <p>Redirection vers <a href="${pageUrl}">D2Glossary</a>...</p>
</body>
</html>`;
}

/**
 * Construit l'URL canonique avec les paramètres ordonnés (id > lang)
 */
function buildCanonicalUrl(url, lang) {
  const original = new URL(url);
  const canonical = new URL(original.origin + original.pathname);

  // Ordre défini : id en premier, puis autres params, puis lang
  const id = original.searchParams.get('id');
  const selection = original.searchParams.get('selection');

  // 1. Ajouter l'ID si présent
  if (id) {
    canonical.searchParams.set('id', id);
  }

  // 2. Ajouter selection si présent (pour artefact)
  if (selection) {
    canonical.searchParams.set('selection', selection);
  }

  // 3. Ajouter lang en dernier si ce n'est pas la langue par défaut
  if (lang !== DEFAULT_LANGUAGE) {
    canonical.searchParams.set('lang', lang);
  }

  return canonical.toString();
}

/**
 * Handler principal
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const userAgent = request.headers.get('User-Agent') || '';

    // Si ce n'est pas Discord, laisser passer
    if (!isDiscordBot(userAgent)) {
      return fetch(request);
    }

    // Extraire et valider la langue
    const langParam = url.searchParams.get('lang');
    const lang = getValidLanguage(langParam);

    // Extraire la page
    const pageMatch = url.pathname.match(/\/([a-z]+)\.html$/);
    const pageName = pageMatch ? pageMatch[1] : 'index';

    // Vérifier si c'est la page d'index
    if (pageName === 'index' || url.pathname === '/' || url.pathname === '') {
      const canonicalUrl = buildCanonicalUrl(url, lang);
      const html = generateFallbackEmbed('index', canonicalUrl, lang);
      return new Response(html, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8',
          'Cache-Control': 'public, max-age=3600'
        }
      });
    }

    const config = PAGE_CONFIG[pageName];

    // Si page non configurée, utiliser le fallback générique
    if (!config) {
      const canonicalUrl = buildCanonicalUrl(url, lang);
      const html = generateFallbackEmbed('index', canonicalUrl, lang);
      return new Response(html, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8',
          'Cache-Control': 'public, max-age=3600'
        }
      });
    }

    // Récupérer l'ID
    const id = url.searchParams.get('id');

    // Si pas d'ID, utiliser le fallback de la page
    if (!id) {
      const canonicalUrl = buildCanonicalUrl(url, lang);
      const html = generateFallbackEmbed(pageName, canonicalUrl, lang);
      return new Response(html, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8',
          'Cache-Control': 'public, max-age=3600'
        }
      });
    }

    // Récupérer les infos selon le type de page
    let itemInfo = null;
    if (config.type === 'setarmor') {
      itemInfo = await getSetArmorPerkInfo(id, lang);
    } else if (config.type === 'artefact') {
      itemInfo = await getArtefactPerkInfo(id, lang);
    } else {
      itemInfo = await getItemInfo(id, lang, config.file);
    }

    // Si item non trouvé, utiliser le fallback
    if (!itemInfo) {
      const canonicalUrl = buildCanonicalUrl(url, lang);
      const html = generateFallbackEmbed(pageName, canonicalUrl, lang);
      return new Response(html, {
        headers: {
          'Content-Type': 'text/html;charset=UTF-8',
          'Cache-Control': 'public, max-age=3600'
        }
      });
    }

    // Vérifier si l'item a des données DDCVacuum
    const showDDCVacuumFooter = await hasDDCVacuum(id);

    // Construire l'URL canonique
    const canonicalUrl = buildCanonicalUrl(url, lang);

    // Récupérer le label localisé
    const pageLabel = getLocalizedLabel(config, lang);

    // Générer l'embed Discord
    const html = generateDiscordEmbed(itemInfo, pageLabel, canonicalUrl, config.type, showDDCVacuumFooter, lang);

    return new Response(html, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8',
        'Cache-Control': 'public, max-age=3600'
      }
    });
  }
};