import { Page, Locator } from '@playwright/test';

export class StabilityDashboardPage {
  readonly page: Page;

  // Toolbar
  readonly reportTitle:      Locator;
  readonly dataUpdatedLabel: Locator;
  readonly fileBtn:          Locator;
  readonly exportBtn:        Locator;
  readonly shareBtn:         Locator;
  readonly editBtn:          Locator;
  readonly refreshBtn:       Locator;
  readonly resetBtn:         Locator;
  readonly bookmarksBtn:     Locator;
  readonly viewBtn:          Locator;
  readonly favoriteToggle:   Locator;

  // Disclaimer
  readonly acceptBtn: Locator;

  // Home page content
  readonly welcomeHeading:            Locator;
  readonly findHeading:               Locator;
  readonly viewHeading:               Locator;
  readonly createHeading:             Locator;
  readonly stabilityStudyFinderLink:  Locator;
  readonly batchFinderLink:           Locator;
  readonly stabilityDataCentricLink:  Locator;
  readonly impuritiesDashboardsLink:  Locator;
  readonly documentDashboardLink:     Locator;
  readonly assistedAuthoringToolLink: Locator;

  // Bottom bar
  readonly pageTab:              Locator;
  readonly lastRefreshTimestamp: Locator;

  constructor(page: Page) {
    this.page = page;
    const report = page.getByRole('region', { name: 'Power BI Report' });

    // Toolbar
    this.reportTitle      = page.getByRole('button', { name: /CMC Stability Data Hub/ });
    this.dataUpdatedLabel = page.locator('text=/Data updated/');
    this.fileBtn          = page.getByRole('button', { name: 'File' });
    this.exportBtn        = page.getByRole('button', { name: 'Export' });
    this.shareBtn         = page.getByRole('button', { name: 'Share' });
    this.editBtn          = page.getByRole('button', { name: 'Edit' });
    this.refreshBtn       = page.getByRole('button', { name: /Refresh visuals/ });
    this.resetBtn         = page.getByRole('button', { name: /Reset filters/ });
    this.bookmarksBtn     = page.getByRole('button', { name: 'Bookmarks' });
    this.viewBtn          = page.getByRole('button', { name: 'View' });
    this.favoriteToggle   = page.getByRole('checkbox', { name: 'Toggle Favorite' });

    // Disclaimer Accept button
    this.acceptBtn = page.locator('text=Accept').first();

    // Home content
    this.welcomeHeading            = report.locator('text=Welcome to the CMC Data Hub');
    this.findHeading               = report.locator('text=Find');
    this.viewHeading               = report.locator('text=View');
    this.createHeading             = report.locator('text=Create');
    this.stabilityStudyFinderLink  = report.locator('text=Stability Study Finder');
    this.batchFinderLink           = report.locator('text=Batch Finder');
    this.stabilityDataCentricLink  = report.locator('text=Stability Data-Centric Dashboard');
    this.impuritiesDashboardsLink  = report.locator('text=Impurities Dashboards');
    this.documentDashboardLink     = report.locator('text=Document Dashboard');
    this.assistedAuthoringToolLink = report.locator('text=Assisted Authoring Tool');

    // Bottom bar
    this.pageTab              = page.locator('text=CMC Data Hub Home');
    this.lastRefreshTimestamp = page.locator('text=Last Data Refresh Timestamp');
  }

  async goto(url: string) {
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });
  }

  /** Accept the disclaimer popup if it appears (first visit only) */
  async acceptDisclaimerIfPresent() {
    try {
      await this.acceptBtn.waitFor({ state: 'visible', timeout: 5000 });
      await this.acceptBtn.click();
      await this.page.waitForLoadState('domcontentloaded');
    } catch {
      // No disclaimer present — continue
    }
  }

  async waitForHomePage() {
    await this.welcomeHeading.waitFor({ state: 'visible', timeout: 20000 });
  }
}
