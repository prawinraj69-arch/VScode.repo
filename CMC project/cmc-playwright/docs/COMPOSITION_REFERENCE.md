# Composition Report — Confirmed IDs & Slicer Reference

> Migrated from pbi-automation/CLAUDE.md (last confirmed: 2026-06-22 via live DOM inspection)
> These values were confirmed using Claude in Chrome extension on the live SIT environment.
> **Always re-verify via DOM before writing new slicer code — labels can change between releases.**

---

## Report Info

| What | Value |
|------|-------|
| Report name | CMC Composition Data Hub - SIT |
| Report ID | `d5e9c3b1-9135-4212-b19c-abafaddb569e` |
| Workspace Group ID | `ee057979-6120-436e-986c-8769717864c7` |
| Base URL pattern | `/groups/<groupId>/reports/<reportId>/<sectionId>?experience=power-bi` |

---

## Page Section IDs (all confirmed from live DOM)

| Page | Section ID |
|------|-----------|
| Home (landing + Accept button) | `22bfa36c89ab9287172e` |
| Tables (selector page) | `96c1bb731233b2271c40` |
| P.1 Composition | `2592b090a669970c2283` |
| P.4.1 Specifications for Excipients T1 | `0bfa906906bbdda7684b` |
| S.1.1 Nomenclature | `6464e6fa2e2fb31e4f9e` |
| S.1.2 Structure | `ReportSectionbf9bb3f8755eae3ff787` |
| S.3.1 Characterisation | `968223a314c7bd9e900e` |

---

## ⚠️ Critical: Slicer aria-labels differ between pages

Do NOT assume the same label works on different pages. Always read the live DOM first.

---

## S.1.2 Structure — Confirmed Slicers

| Slicer heading | aria-label | Notes |
|---|---|---|
| AZD Id | `"AZD Id"` | **title case** — different from other pages! |
| Product Family Preferred Name | `"Product Family Preferred Name"` | |
| Substance ID | `"Substance ID"` | |
| Official Name | `"Official Name"` | |

**Confirmed option values:**
- AZD Id: `ACP-196`, `ALXN2050`, `ALXN2550`, `APTA-2217`, `AZD0156`, `AZD0186`, `AZD0233`
- Product Family Preferred Name: `acalabrutinib`
- Substance ID: `AZSUB5999112350`
- Official Name: `acalabrutinib`

**Data table:** `group "S.1.2 Structure"`
Row headers: `Substance Structure` | `Molecular Formula` | `Molecular Weight` | `Structural Representation`

**Buttons:** `button[aria-label*="Clear all slicers"]` → alert shows `"Selections cleared"`

---

## S.3.1 Characterisation — Confirmed Slicers

| Slicer heading | aria-label | Notes |
|---|---|---|
| AZD ID | `"AZD ID"` | **ALL CAPS** — different from S.1.2's `"AZD Id"`! |
| Product Family Preferred Name | `"Product Family Preferred Name"` | |
| Compound ID | `"Compound ID"` | S.1.2 calls this "Substance ID" |
| Substance Name | `"Substance Name"` | S.1.2 calls this "Official Name" |
| Experiment Title | `listbox[aria-label="Experiment Title"]` | Use scoped search box (see below) |
| Lab Technique | `"Lab Technique"` | |
| Category | `"Category"` | |
| Sub Category 1 | `"Sub Category 1"` | |
| Sub Category 2 | `"Sub Category 2"` | |

**Experiment Title search box:** Multiple `Search` textboxes exist (one per slicer). Scope by finding the group containing the Experiment Title listbox:
```ts
page.getByRole('group')
  .filter({ has: page.locator('listbox[aria-label="Experiment Title"]') })
  .getByPlaceholder('Search')
```

**Confirmed option values:**
- Lab Technique: `"Balance"`, `"Collecting Descendants Results"`, `"NMR - Nuclear Magnetic Resonance spectroscopy"`, `"Pipette - Dispenser"`
- Sub Category 1: `"Characterisation and testing"`, `"In Process Control"`, `"In Process Test"`, `"Method development"`, `"Method validation"`, `"Other"`, `"Release and Stability testing"`, `"Release testing"`
- Sub Category 2: `"Characterization of samples/screening stability (C3)"`, `"Chemistry requests"`, `"Contributing raw materials"`, `"Device development"`, `"Drug product"`, `"Drug substance"`, `"Excipient"`, `"Impurity tracking"`
- Experiment Title (AZD9833 context): `"AZ14233934 (LIMS Lot: 4893 Batch ID: PC23154-7-D11-1 ) Description, ID and Assay by NMR"` ← note the SPACE before `)`

**Data table:** `group[aria-label*="S3.1 Characterisation"]` ← no dot (confirmed)
Columns: `Image` | `File URL` | `File Title`
Confirmed file titles: `G26-001658_AZ14233934_Assay_2_200uL_TFA.spectrus`, `G26-001658_AZ14233934_Assay_1_200uL_TFA.spectrus`

---

## P.1 Composition — Confirmed Slicers

| Slicer heading | aria-label | Notes |
|---|---|---|
| AZD ID | `"AZD ID"` | ALL CAPS |
| Product Family Name | `"Product Family Name"` | **NO "Preferred"** — unique to P.1! |
| Active Ingredients Strength | `"active_ingredients_strength"` | **snake_case** aria-label — unique to P.1! |
| Dosage Form | `"Dosage Form"` | Only exists on P.1 |
| Substance ID | `"Substance ID"` | |
| Substance Name | `"Substance Name"` | |

**Confirmed option values:**
- AZD ID: `AZD8233`
- Dosage Form: `"solution for injection"`
- Active Ingredients Strength: `"AZSUB6533636362 63 g/l"`

**Data table:** `[aria-label*="P.1 Description and Composition"]`
Columns: `Components` | `Quantity` | `Type` | `Standard`
Confirmed row values (AZD8233 context):
- qty `8.2` | standard `Ph. Eur., USP-NF`
- qty `63 g/l` | standard `In-house`
- qty `6.16 g/l` | standard `Ph. Eur., USP-NF`
- qty `100 % (V/V)` | type `solvent` | standard `Ph. Eur., USP-NF`
- qty `1.78 g/l` | standard `Ph. Eur., USP-NF`

---

## Pages NOT YET CODED

These section IDs are known but DOM inspection not done yet:
- `P.4.1 Specifications for Excipients T1` → `0bfa906906bbdda7684b`
- `S.1.1 Nomenclature` → `6464e6fa2e2fb31e4f9e`

---

## General Locator Rules

1. **Clear all slicers button:** `button[aria-label*="Clear all slicers"]` — visible text says "Clear all filters" but aria-label says "Clear all slicers"
2. **Report disambiguation:** Always use `a[href*="/reports/"]` vs `a[href*="/datasets/"]` to click reports (not semantic models) in workspace list
3. **Slicer pattern:** PBI renders combobox + listbox pairs — click combobox to open, click option in listbox
4. **Direct URL navigation** is always faster than clicking through the workspace list
5. **"Visuals are loading..."** text appears during data loads — wait for it to disappear before asserting
