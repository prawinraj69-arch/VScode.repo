import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';

// Load environment based on ENV variable (default: sit)
const env = process.env.ENV || 'sit';
dotenv.config({ path: `.env.${env}` });

export default defineConfig({
  testDir: './tests',
  timeout: 240_000,
  retries: 1,
  reporter: [
    ['html', { outputFolder: `reports/${env}`, open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL,
    headless: false,
    viewport: { width: 1400, height: 900 },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
    actionTimeout: 15_000,
    // Reuse authenticated session captured by: npm run auth:sit / auth:ppt
    storageState: `auth/${env}.json`,
  },
  projects: [
    {
      name: 'SIT',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/*.spec.ts',
    },
    {
      name: 'PPT',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/*.spec.ts',
    },
  ],
});
