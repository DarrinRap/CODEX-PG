const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");
const root = "C:\\CODEX PG\\CODEX Audit UX Fullscreen Walkthrough PG Aligned";
const htmlPath = path.join(root, "CODEX_audit_ux_fullscreen_walkthrough_PG_aligned_v2.html");
const outDir = path.join(root, "CODEX fullscreen frames");
const frames = [["screen-01","01_testing_audit_panel_PG_aligned.png"],["screen-02","02_workflow_capture_PG_aligned.png"],["screen-03","03_region_capture_review_PG_aligned.png"],["screen-04","04_fail_detail_panel_PG_aligned.png"],["screen-05","05_session_package_PG_aligned.png"],["screen-06","06_claude_handoff_PG_aligned.png"],["screen-07","07_end_to_end_flow_map_PG_aligned.png"]];
(async()=>{const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});await page.goto(pathToFileURL(htmlPath).href);await page.evaluate(()=>document.fonts&&document.fonts.ready);for(const [id,name] of frames){const loc=page.locator('#'+id);await loc.scrollIntoViewIfNeeded();await loc.screenshot({path:path.join(outDir,name),animations:'disabled'});console.log(name)}await browser.close();})();