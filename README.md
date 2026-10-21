# Logic Studio

An interactive explorer for two-variable Boolean functions — the 16 of them, in
every representation, with the 2×2 matrix invariants of each and a full
synthesis of all 16 inside each of the 17 minimal complete bases.

A single self-contained page. No build chain, no dependencies, no server.

**Live:** https://theqmlguy.github.io/My-Experiments-with-Logic-gates/

---

## Representation

- a **variable bar** — `a`, `not a`, `b`, `not b`, and `c`, `not c` at
  three variables — with
  multi-select; the highlight is the intersection of whatever is ticked;
- three **linked diagrams** — **Venn**, **cube (hypercube)** and **tree
  (lattice)** — that cross-highlight in both directions. Click a literal, a Venn
  region, a cube vertex or a tree node and the same minterm lights up in all
  three, plus the matching row of the tables;
- a **2 / 3 variables** toggle. At three variables the Venn is three circles
  giving eight regions, the cube is the eight-vertex cube with its six facet
  labels, and the tree is the B₃ lattice.

Each Venn region is individually clickable — clicks are hit-tested against the
circles, so the four (or eight) atoms select exactly, and the universe is drawn
as an explicit dashed boundary so the outside region is visible before it is
selected.

## Tables

Three sub-tables:

- **representations** — the 16 functions with columns: symbol, expression,
  matrix, det, trace, eigenvalues, rank, code, SOP, ANF, Walsh, set, NPN. Each
  function has its own symbol — `∧ ∨ ⊕ ⊙ ↑ ↓ ⊤ ⊥` for the named ones, and
  `a ∧ not b`, `not a ∧ b`, `a ∨ not b`, `not a ∨ b` for the four mixed ones —
  while the four literals keep their letters (`a`, `not a`, `b`, `not b`). The *expression*
  column writes each function from `a`, `not a`, `b`, `not b`, with the formal
  name on a second line inside the cell — but only where the name is a distinct
  connective name, so `a ∧ b` over `(AND)` and `not a ∧ not b` over `(NOR)`,
  while the projections stay single-line (`a`, `not a`, `b`, `not b`);
- **matrix** — the 2×2 matrix of each function, drawn as a bracketed 2×2, with
  weight, det, trace, characteristic polynomial, eigenvalues, rank, rank over
  GF(2), det over GF(2), class (idempotent / nilpotent / involution), MᵀM,
  singular values, inverse, and Frobenius norm;
- **universal** — the **16 functions written inside each of the 17 minimal
  complete bases**. Rows are the 16 functions, columns the 17 bases; each cell is
  the shortest expression for that function using only that base's connectives,
  found by breadth-first search and written in words — e.g. in the `AND + NOT`
  base, `OR` reads `not(not a and not b)`, and in the `NAND` base it reads
  `(a nand (a nand a)) nand (b nand (b nand b))`.

## Properties

The five Post properties (T₀, T₁, M, D, L) for all 16 functions; the 17 minimal
bases; and a live functional-completeness checker — tick any set of connectives
and it reports whether they are complete, or which class they are trapped in.

## Conventions

Every column header cycles on click: nothing → sort ascending → sort descending
→ **group by that column** (equal values banded) → nothing.

Values are **exact, never rounded**. The golden-ratio eigenvalues print as
`(1+√5)/2, (1−√5)/2`, never `1.62`; the Frobenius norms print as `√2`, `√3`,
never decimals. The two functions with characteristic polynomial `λ² − λ − 1`
are exactly the two whose largest singular value is φ.

Negation is written as the word **`not`** — `not a`, `a ∧ not b`, `not(not a and
not b)` — not a bar over the letter and not an inverted token. The layout is
responsive down to phone width: the diagram panels stack and wide tables scroll
horizontally.

## Files

```
index.html    the studio (landing page)
studio.html   the same page, at its own path
```

Open `index.html` directly, or serve the folder:

```
python3 -m http.server
```

---

Built by Divyansh · TheQMLGuy. An understanding artifact first.
