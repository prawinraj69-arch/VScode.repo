# Power BI Slicer Interaction — Verified Mechanics

> Verified against the live SIT DOM on 2026-06-26 by stepping through each
> action with screenshots and ARIA snapshots (not guessed). If `selectDropdownValue`
> ever needs to change again, re-verify the same way before editing — see
> "How this was verified" below.

## The three things that broke TC01/TC02/TC03, and the proof

### 1. `search.fill(value)` does NOT filter the slicer's option list

Power BI's slicer search box is an Angular component that filters on real
keystroke events. Playwright's `.fill()` sets the input value via the DOM
property and fires a synthetic `input` event — Angular's key listener never
sees it, so the option list stays completely unfiltered.

**Proof:** after `search.fill('AZD3632')`, `getByRole('option', { name: 'AZD3632' })`
matched **0** elements; the visible list was still the full, unfiltered,
alphabetically-sorted option set. Switching to
`search.pressSequentially('AZD3632', { delay: 100 })` (real per-character
key events) immediately filtered the list to exactly **1** option: `"AZD3632"`.

**Rule:** always use `pressSequentially`, never `fill()`, on a slicer search box.

### 2. Pressing `Escape` does not just close the popup — it clears ALL selections

The original bug report ("Selections cleared" alert visible in a captured
snapshot) was a real signal, not noise. Escape on this Power BI report
triggers a global "clear all slicers" action, not a local "close this
dropdown" action.

**Proof:** with `Escape` used to close each dropdown after selecting a value,
every single slicer ended the test still showing `"All"` — including the
very last field selected. The table title stayed on its unfilled placeholder
(`"P.8.1 Stability Batch Summary for [AZ Product]"`) for the entire run.

**Rule:** never press `Escape` while interacting with a slicer. Don't use it
to "make sure the popup is closed" — it's not a safe no-op.

### 3. The popup does not close itself after clicking an option — but clicking the dropdown trigger again does, safely

After clicking the matching `option`, `aria-expanded` on the combobox stayed
`"true"` — the popup stays open with the option now checked. If you don't
close it, the next field's `dropdown.click()` fails with "subtree intercepts
pointer events" (this was the original TC03 failure).

**Proof:** clicking the dropdown trigger a second time (toggling it) set
`aria-expanded` to `"false"` and the selection survived into the next
field — verified across three chained selections (AZD ID → Batch → Protocol)
with a screenshot showing all three retaining their values.

**Rule:** to close a slicer popup after selecting, click the dropdown
trigger itself again. Do not use Escape.

## The verified `selectDropdownValue` pattern

```ts
async selectDropdownValue(dropdown: Locator, value: string) {
  await dropdown.click();
  await this.page.waitForTimeout(600);

  const search = this.page.getByRole('textbox', { name: /search/i }).first();
  await search.waitFor({ state: 'visible', timeout: 4000 });
  await search.pressSequentially(value, { delay: 100 });   // NOT .fill()
  await this.page.waitForTimeout(800);

  const option = this.page.getByRole('option', { name: value }).first();
  await option.waitFor({ state: 'visible', timeout: 4000 });
  await option.click();
  await this.page.waitForTimeout(800);

  await dropdown.click();          // toggle-close — NOT Escape
  await this.page.waitForTimeout(600);

  try {
    await this.page.locator('text=Visuals are loading...').first().waitFor({ state: 'hidden', timeout: 60000 });
  } catch {}
  await this.page.waitForTimeout(1000);
}
```

This is implemented identically in `P81BatchSummaryPage.ts`,
`P81ProtocolSummaryPage.ts`, and `P83StabilityResultsPage.ts`.

## Other guessed-name bugs found and fixed the same way

Several `combobox` locators were defined using the **visible label text**
instead of the slicer's actual accessible name (its underlying field name).
These only failed once a test actually exercised that field, so some sat
unverified for a while:

| Page | Field | Wrong (guessed) name | Correct name (from live DOM) |
|---|---|---|---|
| `P83StabilityResultsPage` | Storage conditions | `Storage conditions (Temp/RH)` | `storage_condition` |
| `P83StabilityResultsPage` | Timepoint | `Timepoint` | `LOWER_TIMEPOINT` |
| `P83StabilityResultsPage` | Test Name | `Test Name` | `test_name` |
| `P83StabilityResultsPage` | Result Name | `Result Name` | `result_name` |
| `P83StabilityResultsPage` | Test Result Combo | `Test Result Combo` | `Test Result` |

`P81BatchSummaryPage` and `P81ProtocolSummaryPage` already had the correct
names for their equivalents — only `P83StabilityResultsPage` had guessed
wrong. **Lesson: a passing test does not mean every locator in the page
object is correct — only the locators that test actually exercises.**

## Two other strict-mode bugs (not slicer-related, found while fixing TC03)

- **`tableTitle` locators** (`r.locator('text=P.8.1 Stability Batch Summary for')`)
  matched 3 elements once the page fully rendered (a tooltip `<p>`, the
  actual `<h3>` title, and a "See more tables" button echoing the same
  text). Fixed by scoping to `r.getByRole('heading', { name: /.../  })`,
  which uniquely matches the `<h3>`.
- **Column headers and gridcells in the P.8.3 results table** repeat the
  same text across hidden secondary cells (grid accessibility structure)
  or across multiple timepoint columns. Any assertion on these must use
  `.first()` or it throws a strict-mode violation once more than one
  timepoint/column is in view.

## How this was verified (so it can be re-verified the same way)

1. Write a throwaway spec under `tests/_debug-*.spec.ts` (delete it when done —
   never commit debug specs).
2. Drive the real page with Playwright (`headless: false` is already the
   project default), screenshot after each action into the scratchpad
   directory, and read the screenshots back — don't infer from logs alone.
3. Check concrete signals: `option` count after typing, `aria-expanded`
   after each click, the actual rendered slicer value chips, and the table
   title/data — not assumptions about what "should" happen.
4. Only promote the verified behavior into the real page objects once a
   multi-field chain (3+ fields) has been shown to survive end-to-end in a
   screenshot.
