import { test, expect } from '@playwright/test';
import { StabilityDashboardPage } from '../pages/StabilityDashboardPage';
import { ENV } from '../utils/env';

test.describe(`CMC Stability Data Hub Home — ${ENV.workspaceName}`, () => {
  let dash: StabilityDashboardPage;

  test.beforeEach(async ({ page }) => {
    dash = new StabilityDashboardPage(page);
    await dash.goto(ENV.stabilityDisclaimerUrl);
    await dash.acceptDisclaimerIfPresent();
    await dash.waitForHomePage();
  });

  // ── Toolbar ────────────────────────────────────────────────────
  test('TC-SD-01 — Report title shows CMC Stability Data Hub', async () => {
    await expect(dash.reportTitle).toContainText('CMC Stability Data Hub');
  });

  test('TC-SD-02 — Data updated label is visible in toolbar', async () => {
    await expect(dash.dataUpdatedLabel).toBeVisible();
  });

  test('TC-SD-03 — File button is visible in toolbar', async () => {
    await expect(dash.fileBtn).toBeVisible();
  });

  test('TC-SD-04 — Export button is visible in toolbar', async () => {
    await expect(dash.exportBtn).toBeVisible();
  });

  test('TC-SD-05 — Share button is visible in toolbar', async () => {
    await expect(dash.shareBtn).toBeVisible();
  });

  test('TC-SD-06 — Edit button is visible in toolbar', async () => {
    await expect(dash.editBtn).toBeVisible();
  });

  test('TC-SD-07 — Reset filters button is visible', async () => {
    await expect(dash.resetBtn).toBeVisible();
  });

  test('TC-SD-08 — Bookmarks button is visible', async () => {
    await expect(dash.bookmarksBtn).toBeVisible();
  });

  test('TC-SD-09 — View button is visible', async () => {
    await expect(dash.viewBtn).toBeVisible();
  });

  test('TC-SD-10 — Refresh visuals button is visible', async () => {
    await expect(dash.refreshBtn).toBeVisible();
  });

  test('TC-SD-11 — Toggle Favourite checkbox is visible', async () => {
    await expect(dash.favoriteToggle).toBeVisible();
  });

  // ── Home page content ──────────────────────────────────────────
  test('TC-SD-12 — Welcome heading is displayed on Home page', async () => {
    await expect(dash.welcomeHeading).toBeVisible();
  });

  test('TC-SD-13 — Page tab shows "CMC Data Hub Home"', async () => {
    await expect(dash.pageTab).toBeVisible();
  });

  test('TC-SD-14 — Last Data Refresh Timestamp is visible', async () => {
    await expect(dash.lastRefreshTimestamp).toBeVisible();
  });

  // ── Find column ────────────────────────────────────────────────
  test('TC-SD-15 — "Find" section heading is visible', async () => {
    await expect(dash.findHeading).toBeVisible();
  });

  test('TC-SD-16 — Stability Study Finder link is visible', async () => {
    await expect(dash.stabilityStudyFinderLink).toBeVisible();
  });

  test('TC-SD-17 — Batch Finder link is visible', async () => {
    await expect(dash.batchFinderLink).toBeVisible();
  });

  test('TC-SD-18 — Stability Data-Centric Dashboard link is visible', async () => {
    await expect(dash.stabilityDataCentricLink).toBeVisible();
  });

  // ── View column ────────────────────────────────────────────────
  test('TC-SD-19 — "View" section heading is visible', async () => {
    await expect(dash.viewHeading).toBeVisible();
  });

  test('TC-SD-20 — Impurities Dashboards link is visible', async () => {
    await expect(dash.impuritiesDashboardsLink).toBeVisible();
  });

  test('TC-SD-21 — Document Dashboard link is visible', async () => {
    await expect(dash.documentDashboardLink).toBeVisible();
  });

  // ── Create column ──────────────────────────────────────────────
  test('TC-SD-22 — "Create" section heading is visible', async () => {
    await expect(dash.createHeading).toBeVisible();
  });

  test('TC-SD-23 — Assisted Authoring Tool link is visible', async () => {
    await expect(dash.assistedAuthoringToolLink).toBeVisible();
  });
});
