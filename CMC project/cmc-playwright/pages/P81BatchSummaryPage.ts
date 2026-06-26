import { Page, Locator } from '@playwright/test';

/**
 * P.8.1 Stability Batch Summary for Drug Product
 * URL: /reports/{stabilityReportId}/{p81BatchSummaryPageId}
 */
export class P81BatchSummaryPage {
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
  readonly timepointDropdown:         Locator;
  readonly storageConditionsDropdown: Locator;
  readonly testNameDropdown:          Locator;
  readonly resultNameDropdown:        Locator;

  // Table row headers
  readonly batchIdHeader:                 Locator;
  readonly batchSizeHeader:               Locator;
  readonly manufacturingDateHeader:       Locator;
  readonly manufacturingSiteNameHeader:   Locator;
  readonly containerFillHeader:           Locator;
  readonly containerTypeHeader:           Locator;
  readonly containerSizeHeader:           Locator;
  readonly closureTypeHeader:             Locator;
  readonly studyStartDateHeader:          Locator;
  readonly processHeader:                 Locator;
  readonly latestReportedTimepointHeader: Locator;
  readonly batchUtilizationHeader:        Locator;
  readonly drugSubstanceLotNumberHeader:  Locator;
  readonly strengthHeader:                Locator;

  // ── TC01 expected table output values ────────────────────────
  readonly batchIdValue:                 Locator;
  readonly manufacturingDateValue:       Locator;
  readonly manufacturingSiteNameValue:   Locator;
  readonly containerFillValue:           Locator;
  readonly containerTypeValue:           Locator;
  readonly studyStartDateValue:          Locator;
  readonly latestReportedTimepointValue: Locator;
  readonly strengthValue:                Locator;

  // See more tables
  readonly seeMoreTablesSection:         Locator;
  readonly p81BatchSummaryTableBtn:      Locator;
  readonly p81ProtocolSummaryTableBtn:   Locator;
  readonly p83StabilityResultsTableBtn:  Locator;
  readonly fdaDataElementsTableBtn:      Locator;

  // Navigation
  readonly backBtn: Locator;

  constructor(page: Page) {
    this.page = page;
    const r = page.getByRole('region', { name: 'Power BI Report' });

    this.clearAllFiltersBtn = r.getByRole('button', { name: /Clear all slicers/ });
    this.tableTitle         = r.getByRole('heading', { name: /P\.8\.1 Stability Batch Summary for/ });

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

    // Row headers
    this.batchIdHeader                 = r.getByRole('rowheader', { name: 'Batch ID' });
    this.batchSizeHeader               = r.getByRole('rowheader', { name: 'Batch Size' });
    this.manufacturingDateHeader       = r.getByRole('rowheader', { name: 'Manufacturing Date' });
    this.manufacturingSiteNameHeader   = r.getByRole('rowheader', { name: 'Manufacturing Site Name' });
    this.containerFillHeader           = r.getByRole('rowheader', { name: 'Container Fill' });
    this.containerTypeHeader           = r.getByRole('rowheader', { name: 'Container Type' });
    this.containerSizeHeader           = r.getByRole('rowheader', { name: 'Container Size' });
    this.closureTypeHeader             = r.getByRole('rowheader', { name: 'Closure Type' });
    this.studyStartDateHeader          = r.getByRole('rowheader', { name: 'Study Start Date' });
    this.processHeader                 = r.getByRole('rowheader', { name: 'Process' });
    this.latestReportedTimepointHeader = r.getByRole('rowheader', { name: 'Latest Reported Timepoint' });
    this.batchUtilizationHeader        = r.getByRole('rowheader', { name: 'Batch Utilization' });
    this.drugSubstanceLotNumberHeader  = r.getByRole('rowheader', { name: 'Drug Substance Lot Number' });
    this.strengthHeader                = r.getByRole('rowheader', { name: 'Strength' });

    // TC01 expected values
    this.batchIdValue                  = r.getByRole('gridcell', { name: 'L028672' });
    this.manufacturingDateValue        = r.getByRole('gridcell', { name: '04 February 2025' });
    this.manufacturingSiteNameValue    = r.getByRole('gridcell', { name: 'AZ Macclesfield' });
    this.containerFillValue            = r.getByRole('gridcell', { name: '10.0000 Tablets' });
    this.containerTypeValue            = r.getByRole('gridcell', { name: '75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant' });
    this.studyStartDateValue           = r.getByRole('gridcell', { name: '08 April 2025' });
    this.latestReportedTimepointValue  = r.getByRole('gridcell', { name: '52 weeks (w)' });
    this.strengthValue                 = r.getByRole('gridcell', { name: '25 MG' });

    // See more tables
    this.seeMoreTablesSection         = r.getByRole('group',  { name: 'See more tables' });
    this.p81BatchSummaryTableBtn      = r.locator('text=P.8.1 Stability Batch Summary for Drug');
    this.p81ProtocolSummaryTableBtn   = r.locator('text=P.8.1 Stability Protocol Summary for Drug');
    this.p83StabilityResultsTableBtn  = r.locator('text=P.8.3 Stability Results for Drug Product');
    this.fdaDataElementsTableBtn      = r.locator('text=FDA Data Elements');

    this.backBtn = r.getByRole('link', { name: /Back.*go back/ });
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
}
