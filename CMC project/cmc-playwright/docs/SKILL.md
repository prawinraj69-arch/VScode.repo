# SKILL.md — CMC Playwright Automation Workflow

> Migrated and adapted from pbi-automation/SKILL.md (2026-06-22)
> Updated for TypeScript/Playwright (cmc-playwright project)

---

## Skill: validate-powerbi

### Description
End-to-end Playwright (TypeScript) automation for validating Power BI reports.
Handles SSO/MFA auth via saved browser storage state, multi-environment support (SIT/PPT),
slicer/filter interactions, and data value assertions.

Uses **Claude in Chrome** extension for live DOM inspection to get exact aria-labels,
section IDs, and slicer option values — **never guess these from visual inspection alone**.

---

### Trigger Conditions
Use this workflow when asked to:
- Add a new Power BI test case (TC)
- Validate a report, table, slicer, or KPI value
- Navigate to a new page section in SIT or PPT
- Debug a failing TC
- Extend the Page Object Model for a new report page
- Inspect a PBI page with Claude in Chrome to get real locators

---

### Workflow

#### Step 1 — Identify target
- Which environment? (SIT / PPT)
- Which report? (stability / composition / control / impurities)
- Which page section? (check `utils/env.ts` or `docs/COMPOSITION_REFERENCE.md` for known IDs)

#### Step 2 — Auth check
The project uses Playwright's saved storage state for MFA bypass. There is one
file **per environment**: `auth/sit.json` and `auth/ppt.json`.
```bash
ls -lh auth/sit.json   # SIT session  (~680 KB)
ls -lh auth/ppt.json   # PPT session  (~680 KB)
```
If missing/expired, regenerate with the matching command:
```bash
npm run auth:sit   # opens a browser → log in to SIT  → ENTER → writes auth/sit.json
npm run auth:ppt   # opens a browser → log in to PPT  → ENTER → writes auth/ppt.json
```
Auth state is **gitignored** (`auth/`) — each person generates their own. Never commit.

#### Step 3 — Inspect live DOM (for new pages)
Use Claude in Chrome extension:
```
1. Navigate to the PBI report page section via direct URL
2. Use read_page(filter="interactive", depth=10) in Claude in Chrome
3. Note:
   - combobox aria-labels (DIFFER per page — do NOT assume)
   - listbox aria-labels (may differ from combobox label)
   - group aria-labels for data tables
   - columnheader / rowheader text
   - Confirmed option values in listboxes
4. Confirm section ID from the browser URL bar
```

#### Step 4 — Add IDs to env.ts (if new page section)
```typescript
// In utils/env.ts — add new page ID
newPageId: process.env.NEW_PAGE_ID || '',

get newPageUrl(): string {
  return `${this.baseURL}/groups/${this.groupId}/reports/${this.reportId}/${this.newPageId}?experience=power-bi`;
},
```
And add to `.env.sit` / `.env.ppt`:
```
NEW_PAGE_ID=confirmed_section_id_from_url
```

#### Step 5 — Create/update page object
- Create a new file in `pages/` (e.g., `pages/NewTablePage.ts`)
- Add locator constants as class properties
- Add a `selectDropdownValue(dropdown, value)` method for slicer interactions
- Add `waitForPage()`, `clearAllFiltersBtn`, and assertion helpers
- Follow the pattern established in `P81BatchSummaryPage.ts`

#### Step 6 — Write the TC
```typescript
// In tests/document-dashboard.spec.ts (or appropriate spec file)
test('TC{nn} — {table name} DP', async ({ page }) => {
  const p = new NewTablePage(page);

  // STEP 1: Navigate
  await p.goto(ENV.newPageUrl);
  await p.waitForPage();

  // STEP 2: Clear all filters — MANDATORY
  await p.clearAllFiltersBtn.click();
  await page.waitForTimeout(1500);

  // STEP 3+: Select filters
  await p.selectDropdownValue(p.someDropdown, 'confirmed value');

  // STEP N: Wait and assert
  await p.tableTitle.waitFor({ state: 'visible', timeout: 15000 });
  await expect(p.tableTitle).toContainText('Expected Title');
  // ... more assertions
});
```

#### Step 7 — Run and verify
Run **serially** (`--workers=1`). Parallel headed browsers share one live Power BI
session and overload it; serial is required for reliable slicer-heavy TCs.
```bash
# SIT — all document-dashboard TCs
ENV=sit npx playwright test document-dashboard --project=SIT --workers=1

# SIT — just TC01–TC03
ENV=sit npx playwright test document-dashboard --grep "TC0" --project=SIT --workers=1

# PPT (requires .env.ppt GUIDs filled + auth/ppt.json — see Step 8)
ENV=ppt npx playwright test document-dashboard --project=PPT --workers=1

# Single TC
ENV=sit npx playwright test --grep "TC01" --project=SIT --workers=1
```

#### Step 8 — Running the SAME TCs against PPT
The test code is environment-agnostic — the same spec + page objects run against
either environment via `ENV`. To enable PPT you only need configuration, no code copy:
1. **Fill the two PPT GUIDs** in `.env.ppt` — `POWER_BI_GROUP_ID` and
   `STABILITY_REPORT_ID`. Get them from the live PPT report URL:
   `app.powerbi.com/groups/<GROUP_ID>/reports/<REPORT_ID>/<pageId>`.
   The page (report-section) IDs are already copied from SIT and are normally
   identical across environments — verify, and only change one if its page fails to load.
2. **Capture PPT auth**: `npm run auth:ppt` (or reuse SIT's session if PPT is the
   same tenant — `auth/ppt.json` may be seeded from `auth/sit.json`).
3. Run: `ENV=ppt npx playwright test document-dashboard --project=PPT --workers=1`.

The expected data values (batches, AZD IDs, dates) are hardcoded in the TCs on the
assumption PPT holds the **same data in the same dashboard** as SIT. If PPT data
differs, the assertions — not the locators — are what you update.

---

### TC Naming Convention
Format: `TC{nn} — {table name} DP`

Examples:
- `TC01 — P.8.1 Stab Batch Summary DP`
- `TC02 — P.8.1 Stab Protocol Summary DP`
- `TC03 — P.8.3 Stability Results DP`

Navigation/setup steps (accept disclaimer, click menus) are **not** TCs. A TC starts when you fill in filter fields and validate table output.

---

### Slicer Interaction Pattern (TypeScript) — VERIFIED

> ⚠️ This is the **only** pattern that works on these reports. The naïve
> "click dropdown → click option" does NOT apply the filter. Full proof and
> reasoning: **`docs/SLICER_INTERACTION.md`**. Do not change this without
> re-verifying via the screenshot method documented there.

```typescript
async selectDropdownValue(dropdown: Locator, value: string) {
  await dropdown.click();
  await this.page.waitForTimeout(600);

  const search = this.page.getByRole('textbox', { name: /search/i }).first();
  await search.waitFor({ state: 'visible', timeout: 4000 });
  await search.pressSequentially(value, { delay: 100 });   // NOT .fill() — fill() doesn't trigger PBI's filter
  await this.page.waitForTimeout(800);

  const option = this.page.getByRole('option', { name: value }).first();
  await option.waitFor({ state: 'visible', timeout: 4000 });
  await option.click();
  await this.page.waitForTimeout(800);

  await dropdown.click();   // toggle the popup closed — NEVER Escape (Escape clears ALL slicers)
  await this.page.waitForTimeout(600);

  try {
    await this.page.locator('text=Visuals are loading...').first().waitFor({ state: 'hidden', timeout: 60000 });
  } catch {}
  await this.page.waitForTimeout(1000);
}
```

**Three non-obvious facts this encodes (all screenshot-verified):**
1. `search.fill()` sets the value without firing the keystrokes PBI's Angular
   filter listens for → list never narrows → option click finds nothing.
   Use `pressSequentially`.
2. `Escape` triggers PBI's "Selections cleared" → wipes every field chosen so
   far, not just the open popup. Never press it.
3. The popup stays open after an option click; close it by clicking the
   dropdown trigger again, or it intercepts clicks on the next slicer.

### Strict-mode gotchas (use `.first()` / `getByRole('heading')`)
- **Table titles**: `text=...` matches the tooltip + heading + a "See more
  tables" button (3 elements). Use `getByRole('heading', { name: /.../ })`.
- **Column headers / gridcells**: the pivot grid repeats each value across
  hidden secondary cells and across timepoint columns. Assert with `.first()`.
- **Slicer aria-names are the field's internal name, not the visible label**
  (e.g. Storage conditions → `storage_condition`, Timepoint → `LOWER_TIMEPOINT`,
  Test Name → `test_name`). Read the live DOM; never use the visible label.

---

### Known Confirmed Values (CMC SIT)

| What | Value |
|------|-------|
| Workspace Group ID | `ee057979-6120-436e-986c-8769717864c7` |
| Stability Report ID | `e452fcb6-41a6-452b-b1a3-8ca40b7f867e` |
| Composition Report ID | `d5e9c3b1-9135-4212-b19c-abafaddb569e` |
| Control Report ID | `609b982c-0047-45cb-8d78-4b28520cea02` |
| Impurities Report ID | `798b6938-3021-4857-a5d6-6195c334304e` |

For Composition report slicer details → see `docs/COMPOSITION_REFERENCE.md`

---

### Security Rules
- `auth/sit.json` / `auth/ppt.json` — **NEVER commit**. The whole `auth/` dir is
  gitignored. They hold live session cookies. Each person generates their own.
- `.env.sit` / `.env.ppt` — hold Power BI workspace/report GUIDs + page IDs (not
  credentials). Treat as environment config; don't paste secrets into them.

---

### Anti-hallucination workflow (MANDATORY for locator/slicer work)
When a slicer or locator misbehaves, **do not guess a fix.** Prove it:
1. Write a throwaway `tests/_debug-*.spec.ts`.
2. Drive the real page, `page.screenshot()` after each step into the scratchpad dir.
3. Read the screenshots back and check concrete signals: option count after
   typing, `aria-expanded` after clicks, the actual rendered values, table text.
4. Only promote behavior into the real page object once a 3+ field chain is
   shown surviving end-to-end in a screenshot.
5. Delete the debug spec — never commit `_debug-*` files.

Full worked example and the reasoning: `docs/ANTI_HALLUCINATION.md` and
`docs/SLICER_INTERACTION.md`.
