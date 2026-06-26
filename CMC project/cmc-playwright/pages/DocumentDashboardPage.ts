import { Page, Locator } from '@playwright/test';

export class DocumentDashboardPage {
  readonly page: Page;

  // Header
  readonly pageHeader: Locator;

  // Navigation tabs
  readonly studyFinderTab:          Locator;
  readonly dataCentricDashboardTab: Locator;

  // Table filter buttons (Composition / Control / Stability)
  readonly stabilityFilterBtn:   Locator;
  readonly compositionFilterBtn: Locator;
  readonly controlFilterBtn:     Locator;

  // Table grid instruction
  readonly tableGridHeading: Locator;

  // Stability table rows
  readonly fdaElementsRow:          Locator;
  readonly p81BatchSummaryRow:      Locator;
  readonly p81ProtocolSummaryRow:   Locator;
  readonly p83StabilityResultsRow:  Locator;
  readonly s71BatchSummaryRow:      Locator;
  readonly s71ProtocolSummaryRow:   Locator;
  readonly s73StabilityResultsRow:  Locator;

  // Bottom bar
  readonly lastRefreshTimestamp: Locator;

  constructor(page: Page) {
    this.page = page;
    const report = page.getByRole('region', { name: 'Power BI Report' });

    this.pageHeader              = report.locator('text=Select a table to access the Document Dashboard');
    this.studyFinderTab          = report.getByText('Study Finder', { exact: true });
    this.dataCentricDashboardTab = report.locator('text=Data Centric Dashboard');

    this.stabilityFilterBtn      = report.getByRole('button', { name: 'Stability', exact: true });
    this.compositionFilterBtn    = report.getByRole('button', { name: 'Composition', exact: true });
    this.controlFilterBtn        = report.getByRole('button', { name: 'Control', exact: true });

    this.tableGridHeading        = report.locator('text=Click on the table link below to navigate to it');

    this.fdaElementsRow          = report.locator('text=FDA Elements');
    this.p81BatchSummaryRow      = report.locator('text=P.8.1 Stability Batch Summary for Drug Product');
    this.p81ProtocolSummaryRow   = report.locator('text=P.8.1 Stability Protocol Summary for Drug Product');
    this.p83StabilityResultsRow  = report.locator('text=P.8.3 Stability Results for Drug Product');
    this.s71BatchSummaryRow      = report.locator('text=S.7.1 Stability Batch Summary for Drug Substance');
    this.s71ProtocolSummaryRow   = report.locator('text=S.7.1 Stability Protocol Summary for Drug Substance');
    this.s73StabilityResultsRow  = report.locator('text=S.7.3 Stability Results for Drug Substance');

    this.lastRefreshTimestamp    = page.locator('text=Last Data Refresh Timestamp');
  }

  async goto(url: string) {
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });
    await this.page.waitForTimeout(3000); // allow Power BI report iframe to begin rendering
  }

  async waitForPage() {
    await this.stabilityFilterBtn.waitFor({ state: 'visible', timeout: 30000 });
  }
}
