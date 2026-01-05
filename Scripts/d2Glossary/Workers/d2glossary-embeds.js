/**
 * Cloudflare Worker pour D2Glossary - Génération d'embeds dynamiques
 *
 * Ce worker intercepte les requêtes des crawlers (Discord, Twitter, etc.)
 * et injecte les métadonnées Open Graph basées sur l'ID dans l'URL
 */

// Configuration
const SITE_URL = 'https://d2glossary.fr';
const BUNGIE_BASE_URL = 'https://www.bungie.net';
const DATA_BASE_URL = 'https://d2glossary.fr/data';
const DEFAULT_IMAGE = 'https://d2glossary.fr/assets/src/ico/logo-d2glossaire.png';

// Cache pour les données JSON (évite de refetch à chaque requête)
const dataCache = new Map();

// User agents des crawlers qui ont besoin des métadonnées OG
const BOT_USER_AGENTS = [
  'Discordbot',
  'Twitterbot',
  'facebookexternalhit',
  'LinkedInBot',
  'Slackbot',
  'TelegramBot',
  'WhatsApp',
  'Googlebot',
  'bingbot'
];

// Mapping des pages vers leurs fichiers de données
const PAGE_DATA_MAP = {
  'perk': { file: 'item_definitions.json', type: 'item' },
  'trait': { file: 'trait_definitions.json', type: 'item' },
  'breaker': { file: 'breaker_definitions.json', type: 'item' },
  'damagetype': { file: 'damagetype_definitions.json', type: 'item' },
  'modifier': { file: 'modifier_definitions.json', type: 'item' },
  'setarmor': { file: 'setarmor_definitions_enriched.json', type: 'setarmor' },
  'artefact': { file: 'artefact_definitions_enriched.json', type: 'artefact' }
};

/**
 * Détecte si la requête vient d'un bot/crawler
 */
function isBot(userAgent) {
  if (!userAgent) return false;
  return BOT_USER_AGENTS.some(bot =>
    userAgent.toLowerCase().includes(bot.toLowerCase())
  );
}

/**
 * Charge les données JSON avec cache
 */
async function loadData(lang, filename) {
  const cacheKey = `${lang}/${filename}`;

  if (dataCache.has(cacheKey)) {
    return dataCache.get(cacheKey);
  }

  try {
    const url = `${DATA_BASE_URL}/${lang}/${filename}`;
    const response = await fetch(url, {
      cf: { cacheTtl: 3600 } // Cache Cloudflare 1h
    });

    if (!response.ok) return null;

    const data = await response.json();
    dataCache.set(cacheKey, data);
    return data;
  } catch (e) {
    console.error(`Erreur chargement ${cacheKey}:`, e);
    return null;
  }
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
    name: props.name || 'Item inconnu',
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

  // Chercher le perk dans tous les sets
  for (const [setId, setData] of Object.entries(data)) {
    if (!setData.setPerks) continue;

    const perk = setData.setPerks.find(p =>
      String(p.sandboxPerkHash) === String(id)
    );

    if (perk && perk.displayProperties) {
      return {
        name: perk.displayProperties.name || 'Perk inconnu',
        description: perk.displayProperties.description || '',
        icon: perk.displayProperties.icon
          ? `${BUNGIE_BASE_URL}${perk.displayProperties.icon}`
          : null,
        setName: setData.displayProperties?.name || ''
      };
    }
  }

  return null;
}

/**
 * Génère le HTML avec les métadonnées Open Graph
 */
function generateOGHtml(info, pageUrl, pageName) {
  const title = info.name ? `${info.name} - D2Glossary` : 'D2Glossary';
  const description = info.description
    ? truncate(cleanDescription(info.description), 200)
    : 'Glossaire communautaire pour Destiny 2 - Définitions, perks, et plus encore.';

  const footerText = '🎮 Cliquez pour plus d\'informations sur D2Glossary';
  const fullDescription = `${description}\n\n${footerText}`;

  // Image par défaut si pas d'icône
  const image = info.icon || `${SITE_URL}/assets/src/ico/logo-d2glossaire.png`;

  return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Primary Meta Tags -->
  <title>${escapeHtml(title)}</title>
  <meta name="title" content="${escapeHtml(title)}">
  <meta name="description" content="${escapeHtml(fullDescription)}">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="${pageUrl}">
  <meta property="og:title" content="${escapeHtml(title)}">
  <meta property="og:description" content="${escapeHtml(fullDescription)}">
  <meta property="og:image" content="${image}">
  <meta property="og:site_name" content="D2Glossary">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:url" content="${pageUrl}">
  <meta name="twitter:title" content="${escapeHtml(title)}">
  <meta name="twitter:description" content="${escapeHtml(fullDescription)}">
  <meta name="twitter:image" content="${image}">

  <!-- Discord -->
  <meta name="theme-color" content="#F3CF55">

  <!-- Redirect pour les vrais utilisateurs -->
  <meta http-equiv="refresh" content="0;url=${pageUrl}">

  <style>
    body {
      background: #0e0e0e;
      color: #fff;
      font-family: sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .loader {
      text-align: center;
    }
    .loader img {
      width: 100px;
      margin-bottom: 1rem;
    }
    a {
      color: #F3CF55;
    }
  </style>
</head>
<body>
  <div class="loader">
    <img src="${SITE_URL}/assets/src/ico/logo-d2glossaire.png" alt="D2Glossary">
    <p>Redirection vers D2Glossary...</p>
    <p><a href="${pageUrl}">Cliquez ici si vous n'êtes pas redirigé</a></p>
  </div>
</body>
</html>`;
}

/**
 * Nettoie la description (retire les variables, etc.)
 */
function cleanDescription(text) {
  if (!text) return '';
  return text
    .replace(/\{var:[a-zA-Z0-9_]+\}/g, '')
    .replace(/\[([^\]]+)\]/g, '$1') // Retire les crochets des keywords
    .replace(/ ?•/g, ' •')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Tronque le texte à une longueur max
 */
function truncate(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
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
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Handler principal
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const userAgent = request.headers.get('User-Agent') || '';

    // Si ce n'est pas un bot, laisser passer la requête normalement
    if (!isBot(userAgent)) {
      return fetch(request);
    }

    // Extraire la page et l'ID
    const pathname = url.pathname;
    const id = url.searchParams.get('id');

    // Si pas d'ID, laisser passer
    if (!id) {
      return fetch(request);
    }

    // Identifier la page
    const pageMatch = pathname.match(/\/([a-z]+)\.html$/);
    if (!pageMatch) {
      return fetch(request);
    }

    const pageName = pageMatch[1];
    const pageConfig = PAGE_DATA_MAP[pageName];

    if (!pageConfig) {
      return fetch(request);
    }

    // Détecter la langue (par défaut: fr)
    const lang = url.searchParams.get('lang') || 'fr';

    // Récupérer les infos de l'item
    let itemInfo = null;

    if (pageConfig.type === 'setarmor') {
      itemInfo = await getSetArmorPerkInfo(id, lang);
    } else {
      itemInfo = await getItemInfo(id, lang, pageConfig.file);
    }

    // Si item non trouvé, laisser passer
    if (!itemInfo) {
      return fetch(request);
    }

    // Générer le HTML avec les métadonnées OG
    const html = generateOGHtml(itemInfo, url.toString(), pageName);

    return new Response(html, {
      headers: {
        'Content-Type': 'text/html;charset=UTF-8',
        'Cache-Control': 'public, max-age=3600' // Cache 1h
      }
    });
  }
};