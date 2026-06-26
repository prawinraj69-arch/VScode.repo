# CLAUDE.md — CMC Project Root

> Last updated: 2026-06-26 by Prawin (prawinraj69@gmail.com)
> **Read this first in every new session.**
> For full context → read `cmc-playwright/docs/SESSION_NOTES.md`

---

## Active Project

### CMC Playwright (TypeScript) — `cmc-playwright/` ← ONLY ACTIVE PROJECT

Full session notes, TC status, all IDs → `cmc-playwright/docs/SESSION_NOTES.md`
Rules → `cmc-playwright/docs/RULES.md`
Workflow skill → `cmc-playwright/docs/SKILL.md`
Composition report IDs & slicer reference → `cmc-playwright/docs/COMPOSITION_REFERENCE.md`

---

## How to Continue Work

```
1. Open Cowork, select folder: C:\Users\PRAWIN\VS-code-repo\CMC project
2. Say: "continue pbi automation — read cmc-playwright/docs/SESSION_NOTES.md"
3. Claude reads SESSION_NOTES.md for full context (no re-explaining needed)
4. Navigate to the next PBI page in Claude Chrome
5. Fill in the fields, say "TC complete — capture all data"
6. Claude writes the next TC in document-dashboard.spec.ts
```

---

## Quick Reference — TC Status

### Stability Data Hub → Document Dashboard
| TC | Name | Page ID | Status |
|---|---|---|---|
| TC01 | P.8.1 Stab Batch Summary DP | `03f67392e07a57c72e8e` | ✅ PASSED |
| TC02 | P.8.1 Stab Protocol Summary DP | `ReportSection5d7c126b4d3d5c35570f` | ✅ PASSED |
| TC03 | P.8.3 Stab Results DP | `ReportSection18a7ee8355c6a90b9a30` | ✅ PASSED |
| TC04 | (next table) | TBD | 🔲 |

> Status above is **SIT**. **PPT is set up but not yet runnable** — PPT isn't
> deployed, and `.env.ppt` still needs the real `POWER_BI_GROUP_ID` +
> `STABILITY_REPORT_ID`. Full PPT state + steps → `cmc-playwright/docs/SESSION_NOTES.md`.

---

## Key IDs (SIT Environment)

| What | ID |
|------|----|
| Power BI Group ID | `ee057979-6120-436e-986c-8769717864c7` |
| Stability Report ID | `e452fcb6-41a6-452b-b1a3-8ca40b7f867e` |
| Composition Report ID | `d5e9c3b1-9135-4212-b19c-abafaddb569e` |
| Control Report ID | `609b982c-0047-45cb-8d78-4b28520cea02` |
| Impurities Report ID | `798b6938-3021-4857-a5d6-6195c334304e` |
| Stability Home Page ID | `b3ed74ac137ae98e16d2` |
| Doc Dashboard Page ID | `90b0cac629eb7de723a1` |
| P.8.1 Batch Summary Page ID | `03f67392e07a57c72e8e` |
| P.8.1 Protocol Summary Page ID | `ReportSection5d7c126b4d3d5c35570f` |
| P.8.3 Stability Results Page ID | `ReportSection18a7ee8355c6a90b9a30` |

---

## ⚠️ Rules (apply to ALL TCs)

1. **Always click "Clear all slicers" BEFORE filling any fields** — mandatory first step in every TC
2. **Never guess aria-labels** — always read the live DOM before writing slicer code. The
   aria-name is the field's *internal* name (e.g. `storage_condition`), not the visible label.
3. **TC naming:** `TC{nn} — {table name} DP`
4. **Slicer selection** — use `pressSequentially` (NOT `fill()`) on the search box, click the
   option, then click the dropdown again to close. **Never press `Escape`** — it clears ALL
   slicers. Details → `cmc-playwright/docs/SLICER_INTERACTION.md`.
5. **Run serially** — always `--workers=1`. Parallel headed browsers overload the live PBI session.
6. **Verify with evidence, never guess** — debug locator/slicer issues with a throwaway
   `tests/_debug-*.spec.ts` + screenshots, then delete it. → `cmc-playwright/docs/ANTI_HALLUCINATION.md`.

---

## Key File Locations

| What | Where |
|------|-------|
| Session notes + TC status | `cmc-playwright/docs/SESSION_NOTES.md` |
| All rules | `cmc-playwright/docs/RULES.md` |
| Workflow skill | `cmc-playwright/docs/SKILL.md` |
| Composition IDs + slicer reference | `cmc-playwright/docs/COMPOSITION_REFERENCE.md` |
| Verified slicer interaction mechanics | `cmc-playwright/docs/SLICER_INTERACTION.md` |
| Anti-hallucination / evidence-first workflow | `cmc-playwright/docs/ANTI_HALLUCINATION.md` |
| PPT environment config | `cmc-playwright/.env.ppt` |
| Main test file | `cmc-playwright/tests/document-dashboard.spec.ts` |
| Environment config | `cmc-playwright/utils/env.ts` |
| SIT env variables | `cmc-playwright/.env.sit` |
| PPT env variables | `cmc-playwright/.env.ppt` |
