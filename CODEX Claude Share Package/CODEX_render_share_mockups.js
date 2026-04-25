const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const files = [
  'C:/CODEX PG/CODEX Visual Mockups/CODEX_testing_audit_dashboard_v1.html',
  'C:/CODEX PG/CODEX Visual Mockups/CODEX_tester_capture_panel_v1.html',
  'C:/CODEX PG/CODEX Visual Mockups/CODEX_region_review_dialog_v1.html',
  'C:/CODEX PG/CODEX Interface Storyboards/CODEX_step_by_step_ui_storyboard_v1.html'
];
const outDir = 'C:/CODEX PG/CODEX Claude Share Package/CODEX Full Size Mockup Images/CODEX Audit Testing';

function slugify(name) {
  return name.replace(/\.html$/i, '').replace(/[^a-z0-9]+/gi, '_').replace(/^_+|_+$/g, '').toLowerCase();
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 980 }, deviceScaleFactor: 1 });
  const results = [];

  for (const file of files) {
    const outName = `${slugify(path.basename(file))}.png`;
    const outPath = path.join(outDir, outName);
    const url = 'file:///' + file.replaceAll('\\', '/').replaceAll(' ', '%20');
    let title = '';
    let size = null;
    let error = null;
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
      await page.screenshot({ path: outPath, fullPage: true });
      title = await page.title();
      size = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight }));
    } catch (err) {
      error = String(err && err.message || err);
    }
    results.push({ file, screenshot: outPath, title, size, error });
    console.log(`${error ? 'ERR' : 'OK '} ${file} -> ${outName}`);
  }
  await browser.close();
  fs.writeFileSync(path.join(outDir, 'CODEX_audit_testing_render_manifest.json'), JSON.stringify(results, null, 2));
})();
