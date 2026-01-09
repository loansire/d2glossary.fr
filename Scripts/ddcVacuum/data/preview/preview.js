/**
 * DDCVacuum Preview - Lecture de all_data_styled.json
 */

// Convertit le format DDCVacuum linesContent en HTML
function ddcvacuumToHTML(ddcvacuumContent) {
    if (!ddcvacuumContent || !Array.isArray(ddcvacuumContent)) {
        return '';
    }

    const htmlParts = [];

    for (const item of ddcvacuumContent) {
        // Spacer
        if (item.classNames && item.classNames.includes('spacer')) {
            htmlParts.push('<div class="spacer"></div>');
            continue;
        }

        // Ligne avec contenu
        if (item.linesContent) {
            let lineHTML = '';

            for (const segment of item.linesContent) {
                const text = segment.text || '';
                const classes = segment.classNames || [];
                const link = segment.link;

                if (link) {
                    lineHTML += `<a href="${link}" class="link" target="_blank">${text}</a>`;
                } else if (classes.length > 0) {
                    const classStr = classes.join(' ');
                    lineHTML += `<span class="${classStr}">${text}</span>`;
                } else {
                    lineHTML += text;
                }
            }

            htmlParts.push(`<div class="line">${lineHTML}</div>`);
        }
    }

    return htmlParts.join('\n');
}

// Génère le HTML pour un record
function renderRecord(record) {
    const name = record.Name || '';
    const setName = record.SetName || '';
    const pieceRequirement = record.PieceRequirement || '';
    const comment = record.Comment || '';

    // Utilise le format DDCVacuum si disponible
    let descriptionHTML;
    if (record.descriptions && record.descriptions.en) {
        descriptionHTML = ddcvacuumToHTML(record.descriptions.en);
    } else {
        descriptionHTML = record.Description || '';
    }

    // Construction de la métadonnée (SetName + PieceRequirement + Comment)
    let metadataHTML = '';
    const metadataParts = [];

    if (setName && setName !== 'NaN' && setName !== 'null') {
        metadataParts.push(`<span class="metadata-set-name">${setName}</span>`);
    }

    if (pieceRequirement && pieceRequirement !== 'NaN' && pieceRequirement !== 'null') {
        metadataParts.push(`<span class="metadata-piece">${pieceRequirement}</span>`);
    }

    if (comment && comment !== 'NaN' && comment !== 'null') {
        metadataParts.push(`<span class="metadata-comment">${comment}</span>`);
    }

    if (metadataParts.length > 0) {
        metadataHTML = `<div class="perk-metadata">${metadataParts.join(' • ')}</div>`;
    }

    // Construction des informations de hash
    let hashHTML = '';
    const hashParts = [];

    // Hash principal
    if (record.hash !== undefined && record.hash !== null) {
        hashParts.push(`<span class="hash-main">Hash: <code>${record.hash}</code></span>`);
    }

    // Parent Hash
    if (record.parentHash !== undefined && record.parentHash !== null) {
        hashParts.push(`<span class="hash-parent">Parent Hash: <code>${record.parentHash}</code></span>`);
    }

    // Parent Name
    if (record.parentName && record.parentName !== 'NaN' && record.parentName !== 'null') {
        hashParts.push(`<span class="hash-parent-name">Parent: ${record.parentName}</span>`);
    }

    // Warnings (multiple matches ou no match)
    if (record.hash_warning) {
        hashParts.push(`<span class="hash-warning">⚠️ ${record.hash_warning}</span>`);
    }

    if (hashParts.length > 0) {
        hashHTML = `<div class="perk-hash-info">${hashParts.join(' • ')}</div>`;
    }

    // Si pas de nom valide, affiche quand même la div mais sans le titre
    const nameHTML = (name && name !== 'NaN' && name !== 'null')
        ? `<div class="perk-name">${name}</div>`
        : '';

    return `
        <div class="perk">
            ${nameHTML}
            ${metadataHTML}
            ${hashHTML}
            <div class="perk-description">${descriptionHTML || '—'}</div>
        </div>
    `;
}

// Génère le contenu complet
function renderContent(data) {
    const nav = document.getElementById('nav');
    const content = document.getElementById('content');

    // Génère la navigation
    const navLinks = Object.keys(data).map(sheetName =>
        `<a href="#${sheetName}">${sheetName}</a>`
    ).join('\n');
    nav.innerHTML = navLinks;

    // Génère les sections
    let contentHTML = '';
    for (const [sheetName, records] of Object.entries(data)) {
        contentHTML += `
            <h2 id="${sheetName}">
                ${sheetName}
                <span class="count">(${records.length} items)</span>
            </h2>
        `;

        for (const record of records) {
            contentHTML += renderRecord(record);
        }
    }

    content.innerHTML = contentHTML;
}

// Charge le JSON et affiche le contenu
async function loadPreview() {
    try {
        // Le JSON est dans Data/all_data_styled.json
        // La preview est dans Data/preview/index.html
        // Donc chemin relatif : ../all_data_styled.json
        const response = await fetch('../all_data_styled.json');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        renderContent(data);

        console.log('✓ Preview chargée avec succès');
        console.log('✓ JSON lu depuis : Data/all_data_styled.json');
    } catch (error) {
        console.error('Erreur lors du chargement du JSON:', error);
        document.getElementById('content').innerHTML = `
            <div style="color: #ff6b6b; padding: 20px; background: #2d1f1f; border-radius: 8px;">
                <h3>❌ Erreur de chargement</h3>
                <p>Impossible de charger ../all_data_styled.json</p>
                <p><code>${error.message}</code></p>
                <p style="margin-top: 10px; font-size: 0.9em;">
                    Vérifiez que Data/all_data_styled.json existe
                </p>
            </div>
        `;
    }
}

// Charge au chargement de la page
document.addEventListener('DOMContentLoaded', loadPreview);