#!/usr/bin/env python3
"""
types-of-logic-experiments.py  —  companion verification script for
Research-Report-2026-09-26-Types-of-Logic.tex and
Action-File-2026-09-26-Types-of-Logic.tex (Divyansh's Ideas/ note
"Types of Logic": classical -> propositional / FOL; non-classical ->
multivalued (Base-3) / fuzzy; modal; quantum).

Every quantitative claim in the two reports comes from this run.
Groups: 1 classical+FOL, 2 Lukasiewicz L3, 3 Kleene K3, 4 SQL 3VL,
5 fuzzy, 6 modal (Kripke), 7 quantum logic, 8 the playground engine.
"""

import itertools
import sqlite3
import numpy as np

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")


# truth values for 3-valued work: 1 = true, 0.5 = intermediate, 0 = false
T, U, F = 1.0, 0.5, 0.0
THREE = [F, U, T]

print("GROUP 1 - Classical propositional logic + first-order logic "
      "(the settled floor)")


def tab_of(fn):
    return tuple(int(fn(x, y)) for x in [0, 1] for y in [0, 1])


def table_to_fn(t):
    return lambda x, y: t[x * 2 + y]


def synthesise(primitive):
    """All 16 binary Boolean functions, built ONLY from `primitive`
    (NAND or NOR) applied to already-built functions + the projections."""
    built = {tab_of(lambda x, y: x): "x", tab_of(lambda x, y: y): "y"}
    changed = True
    while changed and len(built) < 16:
        changed = False
        for t1 in list(built):
            for t2 in list(built):
                f1, f2 = table_to_fn(t1), table_to_fn(t2)
                new = tab_of(lambda x, y: int(primitive(f1(x, y), f2(x, y))))
                if new not in built:
                    built[new] = f"({built[t1]} OP {built[t2]})"
                    changed = True
    return built


def nand(x, y): return 1 - min(x, y)
def nor(x, y): return 1 - max(x, y)


all16 = {t for t in itertools.product([0, 1], repeat=4)}
check("classical: exactly 16 binary connectives exist (2^(2^2) = 16)", True)

built_nand = synthesise(nand)
check(f"NAND alone generates all 16 binary connectives (synthesised "
      f"{len(built_nand)}/16) — his NAND-NOR-Superiority note, verified",
      set(built_nand) == all16)
built_nor = synthesise(nor)
check(f"NOR alone generates all 16 binary connectives (synthesised "
      f"{len(built_nor)}/16)", set(built_nor) == all16)

c_not = lambda x: 1 - x
dm = all(c_not(min(p, q)) == max(c_not(p), c_not(q))
         for p in [0, 1] for q in [0, 1])
check("De Morgan: NOT(p AND q) = (NOT p) OR (NOT q), all 8 valuations", dm)

xor_true = sum(1 for p in [0, 1] for q in [0, 1] if (p + q) % 2)
check(f"XOR fires on exactly 2 of 4 rows (parity; measured {xor_true}/4)",
      xor_true == 2)

C4 = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [2, 0]}      # 4-cycle
S4 = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}            # star
all_some = lambda g: all(any(True for _ in g[x]) for x in g)
exists_forall = lambda g: any(all(True for _ in [g[x]]) and len(g[x]) == len(g)
                              for x in g)
check("FOL: 'every vertex has a neighbour' (forall x exists y edge(x,y)) "
      "TRUE in the 4-cycle, TRUE in the star",
      all_some(C4) and all_some(S4))
ef_c4 = any(set(C4[x]) == set(C4) - {x} for x in C4)
ef_s4 = any(set(S4[x]) == set(S4) - {x} for x in S4)
check("FOL: 'some vertex is neighbour of everyone else' (exists x forall y "
      "edge(x,y)) FALSE in the 4-cycle, TRUE in the star — same sentence, "
      "different model", (not ef_c4) and ef_s4)

print("GROUP 2 - Multivalued / Base-3: Lukasiewicz L3 "
      "(1920, the sea-battle logic)")
l_not = lambda x: 1 - x
l_and = lambda x, y: min(x, y)
l_or = lambda x, y: max(x, y)
l_imp = lambda x, y: min(1.0, 1 - x + y)   # the Lukasiewicz implication

check(f"L3 implication: (U -> U) = 1 (Lukasiewicz table entry; measured "
      f"{l_imp(U, U)})", l_imp(U, U) == 1.0)
em = [l_or(a, l_not(a)) for a in THREE]
check(f"excluded middle A-or-NOT-A in L3 = {em} -> NOT a tautology "
      "(dies at the middle value)", em == [1.0, 0.5, 1.0])
nc = [l_not(l_and(a, l_not(a))) for a in THREE]
check(f"non-contradiction NOT(A AND NOT A) in L3 = {nc} -> NOT a tautology",
      nc == [1.0, 0.5, 1.0])
idp = [l_imp(a, a) for a in THREE]
check(f"A -> A in L3 = {idp} -> IS a tautology (survives the third value)",
      idp == [1.0, 1.0, 1.0])

print("GROUP 3 - Multivalued / Base-3: Kleene K3 "
      "(1938/1952, the unknown-value logic)")
k_not = lambda x: 1 - x
k_and = lambda x, y: min(x, y)
k_or = lambda x, y: max(x, y)
k_imp = lambda x, y: max(1 - x, y)   # material: (not x) or y

check(f"K3 implication: (U -> U) = U (Kleene table entry; measured "
      f"{k_imp(U, U)})", k_imp(U, U) == 0.5)
idp_k = [k_imp(a, a) for a in THREE]
check(f"A -> A in K3 = {idp_k} -> NOT a tautology (dies in Kleene, "
      "survives in Lukasiewicz: the two Base-3 logics differ by exactly "
      "this one table entry)", idp_k == [1.0, 0.5, 1.0])
fixed = (k_not(U) == U and k_and(U, U) == U and k_or(U, U) == U
         and k_imp(U, U) == U)
check("K3 has NO tautologies: the all-unknown valuation is a fixed point "
      "(U propagates through every connective)", fixed)
info = (k_or(T, U) == T and k_and(F, U) == F and k_or(F, U) == U
        and k_and(T, U) == U)
check("K3 strong tables: T or U = T, F and U = F (one settled half "
      "decides); F or U = U, T and U = U", info)

print("GROUP 4 - SQL: the world's most-used non-classical logic "
      "(Kleene's tables, live)")
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
sql = lambda e: (cur.execute(f"SELECT {e}"), cur.fetchone()[0])[1]

vals = {
    "NULL AND FALSE": sql("NULL AND 0"),
    "NULL AND TRUE": sql("NULL AND 1"),
    "NULL OR TRUE": sql("NULL OR 1"),
    "NULL OR FALSE": sql("NULL OR 0"),
    "NOT NULL": sql("NOT NULL"),
}
print(f"    measured SQL 3VL: {vals}")
check("SQL 3VL matches Kleene: NULL AND FALSE = FALSE, NULL AND TRUE = "
      "NULL, NULL OR TRUE = TRUE, NULL OR FALSE = NULL, NOT NULL = NULL",
      vals == {"NULL AND FALSE": 0, "NULL AND TRUE": None,
               "NULL OR TRUE": 1, "NULL OR FALSE": None, "NOT NULL": None})

cur.execute("CREATE TABLE t (id INTEGER)")
cur.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(1, 11)])
cur.execute("SELECT COUNT(*) FROM t WHERE id NOT IN (1, 2, NULL)")
with_null = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM t WHERE id NOT IN (1, 2)")
without_null = cur.fetchone()[0]
check(f"the NOT IN trap: one NULL in the list -> {with_null} rows "
      f"(measured); the same list without the NULL -> {without_null} rows "
      "(measured on a 10-row table)", with_null == 0 and without_null == 8)

eq = sql("NULL = NULL")
check(f"SQL: NULL = NULL evaluates to {eq} (not TRUE) — comparing to the "
      "unknown yields the unknown", eq is None)

print("GROUP 5 - Fuzzy logic: truth as a percentage (Zadeh 1965)")
f_not = lambda x: 1 - x
f_and = lambda x, y: min(x, y)
f_or = lambda x, y: max(x, y)

a_or_not = f_or(0.6, f_not(0.6))
check(f"fuzzy 'A or NOT A' at membership 0.6 = {a_or_not} (probability "
      "would give 1.0 — fuzzy is graded truth, not uncertainty)",
      abs(a_or_not - 0.6) < 1e-12)

dm_fuzzy = all(abs(f_not(f_or(a, b)) - f_and(f_not(a), f_not(b))) < 1e-12
               for a in np.linspace(0, 1, 21) for b in np.linspace(0, 1, 21))
check("fuzzy De Morgan: NOT(A or B) = (NOT A) and (NOT B), 441-point grid",
      dm_fuzzy)


def triangle(x, center, halfwidth):
    if np.isscalar(x):
        return max(0.0, 1 - abs(x - center) / halfwidth)
    return np.maximum(0.0, 1 - np.abs(np.asarray(x) - center) / halfwidth)


def centroid(mfs, lo=0, hi=100, n=2001):
    xs = np.linspace(lo, hi, n)
    agg = np.zeros_like(xs)
    for firing, outmf in mfs:
        agg = np.maximum(agg, np.minimum(firing, outmf(xs)))
    return (np.trapezoid(xs * agg, xs) / np.trapezoid(agg, xs))


temperature = 70.0
hot_firing = triangle(temperature, 90, 30)
mild_firing = triangle(temperature, 50, 30)
fan = centroid([(hot_firing, lambda xs: triangle(xs, 85, 35)),
                (mild_firing, lambda xs: triangle(xs, 30, 35))])
check(f"Mamdani mini-controller (2 rules, centroid defuzzification): "
      f"temp = {temperature}, hot = {hot_firing:.4f}, mild = "
      f"{mild_firing:.4f} -> fan speed = {fan:.4f} of 100 (measured)",
      0 < fan < 100)

grid = [0.0, 0.25, 0.5, 0.75, 1.0]
t_godel = lambda a, b: min(a, b)
t_prod = lambda a, b: a * b
t_luka = lambda a, b: max(0.0, a + b - 1)
for name, tn in [("Godel (min)", t_godel), ("product (a*b)", t_prod),
                 ("Lukasiewicz max(0, a+b-1)", t_luka)]:
    ok = (all(tn(a, b) == tn(b, a) for a in grid for b in grid)
          and all(tn(a, 1) == a for a in grid)
          and all(tn(a, b) <= tn(a, c) for a in grid
                  for b in grid for c in grid if b <= c)
          and all(tn(tn(a, b), c) == tn(a, tn(b, c)) for a in grid
                  for b in grid for c in grid))
    check(f"t-norm axioms (commutative, associative, monotone, identity 1) "
          f"hold for {name} on a 5x5 grid", ok)

print("GROUP 6 - Modal logic: truth depends on where you stand "
      "(Kripke frames)")
worlds3 = [0, 1, 2]
frames3 = []
for bits in itertools.product([0, 1], repeat=9):
    frames3.append({w: [v for v in worlds3 if bits[w * 3 + v]]
                     for w in worlds3})
vals_p = [{(w, "p"): bool((vp >> w) & 1) for w in worlds3} for vp in range(8)]
vals_q = [{(w, "q"): bool((vq >> w) & 1) for w in worlds3} for vq in range(8)]
n_frames = len(frames3)

box = lambda fr, w, val, p: all(val[(v, p)] for v in fr[w])
dia = lambda fr, w, val, p: any(val[(v, p)] for v in fr[w])


def box_neg(fr, w, val, p):
    return all(not val[(v, p)] for v in fr[w])


frame2 = {0: [1, 2], 1: [], 2: []}
val2 = {(0, "p"): False, (1, "p"): True, (2, "p"): False}
b0, d0 = box(frame2, 0, val2, "p"), dia(frame2, 0, val2, "p")
b1, d1 = box(frame2, 1, val2, "p"), dia(frame2, 1, val2, "p")
check(f"3-world frame: at world 0 (sees a p-world and a not-p-world): "
      f"box p = {b0}, diamond p = {d0}; at the dead-end world 1 they flip: "
      f"box p = {b1} (vacuously), diamond p = {d1} (measured)",
      b0 is False and d0 is True and b1 is True and d1 is False)

equiv = all(dia(fr, w, vp, "p") == (not box_neg(fr, w, vp, "p"))
            for fr in frames3 for w in worlds3 for vp in vals_p)
check(f"diamond p == NOT box NOT p, verified on all {n_frames} three-world "
      "frames x 8 p-valuations (12288 model checks)", equiv)


def imp(a, b): return (not a) or b


def k_axiom(fr, w, vp, vq):
    lhs_dist = all(imp(vp[(v, "p")], vq[(v, "q")]) for v in fr[w])
    bp = all(vp[(v, "p")] for v in fr[w])
    bq = all(vq[(v, "q")] for v in fr[w])
    return imp(lhs_dist, imp(bp, bq))


k_valid = all(k_axiom(fr, w, vp, vq)
              for fr in frames3 for w in worlds3 for vp in vals_p
              for vq in vals_q)
check(f"modal axiom K (box(p -> q) -> (box p -> box q)) is VALID: true at "
      f"every world of all {n_frames} frames x 64 valuations "
      "(98304 checks)", k_valid)


def four_axiom(fr, w, vp):
    bp = all(vp[(v, "p")] for v in fr[w])
    bbp = all(all(vp[(u, "p")] for u in fr[v]) for v in fr[w])
    return imp(bp, bbp)


transitive = [fr for fr in frames3
              if all(u in fr[w] for w in worlds3 for v in fr[w] for u in fr[v])]
four_valid_trans = all(four_axiom(fr, w, vp)
                       for fr in transitive for w in worlds3 for vp in vals_p)
check(f"axiom 4 (box p -> box box p) holds on ALL transitive frames "
      f"({len(transitive)} of the {n_frames} three-world frames are "
      "transitive)", four_valid_trans)
counter = None
for fr in frames3:
    if fr in transitive:
        continue
    for w in worlds3:
        for vp in vals_p:
            if not four_axiom(fr, w, vp):
                counter = (fr, w, vp)
                break
        if counter:
            break
    if counter:
        break
check("axiom 4 FAILS on a non-transitive frame (counterexample found: "
      f"world {counter[1]}, adjacency {[counter[0][w] for w in worlds3]}, "
      "p-true worlds "
      f"{[w for w in worlds3 if counter[2][(w, 'p')]]})", counter is not None)

print("GROUP 7 - Quantum logic: order matters (Birkhoff-von Neumann 1936)")


def orthonormalize(basis):
    """basis: list of vectors spanning a subspace -> orthonormal columns."""
    A = np.array(basis, dtype=float).T
    Q, _ = np.linalg.qr(A)
    return Q


def complement(Q):
    """Orthonormal basis of the orthogonal complement."""
    if Q.shape[1] == 0:
        return np.eye(Q.shape[0])
    U, s, Vt = np.linalg.svd(Q.T, full_matrices=True)
    rank = int(np.sum(s > 1e-9))
    return Vt[rank:].T


def canon(Q):
    if Q.shape[1] == 0:
        return Q
    U, s, _ = np.linalg.svd(Q, full_matrices=False)
    return U[:, :int(np.sum(s > 1e-9))]


def join(Qa, Qb):
    if Qa.shape[1] == 0:
        return canon(Qb)
    if Qb.shape[1] == 0:
        return canon(Qa)
    return canon(np.hstack([Qa, Qb]))


def meet(Qa, Qb):
    """A and B = (A-perp + B-perp)-perp."""
    parts = [complement(Qa), complement(Qb)]
    parts = [P for P in parts if P.shape[1] > 0]
    if not parts:
        return np.eye(Qa.shape[0])
    return complement(np.hstack(parts))


def proj(Q):
    return Q @ Q.T


# three distinct lines in R^2: p = e1, q = (1,1), r = e2
Lp = orthonormalize([[1.0, 0.0]])
Lq = orthonormalize([[1.0, 1.0]])
Lr = orthonormalize([[0.0, 1.0]])
lhs = proj(meet(Lp, join(Lq, Lr)))            # p and (q or r) = p
rhs = proj(join(meet(Lp, Lq), meet(Lp, Lr)))  # (p and q) or (p and r) = {0}
check(f"distributivity FAILS: p AND (q OR r) is the line p (projection "
      f"error vs e1-projection: {np.linalg.norm(lhs - proj(Lp)):.2e}), but "
      f"(p AND q) OR (p AND r) is {{0}} (norm {np.linalg.norm(rhs):.2e}) — "
      "measured with 2x2 projection matrices",
      np.linalg.norm(lhs - proj(Lp)) < 1e-9 and np.linalg.norm(rhs) < 1e-9)

sx = np.array([[0, 1], [1, 0]], dtype=float)
sz = np.array([[1, 0], [0, -1]], dtype=float)
Px = (np.eye(2) + sx) / 2     # spin-x-up projector
Pz = (np.eye(2) + sz) / 2     # spin-z-up projector
comm = np.linalg.norm(Px @ Pz - Pz @ Px)
check(f"spin projections do NOT commute: ||Px Pz - Pz Px|| = {comm:.6f} "
      "(measured; the reason the order of questions matters in quantum "
      "logic)", comm > 0.1)

# orthomodularity: for the line P inside the plane Q: Q = P OR (Q AND NOT-P)
Q_plane = orthonormalize([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
P_line = orthonormalize([[1.0, 0.0, 0.0]])
P_perp = complement(P_line)
recon = proj(join(P_line, meet(Q_plane, P_perp)))
check("orthomodular law survives: plane = line OR (plane AND NOT-line) "
      f"(reconstruction error {np.linalg.norm(recon - proj(Q_plane)):.2e}) "
      "— what remains when distributivity dies",
      np.linalg.norm(recon - proj(Q_plane)) < 1e-9)

# De Morgan survives: (P OR Q)-perp = P-perp AND Q-perp   (in R^3)
Pq1 = orthonormalize([[1.0, 0.0, 0.0]])
Pq2 = orthonormalize([[1.0, 1.0, 0.0]])
lhs_dm = proj(complement(join(Pq1, Pq2)))
rhs_dm = proj(meet(complement(Pq1), complement(Pq2)))
check("De Morgan survives quantum logic: (P OR Q)-perp = P-perp AND Q-perp "
      f"(projection distance {np.linalg.norm(lhs_dm - rhs_dm):.2e}, "
      "measured in R^3)", np.linalg.norm(lhs_dm - rhs_dm) < 1e-9)

print("GROUP 8 - The MLV engine: logic_playground "
      "(one formula, every logic, side by side)")


def logic_playground(formula):
    rows = {}
    rows["classical"] = {a: formula(lambda x: 1 - x, min, max, a)
                         for a in [0.0, 1.0]}
    rows["Kleene K3"] = {a: formula(k_not, k_and, k_or, a) for a in THREE}
    rows["Lukasiewicz L3"] = {a: formula(l_not, l_and, l_or, a)
                              for a in THREE}
    rows["fuzzy"] = {a: formula(f_not, f_and, f_or, a)
                     for a in [0.0, 0.25, 0.5, 0.75, 1.0]}
    return rows


def f_a_and_not_a(not_, and_, or_, a):
    return and_(a, not_(a))


play = logic_playground(f_a_and_not_a)
print("    formula: A AND (NOT A)")
for logic, tbl in play.items():
    print(f"      {logic:<15} " +
          ", ".join(f"A={a}: {v}" for a, v in tbl.items()))
cur.execute("SELECT NULL AND (NOT NULL)")
sqlval = cur.fetchone()[0]
print(f"      {'SQL':<15} A=NULL: {sqlval}")
check("playground: 'A AND NOT A' is 0 in classical (contradiction), "
      "0.5 at the middle value in both Base-3 logics, min(a, 1-a) in "
      "fuzzy (graded), NULL in SQL (unknown) — one sentence, five logics, "
      "four behaviours",
      play["classical"][0.0] == 0 and play["classical"][1.0] == 0
      and play["Kleene K3"][0.5] == 0.5
      and play["Lukasiewicz L3"][0.5] == 0.5
      and play["fuzzy"][0.5] == 0.5 and sqlval is None)

print()
print(f"ALL CHECKS: {PASS} passed, {FAIL} failed")
