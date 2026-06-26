/**
 * save-auth.js
 * Run once to capture your authenticated Power BI session.
 * Usage:  node scripts/save-auth.js
 */

const { chromium } = require('@playwright/test');
const fs       = require('fs');
const path     = require('path');
const readline = require('readline');

// Pick the environment from `--env <name>` (defaults to sit) so the same
// script can capture auth for SIT or PPT into the matching auth/<env>.json.
const envArgIndex = process.argv.indexOf('--env');
const ENV_NAME    = envArgIndex !== -1 ? process.argv[envArgIndex + 1] : 'sit';

const AUTH_DIR  = path.join(__dirname, '..', 'auth');
const AUTH_FILE = path.join(AUTH_DIR, `${ENV_NAME}.json`);

async function main() {
  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page    = await context.newPage();

  console.log('\n──────────────────────────────────────────────');
  console.log(`  Capturing auth for environment: ${ENV_NAME.toUpperCase()}`);
  console.log('  Opening Power BI in a headed browser...');
  console.log('  1. Log in with your AZ Microsoft account');
  console.log('  2. Complete MFA on your phone');
  console.log('  3. Wait for the Power BI home page to load');
  console.log('  4. Come back here and press ENTER');
  console.log('──────────────────────────────────────────────\n');

  await page.goto('https://app.powerbi.com');

  await waitForEnter();

  await context.storageState({ path: AUTH_FILE });
  console.log(`\n✅  Auth state saved to: ${AUTH_FILE}`);
  console.log(`   You can now run: npm run test:${ENV_NAME}:doc\n`);

  await browser.close();
}

function waitForEnter() {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question('Press ENTER once you are logged in to Power BI... ', () => {
      rl.close();
      resolve();
    });
  });
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
