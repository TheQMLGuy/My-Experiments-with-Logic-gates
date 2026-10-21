# My Experiments with Logic Gates

Two interactive pages live here.

**The Logic Studio** — the landing page. A 2- and 3-variable Boolean explorer:
the 16 two-variable functions in every representation, the 2×2 matrix invariants
of each, and the 17 minimal covers.

**Logic Lab** — the long-form lab. One sentence, run under classical logic,
Kleene K₃, Łukasiewicz Ł₃, SQL's NULL logic, fuzzy, modal and quantum logic,
side by side.

**Live:**
- Studio — https://theqmlguy.github.io/My-Experiments-with-Logic-gates/
- Logic Lab — https://theqmlguy.github.io/My-Experiments-with-Logic-gates/logic-lab.html

---

## 1. The Logic Studio — `index.html` (also at `studio.html`)

A single self-contained page, no dependencies. Two variable counts, base 2.

### Representation tab

- a **variable bar** — `a ¬a b ¬b` (plus `c ¬c` at three variables) — with
  multi-select; the highlight is the intersection of whatever is ticked;
- three **linked diagrams** — **Venn**, **cube (hypercube)** and **tree
  (lattice)** — that cross-highlight in both directions. Click a literal, a Venn
  region, a cube vertex or a tree node, and the same minterm lights up in all
  three, plus the matching row of the tables. Clicking a Venn region hit-tests
  the circles, so each of the four (or eight) atoms is individually selectable;
- a **2 / 3 variables** toggle. At three variables the Venn is three circles
  giving eight regions, the cube is the eight-vertex cube with six facet labels,
  and the tree is the B₃ lattice.

### Tables tab — three sub-tables

- **representations** — the 16 functions with columns: expression, matrix, det,
  trace, eigenvalues, rank, code, SOP, ANF, Walsh, set, NPN. The *expression*
  column writes each function from `a / ¬a / b / ¬b` with its formal name in
  brackets — e.g. `a ∧ b (AND)`, `(a ∧ b̄) ∨ (ā ∧ b) (XOR)`;
- **matrix** — the 2×2 matrix of each function (drawn as a bracketed 2×2), with
  weight, det, trace, characteristic polynomial, eigenvalues, rank, rank over
  GF(2), det over GF(2), class (idempotent / nilpotent / involution), MᵀM,
  singular values, inverse, and Frobenius norm;
- **universal** — the **17 minimal complete bases as columns**, the connectives
  as rows, membership shown as filled cells (no ticks), split into two blocks.

### Properties tab

The five Post properties (T₀, T₁, M, D, L) for all 16 functions; the 17 minimal
bases; and a live functional-completeness checker — tick any set of connectives
and it reports whether they are complete, or which class they are trapped in.

### Conventions

Every column header cycles on click: nothing → sort ascending → sort descending
→ **group by that column** → nothing. Values are **exact, never rounded** — the
golden-ratio eigenvalues print as `(1+√5)/2, (1−√5)/2`, never `1.62`, and the
Frobenius norms print as `√2`, `√3`, never decimals. Negation is drawn as white
text on black, not a bar. The layout is responsive down to phone width.

## 2. Logic Lab — `logic-lab.html`

It began with a handwritten tree. *Classical logic* at the top (propositional
AND / OR / NOT, then first-order logic with quantifiers), *non-classical logic*
below it (multivalued base-3, fuzzy between 0 and 1), and beneath those *modal
logic* ("what could be") and *quantum logic*. One question ran through all of
it: **if truth is not a clean yes / no, which rulebook still holds?**

Everything on the page is computed live in the browser — nothing is quoted. The
same definitions are checked by the companion script in `experiments/`.

### The experiments

| # | Experiment | What it shows |
|---|------------|----------------|
| 1 | **Gate lab** | The 16 binary connectives; toggle A and B, or write your own sentence. |
| 2 | **Why NAND & NOR are universal** | Build NOT, AND, OR from one gate — and synthesise all 16 connectives from NAND alone (16 / 16). |
| 3 | **One sentence, five logics** | The same sentence under classical, Kleene K₃, Łukasiewicz Ł₃, fuzzy and SQL, plus a live law-survival matrix (excluded middle, non-contradiction, identity, De Morgan). |
| 4 | **SQL: the most-used non-classical logic** | Kleene's three values wearing a `WHERE` clause — and the `NOT IN` trap that turns 8 rows into 0. |
| 5 | **Fuzzy logic** | Truth as a percentage: membership sliders, and a two-rule Mamdani fan controller. |
| 6 | **Modal logic** | Kripke frames: □p and ◇p, and the dead-end flip. |
| 7 | **Quantum logic** | Three lines in the plane; distributivity fails, measured with real 2×2 projection matrices. |
| 8 | **Every Boolean function, classified** | All 16 two-variable and 256 three-variable functions, sorted by linear / affine / monotone / self-dual / symmetric / NPN class. |
| 9 | **From a DFA to a circuit of gates** | A two-state machine over {a, b} reduced to a single NOT gate and a flip-flop. |
| — | **The trail** | The primary sources: the handwritten notes and the verification script. |

## Layout

```
index.html        the Logic Studio (landing page)
studio.html       the same studio, at its own path
logic-lab.html    the long-form lab (the nine experiments above)
styles.css        styling for the lab
app.js            the lab's engine — parser, multi-logic evaluator, every demo
assets/notes/     the original handwritten notes (scans)
data/             boolean_2var.csv, boolean_3var.csv — classifications, generated
experiments/      types-of-logic-experiments.py — the companion verification script
```

No build chain, no server, no dependencies. Open `index.html` directly, or serve
the folder:

```
python3 -m http.server
```

## Verified, not asserted

The companion script `experiments/types-of-logic-experiments.py` runs **34
checks across eight groups** (classical + FOL, Łukasiewicz Ł₃, Kleene K₃, SQL
3VL, fuzzy, modal, quantum, and the multi-logic playground). Run it with:

```
python3 experiments/types-of-logic-experiments.py
```

Last run: **34 passed, 0 failed.** The browser engine reproduces the same
results: NAND and NOR each synthesise all 16 binary connectives; A → A is not a
tautology in K₃ but is in Ł₃ (the two base-3 logics differ by exactly that one
table entry); one NULL in a `NOT IN` list returns 0 rows instead of 8; quantum
distributivity fails while the orthomodular law and De Morgan survive; and the
two-variable classification yields 6 monotone, 8 affine, 4 linear, 4 self-dual
functions in 4 NPN classes (the three-variable one yields 20 monotone and 14 NPN
classes).

## Sources

The primary sources are the original handwritten notes reproduced in
`assets/notes/` — the *Types of Logic* tree, the *NAND NOR Superiority* page, and
*DFA and Logic Gates*. The background literature the report draws on includes
Łukasiewicz (1920), Kleene (1938/1952), Zadeh (1965), Mamdani & Assilian (1974),
Kripke (1959/1963), and Birkhoff & von Neumann (1936).

---

Built by Divyansh · TheQMLGuy. An understanding artifact first.
