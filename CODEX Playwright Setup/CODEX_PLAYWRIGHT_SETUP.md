# CODEX Playwright Setup

Playwright's Node package is available through the bundled Codex runtime, and the Chromium browser binary has been installed locally for this project.

## Installed Browser Location

`C:\CODEX PG\CODEX Playwright Browsers`

This folder is intentionally ignored by git because it contains large downloaded browser binaries.

## Runtime Paths

Node executable:

`C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`

Node packages:

`C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules`

## Required Environment Variables

Before running Playwright scripts from PowerShell:

```powershell
$env:NODE_PATH='C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$env:PLAYWRIGHT_BROWSERS_PATH='C:\CODEX PG\CODEX Playwright Browsers'
```

## Verification Command

```powershell
$env:NODE_PATH='C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$env:PLAYWRIGHT_BROWSERS_PATH='C:\CODEX PG\CODEX Playwright Browsers'
& 'C:\Users\drrap\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' -e "const { chromium } = require('playwright'); (async()=>{ const browser = await chromium.launch({ headless: true }); const page = await browser.newPage(); await page.setContent('<h1>Playwright OK</h1>'); console.log(await page.textContent('h1')); await browser.close(); })();"
```

Expected output:

`Playwright OK`

## Project Use

Use Playwright for:

- rendering local HTML mockups,
- taking screenshots/contact sheets,
- checking responsive layouts,
- testing future web dashboards or HTML specs.

For the Python/PySide desktop app itself, Playwright is not the primary automation tool. It is most useful for HTML-based design artifacts and browser-style interfaces.
