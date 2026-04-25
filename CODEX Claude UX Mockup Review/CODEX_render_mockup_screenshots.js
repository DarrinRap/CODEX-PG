const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const sourceRoots = [
  'C:/panda-gallery/workflows/design',
  'C:/panda-gallery/workflows/design/v4_0'
];
const outDir = 'C:/CODEX PG/CODEX Claude UX Mockup Review/CODEX rendered screenshots';

function slugify(name) {
  return name.replace(/\.html$/i, '').replace(/[^a-z0-9]+/gi, '_').replace(/^_+|_+$/g, '').toLowerCase();
}

function listHtml(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(f => f.toLowerCase().endsWith('.html'))
    .map(f => path.join(dir, f));
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const files = sourceRoots.flatMap(listHtml).sort((a, b) => a.localeCompare(b));
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 980 }, deviceScaleFactor: 1 });
  const results = [];

  for (const file of files) {
    const rel = file.replace('C:\\panda-gallery\\workflows\\design\\', '').replaceAll('\\', '/');
    const outName = `${String(results.length + 1).padStart(2, '0')}_${slugify(rel)}.png`;
    const outPath = path.join(outDir, outName);
    const url = 'file:///' + file.replaceAll('\\', '/').replace(/^C:\//, 'C:/').replaceAll(' ', '%20');
    let title = '';
    let textSample = '';
    let size = null;
    let error = null;
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
      await page.screenshot({ path: outPath, fullPage: true });
      title = await page.title();
      textSample = await page.evaluate(() => document.body ? document.body.innerText.slice(0, 1200) : '');
      size = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight }));
    } catch (err) {
      error = String(err && err.message || err);
    }
    results.push({ file, relative: rel, screenshot: outPath, title, size, error, textSample });
    console.log(`${error ? 'ERR' : 'OK '} ${rel} -> ${outName}`);
  }

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'CODEX_render_manifest.json'), JSON.stringify(results, null, 2));
})();

