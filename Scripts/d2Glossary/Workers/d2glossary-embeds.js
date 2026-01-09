/**
 * Cloudflare Worker pour D2Glossary - Embeds Discord
 */

// Configuration
const SITE_URL = 'https://d2glossary.fr';
const BUNGIE_BASE_URL = 'https://www.bungie.net';
const DATA_BASE_URL = 'https://d2glossary.fr/data';
const CLARITY_URL = 'https://d2glossary.fr/data/clarity.json';

// User agent Discord
const DISCORD_BOT = 'discordbot';

// Mapping des pages
const PAGE_CONFIG = {
  'perk': { file: 'item_definitions.json', label: 'Perk' },
  'trait': { file: 'trait_definitions.json', label: 'Trait' },
  'breaker': { file: 'breaker_definitions.json', label: 'Champion' },
  'damagetype': { file: 'damagetype_definitions.json', label: 'Dégât' },
  'modifier': { file: 'modifier_definitions.json', label: 'Modificateur' },
  'setarmor': { file: 'setarmor_definitions_enriched.json', label: 'Set d\'armure', type: 'setarmor' },
  'artefact': { file: 'artefact_definitions_enriched.json', label: 'Artefact', type: 'artefact' }
};

// Cache pour Clarity
let clarityCache = null;

/**
 * Vérifie si c'est le bot Discord
 */
function isDiscordBot(userAgent) {
  if (!userAgent) return false;
  return userAgent.toLowerCase().includes(DISCORD_BOT);
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
 * Charge les données Clarity
 */
async function loadClarity() {
  if (clarityCache) return clarityCache;

  try {
    const response = await fetch(CLARITY_URL, { cf: { cacheTtl: 3600 } });
    if (!response.ok) return null;
    clarityCache = await response.json();
    return clarityCache;
  } catch (e) {
    console.error(`Erreur chargement Clarity:`, e);
    return null;
  }
}

/**
 * Vérifie si un item a des données Clarity
 */
async function hasClarity(id) {
  const clarity = await loadClarity();
  if (!clarity) return false;
  return clarity[id] !== undefined;
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

  // Parcourir l'artefact et ses tiers
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
 * Nettoie la description
 */
function cleanDescription(text) {
  if (!text) return '';
  return text
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '')
    .replace(/\[([^\]]+)\]/g, '$1')
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
 * Génère le titre selon le type de page
 */
function generateTitle(info, pageLabel, pageType) {
  if (pageType === 'setarmor' && info.requiredCount) {
    return `Set d'armure ${info.requiredCount}x - ${info.name}`;
  }
  if (pageType === 'artefact' && info.tierIndex !== undefined) {
    return `Artefact saisonnier - colonne ${info.tierIndex + 1} - ${info.name}`;
  }
  return `${pageLabel} - ${info.name}`;
}

/**
 * Génère le HTML avec métadonnées pour Discord
 */
function generateDiscordEmbed(info, pageLabel, pageUrl, pageType, showClarityFooter) {
  const title = generateTitle(info, pageLabel, pageType);
  const description = cleanDescription(info.description);

  let fullDescription = description;
  if (showClarityFooter) {
    const footer = 'Cliquez pour obtenir les détails de Destiny Data Compendium.';
    fullDescription = description ? `${description}\n\n${footer}` : footer;
  }

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">

  <!-- Discord Embed -->
  <meta property="og:site_name" content="D2Glossary.fr - Glossaire des termes de Destiny 2">
  <meta property="og:title" content="${escapeHtml(title)}">
  <meta property="og:description" content="${escapeHtml(fullDescription)}">
  <meta property="og:image" content="${info.icon}">
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

    // Extraire la page et l'ID
    const id = url.searchParams.get('id');
    if (!id) return fetch(request);

    const pageMatch = url.pathname.match(/\/([a-z]+)\.html$/);
    if (!pageMatch) return fetch(request);

    const pageName = pageMatch[1];
    const config = PAGE_CONFIG[pageName];
    if (!config) return fetch(request);

    // Langue (défaut: fr)
    const lang = url.searchParams.get('lang') || 'fr';

    // Récupérer les infos selon le type de page
    let itemInfo = null;
    if (config.type === 'setarmor') {
      itemInfo = await getSetArmorPerkInfo(id, lang);
    } else if (config.type === 'artefact') {
      itemInfo = await getArtefactPerkInfo(id, lang);
    } else {
      itemInfo = await getItemInfo(id, lang, config.file);
    }

    if (!itemInfo) return fetch(request);

    // Vérifier si l'item a des données Clarity
    const showClarityFooter = await hasClarity(id);

    // Générer l'embed Discord
    const html = generateDiscordEmbed(itemInfo, config.label, url.toString(), config.type, showClarityFooter);

    return new Response(html, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8',
        'Cache-Control': 'public, max-age=3600'
      }
    });
  }
};