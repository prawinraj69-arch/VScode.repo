# CMC Playwright — Automation Rules

## Rule 1: Clear all filters before every TC
**ALWAYS click "Clear all slicers" as Step 1 of EVERY test case.**
Never skip this — leftover filter state from a previous test will corrupt results.

## Rule 2: Never guess slicer labels
Every Power BI page has different `aria-label` values for its slicers.
Always read the live DOM via **Claude in Chrome** before writing slicer/combobox code.

## Rule 3: TC naming convention
Format: `TC{nn} — {table name} DP`
Examples:
- `TC01 — P.8.1 Stab Batch Summary DP`
- `TC02 — P.8.1 Stab Protocol Summary DP`
- `TC03 — P.8.3 Stability Results DP`

## Rule 4: Navigation steps ≠ TC
Steps to navigate to a page (click menus, select workspace, accept disclaimer) are
**navigation/setup steps** — NOT test cases. A TC starts when you fill in data fields
and validate the table output.

## Rule 5: Optional filters left as default = leave them, don't touch
If a filter shows "All" and you are not selecting a specific value, do NOT interact
with it. Just move on to the next field.

## Rule 6: Two environments — same code, config only
Every TC runs on both SIT and PPT using the **same** spec + page objects; the
environment is selected by `ENV`, never by copying code.
- SIT: `ENV=sit npx playwright test --project=SIT --workers=1`
- PPT: `ENV=ppt npx playwright test --project=PPT --workers=1`

To enable PPT you only fill configuration:
1. `.env.ppt` → `POWER_BI_GROUP_ID` and `STABILITY_REPORT_ID` (the PPT workspace
   + report GUIDs; the page IDs are copied from SIT and normally identical).
2. `auth/ppt.json` → capture with `npm run auth:ppt` (or seed from `auth/sit.json`
   if PPT is the same tenant).

Expected data values are hardcoded in the TCs assuming PPT holds the same data
in the same dashboard. If PPT data differs, update the assertions — not the
locators.

## Rule 6b: Run serially (`--workers=1`)
Parallel headed browsers share one live Power BI session and overload it,
causing unrelated TCs to fail. Always pass `--workers=1` for these reports.

## Rule 7: selectDropdownValue helper
All slicer interactions use the `selectDropdownValue(dropdown, value)` method
defined in each page object. Do NOT interact with slicers using raw Playwright
clicks in tests — always go through the page object method.

See `docs/SLICER_INTERACTION.md` for the verified mechanics behind that
method — in particular: use `pressSequentially`, not `fill()`, on the search
box, and never press `Escape` (it clears all slicers, not just the open one).

## Rule 8: Verify slicer/locator behavior with evidence, not assumptions
When a slicer or locator misbehaves, don't guess at a fix. Write a throwaway
`tests/_debug-*.spec.ts`, screenshot after each step into the scratchpad
directory, and read the screenshots back to confirm what actually happened
(option counts, `aria-expanded`, selected values, rendered text) before
changing the real page object. Delete the debug spec once done.
Full process → `docs/ANTI_HALLUCINATION.md`; verified findings →
`docs/SLICER_INTERACTION.md`.

## Rule 9: A passing test ≠ all locators correct
A green TC only proves the locators it actually exercised. Wrong aria-names sit
dormant until a test touches that field (this is exactly how TC03's
`storage_condition` bug hid). When adding a TC that uses a not-yet-exercised
field, read its real aria-name from the live DOM — don't trust the page object.
