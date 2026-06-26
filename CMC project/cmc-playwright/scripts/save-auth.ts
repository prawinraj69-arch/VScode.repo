/**
 * save-auth.ts
 *
 * Run this ONCE before running tests to capture your authenticated session.
 * It opens a headed browser, navigates to Power BI, and waits for you to
 * log in manually (including MFA/SSO). Once you're on the Power BI home page,
 * press Enter in the terminal and it saves the session to auth/sit.json.
 *
 * Usage:
 *   npx ts-node scripts/save-auth.ts
 *   (or via package.json:  npm run auth:sit)
 *
 * The saved file is used by playwright.config.ts as storageState so all
 * tests skip the login page entirely.
 */

import { chromium } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

// Pick the environment from `--env <name>` (defaults to sit) so the same
// script can capture auth for SIT or PPT into the matching auth/<env>.json.
const envArgIndex = process.argv.indexOf('--env');
const ENV_NAME    = envArgIndex !== -1 ? process.argv[envArgIndex + 1] : 'sit';

const AUTH_DIR  = path.join(__dirname, '..', 'auth');
const AUTH_FILE = path.join(AUTH_DIR, `${ENV_NAME}.json`);

async function main() {
  // Ensure auth/ directory exists
  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page    = await context.newPage();

  console.log('\n──────────────────────────────────────────────');
  console.log(`  Capturing auth for environment: ${ENV_NAME.toUpperCase()}`);
  console.log('  Opening Power BI in a headed browser...');
  console.log('  → Log in with your AZ / Microsoft account');
  console.log('  → Complete MFA if prompted');
  console.log('  → Wait until you see the Power BI home page');
  console.log('  → Then come back here and press ENTER');
  console.log('──────────────────────────────────────────────\n');

  await page.goto('https://app.powerbi.com');

  // Wait for user to finish login
  await waitForEnter();

  // Save storage state (cookies + localStorage)
  await context.storageState({ path: AUTH_FILE });
  console.log(`\n✅  Auth state saved to: ${AUTH_FILE}`);
  console.log('   You can now run: npx playwright test\n');

  await browser.close();
}

function waitForEnter(): Promise<void> {
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
