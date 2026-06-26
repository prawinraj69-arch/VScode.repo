import { test, expect } from '@playwright/test';
import { DocumentDashboardPage } from '../pages/DocumentDashboardPage';
import { P81BatchSummaryPage } from '../pages/P81BatchSummaryPage';
import { P81ProtocolSummaryPage } from '../pages/P81ProtocolSummaryPage';
import { P83StabilityResultsPage } from '../pages/P83StabilityResultsPage';
import { ENV } from '../utils/env';

// ══════════════════════════════════════════════════════════════════════════════
//  Document Dashboard — table list validations
// ══════════════════════════════════════════════════════════════════════════════
test.describe(`Document Dashboard — ${ENV.workspaceName}`, () => {
  test.beforeEach(async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await docPage.goto(ENV.docDashboardUrl);
    await docPage.waitForPage();
  });

  test('TC-DD-01 — Page header instruction text is visible', async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await expect(docPage.pageHeader).toBeVisible();
  });

  test('TC-DD-02 — Study Finder and Data Centric tabs are visible', async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await expect(docPage.studyFinderTab).toBeVisible();
    await expect(docPage.dataCentricDashboardTab).toBeVisible();
  });

  test('TC-DD-03 — All 3 filter buttons are visible (Composition / Control / Stability)', async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await expect(docPage.compositionFilterBtn).toBeVisible();
    await expect(docPage.controlFilterBtn).toBeVisible();
    await expect(docPage.stabilityFilterBtn).toBeVisible();
  });

  test('TC-DD-04 — Stability filter: all 7 table rows are visible', async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await expect(docPage.fdaElementsRow).toBeVisible();
    await expect(docPage.p81BatchSummaryRow).toBeVisible();
    await expect(docPage.p81ProtocolSummaryRow).toBeVisible();
    await expect(docPage.p83StabilityResultsRow).toBeVisible();
    await expect(docPage.s71BatchSummaryRow).toBeVisible();
    await expect(docPage.s71ProtocolSummaryRow).toBeVisible();
    await expect(docPage.s73StabilityResultsRow).toBeVisible();
  });

  test('TC-DD-05 — Last Data Refresh Timestamp is visible', async ({ page }) => {
    const docPage = new DocumentDashboardPage(page);
    await expect(docPage.lastRefreshTimestamp).toBeVisible();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
//  TC01 — P.8.1 Stab Batch Summary DP
//
//  RULE: Always click "Clear all slicers" BEFORE filling any fields.
//
//  Fields selected:
//    Batch                        → L028672
//    Protocol                     → SS25-0053-001
//    Container Orientation        → unknown physical orientation
//    Container Closure            → 75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant
//    Test Article                 → SS25-0053-TA-004
//    Product Family Preferred Name → AZD3632 besylate
//    AZD ID                       → AZD3632
//    Timepoint / Storage / Test / Result → All (default)
//
//  Expected output:
//    Table title        = P.8.1 Stability Batch Summary for AZD3632 besylate
//    Batch ID           = L028672
//    Manufacturing Date = 04 February 2025
//    Mfg Site Name      = AZ Macclesfield
//    Container Fill     = 10.0000 Tablets
//    Container Type     = 75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant
//    Study Start Date   = 08 April 2025
//    Latest Timepoint   = 52 weeks (w)
//    Strength           = 25 MG
// ══════════════════════════════════════════════════════════════════════════════
test('TC01 — P.8.1 Stab Batch Summary DP', async ({ page }) => {
  const p81 = new P81BatchSummaryPage(page);

  // STEP 1: Navigate to P.8.1 Stability Batch Summary page
  await p81.goto(ENV.p81BatchSummaryUrl);
  await p81.waitForPage();

  // STEP 2: Clear all filters — MANDATORY before every TC
  await p81.clearAllFiltersBtn.click();
  await p81.batchDropdown.waitFor({ state: 'visible', timeout: 15000 }); // wait for PBI to settle after clear
  await page.waitForTimeout(1000);

  // STEP 3: Select AZD ID → AZD3632 first, then continue with the remaining fields
  await p81.selectDropdownValue(p81.azdIdDropdown, 'AZD3632');

  // STEP 4: Select Batch → L028672
  await p81.selectDropdownValue(p81.batchDropdown, 'L028672');

  // STEP 5: Select Protocol → SS25-0053-001
  await p81.selectDropdownValue(p81.protocolDropdown, 'SS25-0053-001');

  // STEP 6: Select Container Orientation → unknown physical orientation
  await p81.selectDropdownValue(p81.containerOrientationDropdown, 'unknown physical orientation');

  // STEP 7: Select Container Closure → 75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant
  await p81.selectDropdownValue(
    p81.containerClosureDropdown,
    '75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant'
  );

  // STEP 8: Select Test Article → SS25-0053-TA-004
  await p81.selectDropdownValue(p81.testArticleDropdown, 'SS25-0053-TA-004');

  // STEP 9: Select Product Family Preferred Name → AZD3632 besylate
  await p81.selectDropdownValue(p81.productFamilyDropdown, 'AZD3632 besylate');

  // STEP 10: Leave all optional filters as default (All)
  // Timepoint → Multiple selections (default)
  // Storage Conditions → All (default)
  // Test Name → All (default)
  // Result Name → All (default)

  // STEP 11: Wait for table to render
  await p81.tableTitle.waitFor({ state: 'visible', timeout: 15000 });

  // ── EXPECTED RESULTS ────────────────────────────────────────────
  await expect(p81.tableTitle).toContainText('P.8.1 Stability Batch Summary for AZD3632 besylate');
  await expect(p81.batchIdValue).toHaveText('L028672');
  await expect(p81.manufacturingDateValue).toHaveText('04 February 2025');
  await expect(p81.manufacturingSiteNameValue).toHaveText('AZ Macclesfield');
  await expect(p81.containerFillValue).toHaveText('10.0000 Tablets');
  await expect(p81.containerTypeValue).toHaveText(
    '75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant'
  );
  await expect(p81.studyStartDateValue).toHaveText('08 April 2025');
  await expect(p81.latestReportedTimepointValue).toHaveText('52 weeks (w)');
  await expect(p81.strengthValue).toHaveText('25 MG');
});

// ══════════════════════════════════════════════════════════════════════════════
//  TC02 — P.8.1 Stab Protocol Summary DP
//
//  RULE: Always click "Clear all slicers" BEFORE filling any fields.
//
//  Fields selected:
//    Batch                        → MS-113838
//    Protocol                     → ST-AZD-0786-DS-DSP078620-002
//    Container Orientation        → (Blank) — default
//    Container Closure            → (Blank) — default
//    Test Article                 → (Blank) — default
//    Product Family Preferred Name → AZD0786
//    AZD ID                       → AZD0786
//    Timepoint (optional)         → initial
//    Storage Conditions (optional) → temperature -80 (+/-) 10°C
//    Test Name                    → All (default)
//
//  Expected output:
//    Table title    = P.8.1 Stability Protocol Summary for AZD0786
//    Column header  = Conditions | Intervals (months) | temperature -80 (+/-) 10°C
//    All condition rows → "initial"
//      Appearance
//      Appearance Analysis
//      Cytotoxicity potency assay
//      CZE Charge Analysis
//      Drug to Antibody Ratio
//      Free Drug
//      High Performance Size Exclusion Chromatography - Purity
//      Identification of product
//      Non-reduced Capillary Gel Electrophoresis Analysis
//      pH
//      Total protein
// ══════════════════════════════════════════════════════════════════════════════
test('TC02 — P.8.1 Stab Protocol Summary DP', async ({ page }) => {
  const p81Proto = new P81ProtocolSummaryPage(page);

  // STEP 1: Navigate to P.8.1 Stability Protocol Summary page
  await p81Proto.goto(ENV.p81ProtocolSummaryUrl);
  await p81Proto.waitForPage();

  // STEP 2: Clear all filters — MANDATORY before every TC
  await p81Proto.clearAllFiltersBtn.click();
  await p81Proto.batchDropdown.waitFor({ state: 'visible', timeout: 15000 }); // wait for PBI to settle after clear
  await page.waitForTimeout(1000);

  // STEP 3: Select AZD ID → AZD0786 first, then continue with the remaining fields
  await p81Proto.selectDropdownValue(p81Proto.azdIdDropdown, 'AZD0786');

  // STEP 4: Select Batch → MS-113838
  await p81Proto.selectDropdownValue(p81Proto.batchDropdown, 'MS-113838');

  // STEP 5: Select Protocol → ST-AZD-0786-DS-DSP078620-002
  await p81Proto.selectDropdownValue(p81Proto.protocolDropdown, 'ST-AZD-0786-DS-DSP078620-002');

  // STEP 6: Container Orientation → (Blank) — leave default
  // STEP 7: Container Closure → (Blank) — leave default
  // STEP 8: Test Article → (Blank) — leave default

  // STEP 9: Select Product Family Preferred Name → AZD0786
  await p81Proto.selectDropdownValue(p81Proto.productFamilyDropdown, 'AZD0786');

  // STEP 10: Select Timepoint (optional) → initial
  await p81Proto.selectDropdownValue(p81Proto.timepointDropdown, 'initial');

  // STEP 11: Select Storage Conditions (optional) → temperature -80 (+/-) 10°C
  await p81Proto.selectDropdownValue(p81Proto.storageConditionsDropdown, 'temperature -80 (+/-) 10°C');

  // STEP 12: Leave Test Name as default → All

  // STEP 13: Wait for table to render
  await p81Proto.tableTitle.waitFor({ state: 'visible', timeout: 15000 });

  // ── EXPECTED RESULTS — Table title & column headers ─────────────
  await expect(p81Proto.tableTitle).toContainText('P.8.1 Stability Protocol Summary for AZD0786');
  await expect(p81Proto.conditionsColumnHeader).toBeVisible();
  await expect(p81Proto.intervalsHeader).toContainText('Intervals (months)');
  await expect(p81Proto.storageConditionColumnHeader).toContainText('temperature -80 (+/-) 10°C');

  // ── EXPECTED RESULTS — All condition rows show "initial" ─────────
  await expect(p81Proto.getConditionRow('Appearance')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Appearance Analysis')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Cytotoxicity potency assay')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('CZE Charge Analysis')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Drug to Antibody Ratio')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Free Drug')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('High Performance Size Exclusion Chromatography - Purity')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Identification of product')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Non-reduced Capillary Gel Electrophoresis Analysis')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('pH')).toHaveText('initial');
  await expect(p81Proto.getConditionRow('Total protein')).toHaveText('initial');
});

// ══════════════════════════════════════════════════════════════════════════════
//  TC03 — P.8.3 Stab Results DP
//
//  RULE: Always click "Clear all slicers" BEFORE filling any fields.
//
//  Fields selected:
//    Batch                         → MS00715-106
//    Protocol                      → ST-AZD-0292-DP-DSP029230-001
//    Container Orientation         → upright
//    Container Closure             → 3.8mL Nominal Fill
//    Test Article                  → TA-029230_MS00715-106
//    Product Family Preferred Name → All (default)
//    AZD ID                        → AZD0292
//    Timepoint                     → Multiple selections (default)
//    Storage Conditions (Temp/RH)  → temperature 5 (+/-) 3°C
//    Test Name                     → All (default)
//    Result Name                   → All (default)
//    Test Result Combo             → All (default)
//    Show Spec Tests Only          → unchecked (default)
//
//  Expected output:
//    Table title        = P.8.3 Stability Results for AZD0292, batch MS00715-106, at temperature 5 (+/-) 3°C
//    Storage condition  = temperature 5 (+/-) 3°C
//    Timepoints         = initial | 03 months
//
//    Appearance (lyophilized) (SOP-0040726):
//      Color (none)                  → White
//      Data Reference (none)         → MS01603-335
//      Date of Analysis (none)       → 08-28-2023
//      Disposition (none)            → Meets
//      Physical Appearance (none)    → Solid
//      Recon Time (min) (minutes)    → 5
//      Recon Time (sec) (seconds)    → 300
//      Visible Particles (none)      → Free from visible extraneous particles
// ══════════════════════════════════════════════════════════════════════════════
test('TC03 — P.8.3 Stab Results DP', async ({ page }) => {
  const p83 = new P83StabilityResultsPage(page);

  // STEP 1: Navigate to P.8.3 Stability Results page
  await p83.goto(ENV.p83StabilityResultsUrl);
  await p83.waitForPage();

  // STEP 2: Clear all filters — MANDATORY before every TC
  await p83.clearAllFiltersBtn.click();
  await p83.batchDropdown.waitFor({ state: 'visible', timeout: 15000 }); // wait for PBI to settle after clear
  await page.waitForTimeout(1000);

  // STEP 3: Select AZD ID → AZD0292 first, then continue with the remaining fields
  await p83.selectDropdownValue(p83.azdIdDropdown, 'AZD0292');

  // STEP 4: Select Batch → MS00715-106
  await p83.selectDropdownValue(p83.batchDropdown, 'MS00715-106');

  // STEP 5: Select Protocol → ST-AZD-0292-DP-DSP029230-001
  await p83.selectDropdownValue(p83.protocolDropdown, 'ST-AZD-0292-DP-DSP029230-001');

  // STEP 6: Select Container Orientation → upright
  await p83.selectDropdownValue(p83.containerOrientationDropdown, 'upright');

  // STEP 7: Select Container Closure → 3.8mL Nominal Fill
  await p83.selectDropdownValue(p83.containerClosureDropdown, '3.8mL Nominal Fill');

  // STEP 8: Select Test Article → TA-029230_MS00715-106
  await p83.selectDropdownValue(p83.testArticleDropdown, 'TA-029230_MS00715-106');

  // STEP 9: Product Family Preferred Name → All (leave default)

  // STEP 10: Select Storage Conditions → temperature 5 (+/-) 3°C
  await p83.selectDropdownValue(p83.storageConditionsDropdown, 'temperature 5 (+/-) 3°C');

  // STEP 11: Leave remaining optional filters as default
  // Timepoint       → Multiple selections (default)
  // Test Name       → All (default)
  // Result Name     → All (default)
  // Test Result Combo → All (default)
  // Show Spec Tests Only → unchecked (default)

  // STEP 12: Wait for table to render
  await p83.tableTitle.waitFor({ state: 'visible', timeout: 45000 });

  // ── EXPECTED RESULTS — Table title ──────────────────────────
  await expect(p83.tableTitle).toContainText(
    'P.8.3 Stability Results for AZD0292, batch MS00715-106, at temperature 5 (+/-) 3°C'
  );

  // ── EXPECTED RESULTS — Column header ────────────────────────
  // The grid repeats each header's text across hidden secondary cells for
  // accessibility — only the first (primary) cell is the visible header.
  await expect(page.getByRole('columnheader', { name: /temperature 5 \(\+\/\-\) 3°C/ }).first()).toBeVisible();

  // ── EXPECTED RESULTS — Timepoints ───────────────────────────
  await expect(page.getByRole('columnheader', { name: 'initial' }).first()).toBeVisible();
  await expect(page.getByRole('columnheader', { name: '03 months' }).first()).toBeVisible();

  // ── EXPECTED RESULTS — Appearance (lyophilized) rows ────────
  await expect(p83.getCell('White')).toBeVisible();
  await expect(p83.getCell('MS01603-335')).toBeVisible();
  await expect(p83.getCell('08-28-2023')).toBeVisible();
  await expect(p83.getCell('Meets')).toBeVisible();
  await expect(p83.getCell('Solid')).toBeVisible();
  await expect(p83.getCell('5')).toBeVisible();
  await expect(p83.getCell('300')).toBeVisible();
  await expect(p83.getCell('Free from visible extraneous particles')).toBeVisible();
});

// TC04 onwards — add below as you continue sessions
