const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");
const root = "C:\\CODEX PG\\CODEX Audit UX Fullscreen Walkthrough";
const htmlPath = path.join(root, "CODEX_audit_ux_fullscreen_walkthrough_v1.html");
const outDir = path.join(root, "CODEX fullscreen frames");
const frames = [
  ["screen-01", "01_audit_control_center.png"],
  ["screen-02", "02_guided_test_capture.png"],
  ["screen-03", "03_region_review_annotation.png"],
  ["screen-04", "04_issue_triage_workspace.png"],
  ["screen-05", "05_session_package_builder.png"],
  ["screen-06", "06_claude_handoff_review.png"],
  ["screen-07", "07_end_to_end_ux_flow_map.png"]
];
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  for (const [id, name] of frames) {
    const locator = page.locator("#" + id);
    await locator.scrollIntoViewIfNeeded();
    await locator.screenshot({ path: path.join(outDir, name), animations: "disabled" });
    console.log(name);
  }
  await browser.close();
})();