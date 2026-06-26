# Anti-Hallucination Guide — CMC Playwright

> Written 2026-06-26 after a debugging session where guessed root causes wasted
> time. This file exists so future sessions (human or AI) fix problems with
> **evidence**, not plausible-sounding assumptions.

## Why this file exists

During the TC01–TC03 fix, several "obvious" explanations were proposed and acted
on **before** looking at the page — parallel-browser contention, popup z-index,
unconditional `Escape` to "close" popups. Each was wrong or incomplete. The real
causes were only found by driving the live page and reading screenshots:

- `search.fill()` silently fails to filter a Power BI slicer (0 options matched).
- `Escape` clears **all** slicers, it doesn't just close the open one.
- Several `combobox` aria-names were **guessed from the visible label** and were
  wrong (e.g. `storage_condition`, not "Storage conditions (Temp/RH)").

A passing test does **not** prove every locator is right — only the ones that
test actually exercised. Wrong locators sit dormant until a TC touches them.

## The rule

**Do not change a locator or slicer interaction based on a theory. Prove the
theory against the live DOM first.**

## How to prove it (the loop that works)

1. **Write a throwaway probe**: `tests/_debug-<thing>.spec.ts`. Prefix `_debug-`
   so it's obvious it must be deleted and never committed.
2. **Drive the real page** (the project runs headed by default) and
   `await page.screenshot({ path: '<scratchpad>/NN-step.png' })` after **each**
   action — opening a dropdown, typing, clicking an option, closing.
3. **Read the screenshots back** and log concrete signals, e.g.:
   ```ts
   console.log('option count:', await page.getByRole('option', { name: value }).count());
   console.log('aria-expanded:', await dropdown.getAttribute('aria-expanded'));
   ```
   Judge from what you SEE: did the list filter? did the value chip appear? did
   the title change? — not from what "should" happen.
4. **Verify persistence**: chain 3+ fields and screenshot at the end to confirm
   earlier selections survived. Many slicer bugs only appear on the *next* field.
5. **Promote, then delete**: only after the screenshot proves it, copy the
   verified steps into the real page object. Delete the `_debug-*` spec.

Scratchpad dir for screenshots (session-specific, never in the repo):
`C:\Users\PRAWIN\AppData\Local\Temp\claude\...\scratchpad`

## Red flags that you're about to hallucinate

- "It's probably a timing/parallelism issue" → measure it before bumping timeouts.
- "Escape will just close the popup" → it ran a global clear here. Verify side effects.
- "The aria-label is obviously the visible text" → it's usually the internal
  field name. Read the DOM.
- Editing a page object and immediately re-running the full suite, instead of
  isolating the one interaction with a probe.
- Explaining a failure from the error message alone without opening the
  screenshot / `error-context.md` Playwright already saved under `test-results/`.

## Free evidence you already have — use it first

- `test-results/<test>/error-context.md` — the ARIA snapshot at failure time.
  It shows the real roles/names of every element. Read it before theorizing.
- `test-results/<test>/test-failed-1.png` — what the page actually looked like.
- `test-results/<test>/video.webm` and `trace.zip` — the full run.

See `docs/SLICER_INTERACTION.md` for the concrete, verified findings this
process produced.
