import { test, expect } from '@playwright/test';
import { WorkspacesPanel } from '../pages/WorkspacesPanel';
import { ENV } from '../utils/env';

test.describe(`Workspaces Side Panel — ${ENV.workspaceName}`, () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${ENV.baseURL}/home?experience=power-bi`);
    await page.getByRole('menuitem', { name: 'Workspaces' }).waitFor({ state: 'visible' });
  });

  test('TC-WS-01 — Workspaces nav item is visible in sidebar', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await expect(panel.workspacesNavItem).toBeVisible();
  });

  test('TC-WS-02 — Clicking Workspaces opens side panel with correct heading', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.panelHeading).toBeVisible();
    await expect(panel.panelHeading).toHaveText('Workspaces');
  });

  test('TC-WS-03 — Side panel contains Search box', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.searchBox).toBeVisible();
    await expect(panel.searchBox).toHaveAttribute('placeholder', 'Search');
  });

  test('TC-WS-04 — My workspace button is visible', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.myWorkspaceBtn).toBeVisible();
  });

  test('TC-WS-05 — CMC SIT workspace is visible in panel', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.getWorkspaceButton('CMC SIT')).toBeVisible();
  });

  test('TC-WS-06 — CMC PPT workspace is visible in panel', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.getWorkspaceButton('CMC PPT')).toBeVisible();
  });

  test('TC-WS-07 — Expand button is visible', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.expandButton).toBeVisible();
  });

  test('TC-WS-08 — Close button dismisses the panel', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await panel.closePanel();
    await expect(panel.panelHeading).not.toBeVisible();
  });

  test('TC-WS-09 — Deployment pipelines button is visible', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.deploymentPipelinesBtn).toBeVisible();
  });

  test('TC-WS-10 — New workspace button is visible', async ({ page }) => {
    const panel = new WorkspacesPanel(page);
    await panel.openPanel();
    await expect(panel.newWorkspaceBtn).toBeVisible();
  });
});
