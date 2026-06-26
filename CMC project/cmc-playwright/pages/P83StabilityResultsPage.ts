import { Page, Locator } from '@playwright/test';

/**
 * P.8.3 Stability Results for Drug Product
 * URL: /reports/{stabilityReportId}/{p83StabilityResultsPageId}
 */
export class P83StabilityResultsPage {
  readonly page: Page;

  // Toolbar
  readonly clearAllFiltersBtn: Locator;

  // Table title
  readonly tableTitle: Locator;

  // ── Data Selector Fields (required) ─────────────────────────
  readonly batchDropdown:                Locator;
  readonly protocolDropdown:             Locator;
  readonly containerOrientationDropdown: Locator;
  readonly containerClosureDropdown:     Locator;
  readonly testArticleDropdown:          Locator;

  // ── Only one required ────────────────────────────────────────
  readonly productFamilyDropdown: Locator;
  readonly azdIdDropdown:         Locator;

  // ── Filters (optional) ───────────────────────────────────────
  readonly timepointDropdown:          Locator;
  readonly storageConditionsDropdown:  Locator;
  readonly testNameDropdown:           Locator;
  readonly resultNameDropdown:         Locator;
  readonly testResultComboDropdown:    Locator;

  constructor(page: Page) {
    this.page = page;
    const r = page.getByRole('region', { name: 'Power BI Report' });

    this.clearAllFiltersBtn = r.getByRole('button', { name: /Clear all slicers/ });
    this.tableTitle         = r.getByRole('heading', { name: /P\.8\.3 Stability Results for/ });

    // Required dropdowns
    this.batchDropdown                = r.getByRole('combobox', { name: 'Batch' });
    this.protocolDropdown             = r.getByRole('combobox', { name: 'Protocol' });
    this.containerOrientationDropdown = r.getByRole('combobox', { name: 'Container Orientation' });
    this.containerClosureDropdown     = r.getByRole('combobox', { name: 'Container Closure' });
    this.testArticleDropdown          = r.getByRole('combobox', { name: 'Test Article' });

    // Only one required
    this.productFamilyDropdown = r.getByRole('combobox', { name: 'Product Family Preferred Name' });
    this.azdIdDropdown         = r.getByRole('combobox', { name: 'AZD ID' });

    // Optional filters
    this.timepointDropdown         = r.getByRole('combobox', { name: 'LOWER_TIMEPOINT' });
    this.storageConditionsDropdown = r.getByRole('combobox', { name: 'storage_condition' });
    this.testNameDropdown          = r.getByRole('combobox', { name: 'test_name' });
    this.resultNameDropdown        = r.getByRole('combobox', { name: 'result_name' });
    this.testResultComboDropdown   = r.getByRole('combobox', { name: 'Test Result' });
  }

  async goto(url: string) {
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });
    await this.page.waitForTimeout(3000); // allow Power BI report iframe to begin rendering
  }

  async waitForPage() {
    await this.batchDropdown.waitFor({ state: 'visible', timeout: 30000 });
    try {
      await this.page.locator('text=Visuals are loading...').first().waitFor({ state: 'hidden', timeout: 60000 });
    } catch {
      // Ignore if the loading indicator is not present.
    }
    await this.page.waitForTimeout(3000);
  }

  /**
   * Select a value from a Power BI slicer/combobox.
   *
   * Verified against the live SIT DOM (see docs/SLICER_INTERACTION.md):
   * the search box must receive real per-character key events
   * (`pressSequentially`) — `fill()` sets the value without firing the
   * keystrokes Power BI's filter listens for, so the list never narrows
   * and the click below silently finds nothing. No Escape press is
   * needed or wanted: it triggers Power BI's "Selections cleared" action
   * and wipes out every field selected so far, not just the open popup.
   */
  async selectDropdownValue(dropdown: Locator, value: string) {
    await dropdown.click();
    await this.page.waitForTimeout(600);

    const search = this.page.getByRole('textbox', { name: /search/i }).first();
    await search.waitFor({ state: 'visible', timeout: 4000 });
    await search.pressSequentially(value, { delay: 100 });
    await this.page.waitForTimeout(800);

    const option = this.page.getByRole('option', { name: value }).first();
    await option.waitFor({ state: 'visible', timeout: 4000 });
    await option.click();
    await this.page.waitForTimeout(800);

    // The popup does not close itself after a click — toggle the trigger
    // closed so its option list can't intercept clicks on the next slicer.
    await dropdown.click();
    await this.page.waitForTimeout(600);

    try {
      await this.page.locator('text=Visuals are loading...').first().waitFor({ state: 'hidden', timeout: 60000 });
    } catch {
      // Ignore if the loading indicator is not present.
    }
    await this.page.waitForTimeout(1000);
  }

  /**
   * Get a gridcell by its exact text value.
   */
  getCell(value: string): Locator {
    // The same value can legitimately repeat across multiple timepoint
    // columns in this pivot table — match the first occurrence.
    return this.page.getByRole('gridcell', { name: value, exact: true }).first();
  }
}
