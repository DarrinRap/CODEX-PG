const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const packageDir = "C:\\CODEX PG\\CODEX PANDA Agent Hub Final Design Package";
const htmlPath = path.join(packageDir, "CODEX_PAH_UX_MOCKUPS_v1.html");
const outDir = path.join(packageDir, "CODEX mockup screenshots");

const screens = [
  "overview",
  "threads",
  "decisions",
  "dispatch",
  "validation",
  "notifications",
];

async function visiblePrimaryCount(page) {
  return page.evaluate(() => {
    return [...document.querySelectorAll(".gbtn.primary")].filter((el) => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
    }).length;
  });
}

async function textOverflowCount(page) {
  return page.evaluate(() => {
    const offenders = [];
    const selectors = "button, .td, .th, .pill, .badge, .metric .v, .metric .k, .summary-line, .item-title b";
    for (const el of document.querySelectorAll(selectors)) {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      if (r.width === 0 || r.height === 0 || s.display === "none" || s.visibility === "hidden") continue;
      if (el.scrollWidth > el.clientWidth + 1) {
        offenders.push({
          text: el.textContent.trim().slice(0, 80),
          tag: el.tagName.toLowerCase(),
          className: el.className,
          clientWidth: el.clientWidth,
          scrollWidth: el.scrollWidth,
        });
      }
    }
    return offenders;
  });
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const baseUrl = pathToFileURL(htmlPath).href;
  const manifest = [];

  for (const screen of screens) {
    await page.goto(`${baseUrl}#${screen}`, { waitUntil: "load" });
    await page.evaluate((id) => activate(id), screen);
    await page.waitForTimeout(150);
    const screenshotName = `CODEX_PAH_mockup_${screen}_1440x1000.png`;
    const screenshotPath = path.join(outDir, screenshotName);
    await page.screenshot({ path: screenshotPath, fullPage: false });
    manifest.push({
      screen,
      screenshot: screenshotPath,
      primary_buttons_visible: await visiblePrimaryCount(page),
      text_overflows: await textOverflowCount(page),
    });
  }

  await browser.close();

  const manifestPath = path.join(packageDir, "CODEX_PAH_SCREENSHOT_MANIFEST_v1.json");
  fs.writeFileSync(manifestPath, JSON.stringify({
    generated_at: "2026-04-26T20:15:00-07:00",
    html: htmlPath,
    viewport: "1440x1000",
    screenshots: manifest,
  }, null, 2));

  console.log(`Rendered ${manifest.length} screenshots`);
  console.log(manifestPath);
})();
