---
name: tool-app-design
description: How Divyansh wants a tool app to look and behave, in PyQt or as a self-contained HTML page. Load this before building ANY desktop or web tool app for him — it encodes the look (flat, monochrome, professional), the layout rules (everything in one view, no dropdowns), the notation rules (white-on-black negation, exact values, never rounded) and the interaction rules (cross-linked panels, sort/group headers).
---

# Tool-app design — Divyansh's house style

He is building **tools for himself to think in**, not products for an audience.
He is blunt and fast-moving; he will tell you in three words that something is
wrong. The style below is the distilled result of a long build of
`LogicGatesStudio.py` (PyQt) and its HTML twin `studio.html`. Follow it from the
first draft — most of these rules exist because he had to ask for them twice.

**The two cardinal rules, above all else:**

1. **It must not look "AI-ish".** He will reject a UI on sight for this alone.
2. **Nothing is rounded, nothing is faked.** Every value is exact and every
   table is generated from the underlying data, never retyped.

---

## 1. Look

Flat, monochrome, dense — professional desktop software, circa a lab instrument.

- **No** rounded floating cards, **no** bright blue accent, **no** marketing
  subtitle, **no** explainer paragraph under a heading, **no** generous
  whitespace. Those are the specific things that read as "AI-ish" to him.
- **Palette** (reuse exactly):
  | role | value |
  |---|---|
  | ink (text) | `#1f1f1f` |
  | muted | `#6b6b6b` |
  | border | `#dcdcdc` |
  | grid line | `#d6d6d6` |
  | table header | `#efefef` |
  | accent / active | `#e0a53a` (amber) |
  | highlighted row | `#f7e2b8` |
  | group band | `#f0f0f0` |
  | negated token | `#000` bg / `#fff` text |
- **Type**: monospace for all data (`"DejaVu Sans Mono", ui-monospace`), 8–9 pt;
  sans for chrome. Table rows tight — 16–21 px — with `padding: 0 5px`.
- **Chrome**: a **top bar**, never a sidebar. A brand word on the left, then
  controls, then the tab strip. Tabs **spread across the bar** — he finds
  hard-left tabs "ewww".
- **Cards**: a thin 1px border, a small muted title sitting on the border, then
  the content. Nothing else.
- **The PyQt look**: no `QGroupBox` styling flourishes, no gradients, no icons
  unless asked. `mono_font(n)` for data, a single flat `STYLE` QSS string.

## 2. Layout — "everything in one view"

- He hates **dropdowns** and **scrollbars**. Show every option at once; avoid a
  control that hides its choices. (One deliberate exception was allowed: a
  dropdown placed *inside a table's corner cell* to pick that table's operator.
  Ask before adding any other.)
- Fit the whole thing on one screen. Only split into a new tab when the content
  genuinely does not fit — and say so when you do.
- **Tables beat prose.** When there are several representations of the same
  object, make them **columns of one table**, not paragraphs. If he asks "what
  are the representations?", he wants to *see* them in a table, not read them.
- Related tables go in **sub-tabs** (e.g. `representations · matrix ·
  universal`), not stacked down a page.
- Cards in a row, side by side, with `stretch` so they share the width.

## 3. Notation — the part he cares about most

- **Negation is the word `not`.** Write `not a`, `not b`, `a ∧ not b`,
  `not(not a and not b)`. **Not** a bar over the letter, **not** `¬`, and **not**
  an inverted white-on-black token — he tried that and rejected it as less clean
  than the words. (So: no box-drawing painter at all; just convert the negation
  marker to `"not " + letter` at render time.)
- **Never box letters inside words.** If you ever do render literals with a
  background, only the letters that *are* literals get it — the `A` in `AND` or
  `FALSE` stays plain.
- **Everything in terms of the variables.** Write expressions as combinations
  of `a, ¬a, b, ¬b` with AND / OR / NOT. **Never** use implication (`→`, `⊆`) —
  he does not accept it. Express `a → b` as `¬a ∨ b`.
- **Carry the formal name in brackets**: `a ∧ b (AND)`,
  `not(not a and not b)` style. When he asks for expressions "in words", use the
  connective names (`and or not nand nor xor xnor`), not the symbols.
- **NEVER ROUND. EVER.** This is a standing instruction he repeated. If a value
  is irrational, print the closed form: the golden ratio as `(1+√5)/2`, a norm
  as `√2`, an eigenvalue as `√((3+√5)/2)`. If a value is a half, print `1/2`.
  A decimal fallback anywhere in the code is a bug, not a shortcut.
- Keep the **determinant** and similar invariants alongside the object they
  describe (he annotated the `(0)/(1)/(−1)` by hand and wanted it kept).
- Geometry conventions he stated: all-zeros **bottom-left**, all-ones
  **top-right**, in every dimension.

## 4. Interaction

- **Cross-linked panels.** When the same object appears in several panels, they
  must highlight **both ways**: click in one, the matching element lights up in
  all the others *and* the matching table row. He will notice if one direction
  is missing — he asked for it twice.
- **Multi-select**, not radio, where a selection can combine. The highlight is
  the **intersection** of what is ticked; ticking `a` and `ā` must go empty.
- **Column headers cycle**: nothing → sort ascending → sort descending →
  **group by that column** (equal values banded) → nothing. He asked for exactly
  this cycle.
- **Selection carries across tabs** — pick something on one tab and the matching
  row highlights on the others.
- **Clickable regions must hit-test geometrically.** In SVG do **not** rely on
  masked rects for clicks — a full-canvas rect with a mask still swallows every
  click. Map the click point into the drawing's coordinates and test the shapes.
- Draw the **universe / outer boundary explicitly** (a dashed box) so an
  "outside" region is visibly clickable before it is selected.
- Label placement: put a vertex's label **outside** the shape on the side away
  from the centre, so labels never cross an edge. Set labels (A, B, C) fan
  **outward** from the centroid.

## 5. Engineering

- **One self-contained file.** A single `.py` for PyQt (with a PyQt6→PyQt5
  compat shim); a single self-contained `.html` (inline CSS + JS, no CDN, no
  build chain) for web. No dependencies beyond PyQt.
- **Generate, don't retype.** Build every table from the underlying data in
  code. If you also ship an HTML twin, generate the HTML *from the same data
  functions* so the two can never disagree.
- **Exact arithmetic in the data layer**; formatting only at the edges.
- **SVG hygiene**: use `clipPath` (with `clip-rule="evenodd"` for
  "box-minus-circle"), **not** `mask` — masks render inconsistently on mobile.
  **Namespace every SVG id per block** (`v2c0`, `v3c0`) — two diagrams in one
  document with the same ids silently resolve to the first, which cost a whole
  debugging cycle.
- **Responsive**: below ~820 px stack the panels, let wide tables scroll
  horizontally, scroll the tab strips, enlarge tap targets.
- Do not put `[cite:...]` markers in any file you generate.

## 6. Process

- **Act, don't narrate.** Build it, render it, look at it, then say what you did.
- **Verify by rendering, not by reasoning.** Render the PyQt widget offscreen
  (`QT_QPA_PLATFORM=offscreen`) and *look* at it; render the HTML with headless
  Chromium and *look* at it. For anything numeric (hit-tests, sort order, exact
  values) check it in code and print the result.
- **Test every state**, not just the default: each selection, each variable
  count, each sort direction. He asked "run all the cases yourself" once.
- **Screenshots he sends may be stale.** Check the file before "fixing" a thing
  that is already fixed, and say so plainly if it is.
- Keep replies short and concrete. He is terse; match it. No postamble after
  delivering a file.
- When you make a mistake, own it in one line and fix it. Do not grovel.

## 7. Deliverable conventions

- PyQt app: one `.py` he can `python3 app.py` with no arguments.
- HTML: one `.html` that opens by double-click; the same page must work at
  phone width.
- Name files plainly (`studio.html`, `LogicGatesStudio.py`); re-save the same
  name for a new version rather than inventing `_v2`.
- When the work is for a repo, push it and give him the commit link; when a page
  is the landing page, say which URL serves what.
