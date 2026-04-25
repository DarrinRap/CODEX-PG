const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");
const root = "C:\\CODEX PG\\CODEX Audit Module UX Revision v3";
const htmlPath = path.join(root, "CODEX_audit_module_ux_revision_v3.html");
const outDir = path.join(root, "CODEX fullscreen frames");
const frames = [["screen-01","01_dropbox_intake.png"],["screen-02","02_analysis_review.png"],["screen-03","03_finding_detail.png"],["screen-04","04_sender_response_draft.png"],["screen-05","05_claude_code_task_builder.png"],["screen-06","06_verification_archive.png"],["screen-07","07_minimal_powerful_ux_map.png"]];
(async()=>{const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});await page.goto(pathToFileURL(htmlPath).href);await page.evaluate(()=>document.fonts&&document.fonts.ready);for(const [id,name] of frames){const loc=page.locator('#'+id);await loc.scrollIntoViewIfNeeded();await loc.screenshot({path:path.join(outDir,name),animations:'disabled'});console.log(name)}await browser.close();})();