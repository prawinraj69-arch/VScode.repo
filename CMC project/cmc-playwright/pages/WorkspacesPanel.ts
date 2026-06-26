import { Page, Locator, expect } from '@playwright/test';

export class WorkspacesPanel {
  readonly page: Page;

  // Left sidebar nav item
  readonly workspacesNavItem: Locator;

  // Side panel elements
  readonly panelHeading: Locator;
  readonly searchBox: Locator;
  readonly closeButton: Locator;
  readonly expandButton: Locator;
  readonly myWorkspaceBtn: Locator;
  readonly deploymentPipelinesBtn: Locator;
  readonly newWorkspaceBtn: Locator;

  constructor(page: Page) {
    this.page = page;

    this.workspacesNavItem      = page.getByRole('menuitem', { name: 'Workspaces' });
    this.panelHeading           = page.getByRole('heading',  { name: 'Workspaces' });
    this.searchBox              = page.getByRole('textbox',  { name: 'Workspace search' });
    this.closeButton            = page.getByRole('button',   { name: 'Close' });
    this.expandButton           = page.getByRole('button',   { name: 'Expand' });
    this.myWorkspaceBtn         = page.getByRole('button',   { name: 'My workspace' });
    this.deploymentPipelinesBtn = page.getByRole('button',   { name: 'Deployment pipelines' });
    this.newWorkspaceBtn        = page.locator('button').filter({ hasText: 'New workspace' });
  }

  /** Get a workspace button by its exact display name */
  getWorkspaceButton(name: string): Locator {
    return this.page.getByRole('button', { name, exact: true });
  }

  /** Click the Workspaces nav item and wait for panel to open */
  async openPanel() {
    await this.workspacesNavItem.click();
    await expect(this.panelHeading).toBeVisible();
  }

  /** Close the side panel and verify it is gone */
  async closePanel() {
    await this.closeButton.click();
    await expect(this.panelHeading).not.toBeVisible();
  }

  async searchWorkspace(name: string) {
    await this.searchBox.fill(name);
  }
}
