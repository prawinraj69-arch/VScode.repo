# CMC Playwright — Session Resume Notes

> Last updated: 2026-06-26

---

## ✅ Completed TCs

| TC | Name | Status |
|----|------|--------|
| TC01 | P.8.1 Stab Batch Summary DP | ✅ PASSED |
| TC02 | P.8.1 Stab Protocol Summary DP | ✅ PASSED |
| TC03 | P.8.3 Stab Results DP | ✅ PASSED (2026-06-26) |

All three confirmed passing together in one run (`ENV=sit npx playwright
test document-dashboard --grep "TC0" --project=SIT --workers=1`).

**2026-06-26 fix:** `selectDropdownValue` was silently failing to apply any
slicer selection (`search.fill()` doesn't trigger Power BI's filter, and
`Escape` was clearing all selections, not just closing the popup). Root
cause and the verified working pattern are documented in
`docs/SLICER_INTERACTION.md` — read that before touching slicer code again.

## 🟡 PPT environment — setup ready, NOT yet runnable

PPT is **not deployed yet** (per Prawin, 2026-06-26), so TC01–TC03 cannot run on
PPT right now. Everything that can be prepared without the live PPT report is done:

- ✅ Test code is environment-agnostic — **no code copy needed**. Same spec +
  page objects run on PPT via `ENV=ppt`. `playwright.config.ts` already has a PPT project.
- ✅ `auth/ppt.json` seeded from `auth/sit.json` (same Microsoft tenant/login as SIT).
  Re-run `npm run auth:ppt` if the session is workspace-scoped or expires.
- ✅ `.env.ppt` page IDs pre-filled from SIT (report-section IDs are normally
  identical across environments; P83 was already confirmed identical).
- ✅ Auth-capture scripts fixed — `npm run auth:ppt` now writes `auth/ppt.json`
  (previously it ignored `--env` and overwrote `sit.json`).

**Remaining before PPT can run (needs the live PPT report — only Prawin can get these):**
1. Fill `.env.ppt` → `POWER_BI_GROUP_ID` and `STABILITY_REPORT_ID` with the real
   PPT workspace + report GUIDs (from the PPT report URL).
2. Verify the pre-filled page IDs load on PPT; replace any that don't.
3. Run: `ENV=ppt npx playwright test document-dashboard --grep "TC0" --project=PPT --workers=1`.

See `docs/SKILL.md` Step 8 for the full PPT enablement procedure.

## 🔲 Next to do

- **PPT run** — once PPT is deployed, complete the 3 remaining steps above.
- **TC04** — Next table from Document Dashboard (S.7.1 Batch Summary or FDA Data Elements)

---

## Key IDs (SIT Environment)

| What | ID |
|------|----|
| Power BI Group ID | `ee057979-6120-436e-986c-8769717864c7` |
| Stability Report ID | `e452fcb6-41a6-452b-b1a3-8ca40b7f867e` |
| Stability Home Page ID | `b3ed74ac137ae98e16d2` |
| Doc Dashboard Page ID | `90b0cac629eb7de723a1` |
| P.8.1 Batch Summary Page ID | `03f67392e07a57c72e8e` |
| P.8.1 Protocol Summary Page ID | `ReportSection5d7c126b4d3d5c35570f` |

---

## TC01 — P.8.1 Stab Batch Summary DP

**URL:** `https://app.powerbi.com/groups/ee057979.../reports/e452fcb6.../03f67392e07a57c72e8e`

| Field | Value |
|-------|-------|
| Batch | L028672 |
| Protocol | SS25-0053-001 |
| Container Orientation | unknown physical orientation |
| Container Closure | 75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant |
| Test Article | SS25-0053-TA-004 |
| Product Family Preferred Name | AZD3632 besylate |
| AZD ID | AZD3632 |
| Timepoint / Storage / Test / Result | All (default) |

**Expected results:**

| Row | Value |
|-----|-------|
| Table title | P.8.1 Stability Batch Summary for AZD3632 besylate |
| Batch ID | L028672 |
| Manufacturing Date | 04 February 2025 |
| Manufacturing Site Name | AZ Macclesfield |
| Container Fill | 10.0000 Tablets |
| Container Type | 75 ml square HDPE Bottle + CR cap 33 mm (non AC); no desiccant |
| Study Start Date | 08 April 2025 |
| Latest Reported Timepoint | 52 weeks (w) |
| Strength | 25 MG |

---

## TC02 — P.8.1 Stab Protocol Summary DP

**URL:** `https://app.powerbi.com/groups/ee057979.../reports/e452fcb6.../ReportSection5d7c126b4d3d5c35570f`

| Field | Value |
|-------|-------|
| Batch | MS-113838 |
| Protocol | ST-AZD-0786-DS-DSP078620-002 |
| Container Orientation | (Blank) — default |
| Container Closure | (Blank) — default |
| Test Article | (Blank) — default |
| Product Family Preferred Name | AZD0786 |
| AZD ID | AZD0786 |
| Timepoint (optional) | initial |
| Storage Conditions (optional) | temperature -80 (+/-) 10°C |
| Test Name | All (default) |

**Expected results:**

| Check | Value |
|-------|-------|
| Table title | P.8.1 Stability Protocol Summary for AZD0786 |
| Column headers | Conditions \| Intervals (months) \| temperature -80 (+/-) 10°C |
| All condition rows | initial |

Conditions confirmed: Appearance, Appearance Analysis, Cytotoxicity potency assay, CZE Charge Analysis, Drug to Antibody Ratio, Free Drug, High Performance Size Exclusion Chromatography - Purity, Identification of product, Non-reduced Capillary Gel Electrophoresis Analysis, pH, Total protein

---

## ⚠️ Rules (apply to ALL TCs)

1. **Always click "Clear all slicers" BEFORE filling any fields** — mandatory first step in every TC
2. **Never guess aria-labels** — always read the live DOM via Claude in Chrome before writing slicer code
3. **TC naming convention:** `TC{nn} — {table name} DP` (e.g., TC01 — P.8.1 Stab Batch Summary DP)

---

## How to resume next session

```
1. Open Cowork, select folder: C:\Users\PRAWIN\VS-code-repo\CMC project
2. Say: "continue pbi automation — read cmc-playwright/docs/SESSION_NOTES.md"
3. Navigate to the next Document Dashboard table in Claude Chrome
4. Fill in the fields, then say "TC complete — capture all data"
5. I will write TC03 (and onwards) in document-dashboard.spec.ts
```
