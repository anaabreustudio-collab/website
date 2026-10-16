import { readFile, writeFile, mkdir, cp, rm, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = async file => readFile(path.join(root, file), 'utf8');
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const site = JSON.parse(await read('content/site.json'));
const projects = JSON.parse(await read('content/projects.json'));
const ids = new Set();
const rows = [];
let row = 0;
let column = 0;
function label(text, url, className = '') {
  if (url && !/^(https?:\/\/|mailto:|\/[^/])/.test(url)) throw new Error('Invalid link: '+url);
  return url ? `<a class="${className}" href="${escape(url)}">${escape(text)}</a>` : `<span class="pending-link ${className}">${escape(text)}</span>`;
}
for (const project of projects) {
  if (!/^[a-z0-9-]+$/.test(project.id) || ids.has(project.id)) throw new Error('Each project needs a unique, lowercase ID.');
  ids.add(project.id);
  let artwork;
  if (project.image) {
    if (!/^\/images\/[a-zA-Z0-9_./-]+$/.test(project.image) || project.image.includes('..')) throw new Error('Use a local /images/ path.');
    await stat(path.join(root, 'public', project.image));
    artwork = `<img class="project-image" src="${escape(project.image)}" alt="" loading="lazy" decoding="async" style="object-position:${escape(project.objectPosition || 'center')}" />`;
  } else {
    if (!/^[a-z0-9-]+\.html$/.test(project.artwork || '')) throw new Error('Missing artwork or image for '+project.id);
    artwork = `<div class="composition">${await read('content/artwork/'+project.artwork)}</div>`;
  }
  if (ids.size <= 5) artwork = artwork.replaceAll('loading="lazy"', 'loading="eager"');
  if (project.desktopRow) { row = project.desktopRow - 1; column = (project.desktopColumn || 1) - 1; }
  rows[row] ||= [];
  const caption = project.caption === false ? '' : `<figcaption class="project-caption">${escape(project.title)}${project.category ? ` <span aria-hidden="true">•</span> ${escape(project.category)}` : ''}${project.note ? `<small class="project-note">${escape(project.note)}</small>` : ''}</figcaption>`;
  rows[row].push(`<figure class="project" data-project="${project.id}" style="--desktop-column:${column+1};--offset-x:${Number(project.desktopOffsetX || 0)}px;--offset-y:${Number(project.desktopOffsetY || 0)}px"><div class="artwork" role="img" aria-label="${escape(project.alt || project.title+(project.category ? ' — '+project.category : ''))}">${artwork}</div>${caption}</figure>`);
  column++;
  // The source intentionally reserves an otherwise empty row for Conversas.
  if (column === 5 || project.desktopRow) { row++; column = 0; }
}
const identity = `<span><span class="identity-name">${escape(site.name)}</span> <span aria-hidden="true">•</span> ${escape(site.desktopDescription)}</span>`;
const output = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Selected graphic design work by Ana Abreu." />
  <title>Ana Abreu — Graphic Design</title>
  <link rel="preload" href="/fonts/SuisseIntlTrial-Book.otf" as="font" type="font/otf" crossorigin />
  <link rel="preload" href="/fonts/SuisseIntlTrial-Bold.otf" as="font" type="font/otf" crossorigin />
  <link rel="stylesheet" href="/styles.css" />
  <script src="/layout.js"></script>
</head>
<body>
  <header class="site-header">
    <p><span class="desktop-identity">${identity}</span><span class="mobile-identity"><span class="identity-name">${escape(site.mobileName)}</span> <span aria-hidden="true">•</span> ${escape(site.mobileDescription)}</span></p>
    ${label('Information',site.informationUrl,'information')}
  </header>
  <main class="gallery" aria-label="Selected projects">${rows.map(items => `<div class="project-row">${items.join('\n')}</div>`).join('\n')}</main>
  <footer class="site-footer">
    <nav aria-label="Information">${label('Information',site.informationUrl,'information')}</nav>
    <p class="footer-identity">${identity}</p>
  </footer>
</body>
</html>`;
await rm(path.join(root,'dist'),{recursive:true,force:true});
await mkdir(path.join(root,'dist'),{recursive:true});
await cp(path.join(root,'public'),path.join(root,'dist'),{recursive:true});
await writeFile(path.join(root,'dist/index.html'),output);
const informationContent = await read('content/information.html');
const social = `<nav class="information-social" aria-label="Contact">${label('Instagram',site.instagramUrl)}${label('LinkedIn',site.linkedinUrl)}${label('X',site.xUrl)}${label('Email',site.email ? 'mailto:'+site.email : '')}</nav>`;
const informationPage = output
  .replace('<title>Ana Abreu — Graphic Design</title>', '<title>Information — Ana Abreu</title>')
  .replace('<body>', '<body class="information-page">')
  .replace(/<main class="gallery"[\s\S]*?<\/main>/, `<main class="information-grid" aria-label="Information">${informationContent}${social}</main>`)
  .replace(/<footer[\s\S]*?<\/footer>/, '')
  .replaceAll('<span class="identity-name">Ana Abreu</span>', '<a class="identity-name home-link" href="/" aria-label="Ana Abreu — home">Ana Abreu</a>')
  .replace('class="information"', 'class="information" aria-current="page"');
await writeFile(path.join(root,'dist/information.html'),informationPage);
console.log(`Built ${projects.length} projects → dist/`);
