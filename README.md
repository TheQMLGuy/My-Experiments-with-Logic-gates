# My Experiments with Logic Gates

An interactive lab for the journey from a single NAND gate to the many logics
truth can travel on — classical, three-valued (Kleene and Łukasiewicz), SQL's
NULL logic, fuzzy, modal and quantum. One sentence, run under every logic, side
by side.

**Live site:** https://theqmlguy.github.io/My-Experiments-with-Logic-gates/

---

## What this is

It began with a handwritten tree. *Classical logic* at the top (propositional
AND / OR / NOT, then first-order logic with quantifiers), *non-classical logic*
below it (multivalued base-3, fuzzy between 0 and 1), and beneath those *modal
logic* (“what could be”) and *quantum logic*. One question ran through all of
it: **if truth is not a clean yes / no, which rulebook still holds?**

This lab is that question in tool form. Everything on the page is computed live
in the browser — nothing is quoted. The same definitions are checked by the
companion script in `experiments/`.

## The experiments

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

## Layout

```
index.html      the page (structure and copy)
styles.css      styling
app.js          the whole engine — parser, multi-logic evaluator, and every demo
assets/notes/   the original handwritten notes (scans)
data/           boolean_2var.csv, boolean_3var.csv — the classifications, generated
experiments/    types-of-logic-experiments.py — the companion verification script
```

No build chain, no server, no dependencies. Open `index.html` directly, or serve
the folder:

```
python3 -m http.server
```

## Verified, not asserted

The companion script `experiments/types-of-logic-experiments.py` runs 34 checks
across eight groups (classical + FOL, Łukasiewicz Ł₃, Kleene K₃, SQL 3VL, fuzzy,
modal, quantum, and the multi-logic playground). Run it with:

```
python3 experiments/types-of-logic-experiments.py
```

The browser engine reproduces the same results: NAND and NOR each synthesise all
16 binary connectives; A → A is not a tautology in K₃ but is in Ł₃ (the two
base-3 logics differ by exactly that one table entry); one NULL in a `NOT IN`
list returns 0 rows instead of 8; quantum distributivity fails while orthomodular
law and De Morgan survive; and the two-variable classification yields 6 monotone,
8 affine, 4 linear, 4 self-dual functions in 4 NPN classes (the three-variable
one yields 20 monotone and 14 NPN classes).

## Sources

The primary sources are the original handwritten notes reproduced in
`assets/notes/` — the *Types of Logic* tree, the *NAND NOR Superiority* page, and
*DFA and Logic Gates*. The background literature the report draws on includes
Łukasiewicz (1920), Kleene (1938/1952), Zadeh (1965), Mamdani & Assilian (1974),
Kripke (1959/1963), and Birkhoff & von Neumann (1936).

---

Built by Divyansh · TheQMLGuy. An understanding artifact first.
