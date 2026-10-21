#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logic Gates Studio
==================

A single-file desktop application for Divyansh's *Logic* project -- the body of
work on logic and logic gates built from the ground up.  It gathers the whole
project into one interactive program:

  * Gates & Truth Tables .... the 16 two-input Boolean functions, their symbols,
                              truth tables, canonical SOP, ANF (GF(2) polynomial)
                              and set expressions.
  * Hypercube ............... Q_n drawn as a graph; vertices are minterms, edges
                              are single-bit flips; the Gray-code tour is shown.
  * Venn Diagrams .......... n-set Venn diagrams whose regions are the minterms,
                              built with real region geometry, plus the universe.
  * The 16 Functions ....... every function through the twelve representations,
                              the set dictionary, and the NPN symmetry classes.
  * Completeness ........... Post's theorem checked live on any chosen gate set,
                              and the 17 minimal bases (computed, not quoted).

Agent-owned exposition of Divyansh's ideas; the ideas and the direction are his.

Requires PyQt6  ->  pip install PyQt6
(Falls back to PyQt5 automatically if PyQt6 is not installed.)
"""

import sys
import math
import itertools

# ---------------------------------------------------------------------------
# Qt binding: prefer PyQt6, fall back to PyQt5, and normalise the enum names
# so that a single body of code runs on either.
# ---------------------------------------------------------------------------
try:
    from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, QSize, pyqtSignal
    from PyQt6.QtGui import (QPainter, QColor, QFont, QPen, QBrush, QPolygonF,
                             QPainterPath, QFontMetricsF, QLinearGradient, QAction,
                             QFontDatabase, QIcon, QPixmap, QPainterPathStroker,
                             QTransform, QTextDocument)
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
        QHeaderView, QGridLayout, QGroupBox, QSpinBox, QTextEdit, QListWidget,
        QListWidgetItem, QSplitter, QFrame, QScrollArea, QSizePolicy, QRadioButton,
        QButtonGroup, QSlider, QLineEdit, QFormLayout, QAbstractItemView,
        QToolButton, QStackedWidget, QMessageBox, QStyledItemDelegate,
        QStyle, QStyleOptionComboBox, QTabBar, QStylePainter,
        QStyleOptionTab)
    QT6 = True
except ImportError:  # pragma: no cover - exercised only on a PyQt5 machine
    from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, QSize, pyqtSignal
    from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QBrush, QPolygonF,
                             QPainterPath, QFontMetricsF, QLinearGradient,
                             QFontDatabase, QIcon, QPixmap, QTransform,
                             QTextDocument)
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
        QHeaderView, QGridLayout, QGroupBox, QSpinBox, QTextEdit, QListWidget,
        QListWidgetItem, QSplitter, QFrame, QScrollArea, QSizePolicy, QRadioButton,
        QButtonGroup, QSlider, QLineEdit, QFormLayout, QAbstractItemView,
        QToolButton, QStackedWidget, QMessageBox, QAction,
        QStyledItemDelegate, QStyle, QStyleOptionComboBox, QTabBar,
        QStylePainter, QStyleOptionTab)
    QT6 = False
    for _n in ("AlignmentFlag", "PenStyle", "PenCapStyle", "PenJoinStyle",
               "BrushStyle", "FontWeight", "CheckState", "ItemDataRole",
               "GlobalColor", "WindowType", "TextFlag", "Orientation",
               "FocusPolicy", "ScrollBarPolicy", "ToolButtonStyle",
               "ContextMenuPolicy", "AspectRatioMode", "TransformationMode",
               "CursorShape", "Key"):
        try:
            setattr(Qt, _n, Qt)
        except Exception:
            pass
    QPainter.RenderHint = QPainter
    QFont.Weight = QFont
    QFontDatabase.SystemFont = QFontDatabase
    QHeaderView.ResizeMode = QHeaderView
    QAbstractItemView.SelectionMode = QAbstractItemView
    QAbstractItemView.SelectionBehavior = QAbstractItemView
    QAbstractItemView.EditTrigger = QAbstractItemView
    QMessageBox.Icon = QMessageBox


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
INK        = QColor("#1f1f1f")
MUTED      = QColor("#5a5a5a")
PANEL      = QColor("#f7f7f7")
PANEL_2    = QColor("#ececec")
BORDER     = QColor("#bdbdbd")
ACCENT     = QColor("#39587a")
ACCENT_2   = QColor("#6b7f96")
TRUE_COL   = QColor("#2f7d4f")
FALSE_COL  = QColor("#a2503f")
UNSURE_COL = QColor("#8a6d1e")
GRID       = QColor("#c4c4c4")
HL         = QColor("#e0a53a")
PRETTY     = QColor("#39587a")


# ===========================================================================
#  Core model -- the 16 two-input Boolean functions
# ===========================================================================
#
#  A function is stored as an index 0..15.  Bit i of the index is the output on
#  input row i, where row i encodes (A, B) as  A = (i >> 1) & 1,  B = i & 1.
#  So  i = 0 -> (0,0),  1 -> (0,1),  2 -> (1,0),  3 -> (1,1).
#
#  GATES maps each index to (name, symbol, set expression, plain reading).

GATES = {
    0:  ("FALSE", "0",        "\u2205",                  "nothing"),
    1:  ("NOR",   "A\u2193B", "A\u0304 \u2229 B\u0304",       "neither A nor B"),
    2:  ("B\u2212A", "A\u0304 \u2227 B", "B \u2212 A",     "B without A"),
    3:  ("NOT A", "A\u0304",  "A\u0304",                   "not A"),
    4:  ("A\u2212B", "A \u2227 B\u0304", "A \u2212 B",     "A without B"),
    5:  ("NOT B", "B\u0304",  "B\u0304",                   "not B"),
    6:  ("XOR",   "A \u2295 B", "A \u25b3 B",              "A and B differ"),
    7:  ("NAND",  "A \u2191 B", "A\u0304 \u222a B\u0304",      "A and B disjoint"),
    8:  ("AND",   "A \u2227 B", "A \u2229 B",              "A and B together"),
    9:  ("XNOR",  "A \u2194 B", "(A \u2229 B) \u222a (A\u0304 \u2229 B\u0304)", "A and B coincide"),
    10: ("B",     "B",        "B",                         "just B"),
    11: ("B \u2228 A\u0304", "B \u2228 A\u0304", "A\u0304 \u222a B",    "B, or not A"),
    12: ("A",     "A",        "A",                         "just A"),
    13: ("A \u2228 B\u0304", "A \u2228 B\u0304", "A \u222a B\u0304",    "A, or not B"),
    14: ("OR",    "A \u2228 B", "A \u222a B",              "A or B"),
    15: ("TRUE",  "1",        "U",                         "everything"),
}

# Which of the four corners of the 2x2 K-map each index lights up, and helpers.
LITERAL_A = "A\u0304"
LITERAL_B = "B\u0304"


def rows2(idx):
    """Return [(A, B, out), ...] for the four input rows of a 2-input function."""
    out = []
    for i in range(4):
        a = (i >> 1) & 1
        b = i & 1
        out.append((a, b, (idx >> i) & 1))
    return out


def bits2(idx):
    """f(0,0), f(0,1), f(1,0), f(1,1) as a list of 0/1."""
    return [(idx >> i) & 1 for i in range(4)]


def anf2(idx):
    """Algebraic normal form coefficients (c0, cA, cB, cAB) over GF(2)."""
    v0, v1, v2, v3 = bits2(idx)
    return (v0, v0 ^ v2, v0 ^ v1, v0 ^ v1 ^ v2 ^ v3)


def anf_string(idx):
    """The ANF as a GF(2) polynomial string, e.g. '1 \u2295 A \u2295 AB'."""
    c0, cA, cB, cAB = anf2(idx)
    terms = []
    if c0:
        terms.append("1")
    if cA:
        terms.append("A")
    if cB:
        terms.append("B")
    if cAB:
        terms.append("AB")
    return " \u2295 ".join(terms) if terms else "0"


def sop_string(idx):
    """Canonical sum-of-products string over the minterms."""
    terms = []
    for i in range(4):
        if (idx >> i) & 1:
            a = (i >> 1) & 1
            b = i & 1
            lit = ("A" if a else "A\u0304") + " \u2227 " + ("B" if b else "B\u0304")
            terms.append(lit)
    return " \u2228 ".join(terms) if terms else "0"


def minterms(idx):
    """Row indices (0..3) where the function is true."""
    return [i for i in range(4) if (idx >> i) & 1]


# ---- NPN (input-negation / permutation / output-negation) classes ----------
#  16 functions collapse to 4 classes under the group action.
NPN_CLASS = {}
for _i in range(16):
    if _i in (0, 15):
        NPN_CLASS[_i] = "constant"
    elif _i in (3, 5, 10, 12):
        NPN_CLASS[_i] = "projection"
    elif _i in (6, 9):
        NPN_CLASS[_i] = "XOR / XNOR"
    else:
        NPN_CLASS[_i] = "AND / NAND"


# ---- Post's maximal classes (for functional-completeness checking) ----------
def in_T0(idx):
    """Preserves 0:  f(0,0) = 0."""
    return ((idx >> 0) & 1) == 0


def in_T1(idx):
    """Preserves 1:  f(1,1) = 1."""
    return ((idx >> 3) & 1) == 1


def in_M(idx):
    """Monotone in both arguments."""
    v0, v1, v2, v3 = bits2(idx)          # v0=(0,0) v1=(0,1) v2=(1,0) v3=(1,1)
    return v0 <= v1 <= v3 and v0 <= v2 <= v3


def in_D(idx):
    """Self-dual:  f(a\u0304,b\u0304) = f\u0304(a,b)."""
    v0, v1, v2, v3 = bits2(idx)
    return v0 == (1 - v3) and v1 == (1 - v2)


def in_L(idx):
    """Affine over GF(2):  ANF has degree \u2264 1 (no AB term)."""
    return anf2(idx)[3] == 0


POST_CLASSES = [
    ("T0", "preserves 0", in_T0),
    ("T1", "preserves 1", in_T1),
    ("M",  "monotone",    in_M),
    ("D",  "self-dual",   in_D),
    ("L",  "affine over GF(2)", in_L),
]


def is_complete(idxs):
    """Post's criterion: a set is complete iff it escapes all five families.

    Returns (complete: bool, blocked_by: list of class names it fails to escape).
    """
    blocked = [name for (name, _d, fn) in POST_CLASSES
               if all(fn(i) for i in idxs)]
    return (len(blocked) == 0), blocked


# ---- The standard connective set, for the exact count of minimal bases ------
#
#  Counting "minimal functionally complete bases" only gives the familiar
#  answer once the universe of allowed connectives is fixed.  Over the standard
#  connective set below -- NOT, AND, OR, XOR, XNOR, NAND, NOR, B-or-not-A,
#  A-and-not-B, TRUE, FALSE -- the count comes out exactly 17: two singletons,
#  nine pairs, six triples, none larger.  This reproduces the notebook's claim.
#
#  Each entry is (arity, outputs).  For unary: outputs = (f(0), f(1)).
#  For binary: outputs = (f(0,0), f(0,1), f(1,0), f(1,1)).

def _u(a, b):
    return (1, (a, b))


def _b(o):
    return (2, tuple(o))


CONNECTIVES = {
    "NOT":   _u(1, 0),
    "AND":   _b((0, 0, 0, 1)),
    "OR":    _b((0, 1, 1, 1)),
    "XOR":   _b((0, 1, 1, 0)),
    "XNOR":  _b((1, 0, 0, 1)),
    "NAND":  _b((1, 1, 1, 0)),
    "NOR":   _b((1, 0, 0, 0)),
    "B \u2228 A\u0304": _b((1, 1, 0, 1)),
    "A \u2227 B\u0304": _b((0, 0, 1, 0)),
    "TRUE":  _u(1, 1),
    "FALSE": _u(0, 0),
}


def _conn_in(name, cls_fn):
    """Is connective `name` inside a Post class, given a class test on (arity,o)?"""
    arity, o = CONNECTIVES[name]
    if cls_fn == "T0":
        return o[0] == 0
    if cls_fn == "T1":
        return o[-1] == 1
    if cls_fn == "M":
        if arity == 1:
            return o[0] <= o[1]
        return o[0] <= o[1] <= o[3] and o[0] <= o[2] <= o[3]
    if cls_fn == "D":
        if arity == 1:
            return o[0] == 1 - o[1]
        return o[0] == 1 - o[3] and o[1] == 1 - o[2]
    if cls_fn == "L":
        if arity == 1:
            return True
        return (o[0] ^ o[1] ^ o[2] ^ o[3]) == 0
    raise ValueError(cls_fn)


def standard_complete(names):
    """Post's criterion over the standard connective universe."""
    blocked = [c for c in ("T0", "T1", "M", "D", "L")
               if all(_conn_in(n, c) for n in names)]
    return (len(blocked) == 0), blocked


def minimal_complete_bases(universe=None, max_size=4):
    """All minimal (by inclusion) functionally complete bases.

    Default universe is the standard connective set; the result is the famous
    17 (two singletons, nine pairs, six triples).  Returns {size: [frozenset]}.
    """
    if universe is None:
        universe = tuple(CONNECTIVES.keys())
        complete = standard_complete
    else:
        complete = lambda s: is_complete(s)

    comp = {}
    for r in range(1, max_size + 1):
        for combo in itertools.combinations(universe, r):
            ok, _ = complete(combo)
            if ok:
                comp[frozenset(combo)] = r
    minimal = {}
    for s, r in comp.items():
        if not any((t < s) for t in comp):
            minimal.setdefault(r, []).append(s)
    return minimal


# ---- The notion of each function, written with and / or and the four -------
#      literals a, not-a, b, not-b  (level 2 of the bit representation)
NOTION = {
    0:  "0",
    1:  "a\u0304 \u2227 b\u0304",
    2:  "a\u0304 \u2227 b",
    3:  "a\u0304",
    4:  "a \u2227 b\u0304",
    5:  "b\u0304",
    6:  "(a \u2227 b\u0304) \u2228 (a\u0304 \u2227 b)",
    7:  "a\u0304 \u2228 b\u0304",
    8:  "a \u2227 b",
    9:  "(a \u2227 b) \u2228 (a\u0304 \u2227 b\u0304)",
    10: "b",
    11: "a\u0304 \u2228 b",
    12: "a",
    13: "a \u2228 b\u0304",
    14: "a \u2228 b",
    15: "1",
}


def walsh2(idx):
    """The four +/-1 Walsh coefficients of a 2-input function."""
    out = []
    for u in range(4):
        s = 0
        for x in range(4):
            f = (idx >> x) & 1
            par = bin(u & x).count("1") & 1
            s += -1 if (f ^ par) else 1
        out.append(s)
    return out


def bit_matrix(idx):
    """(bit3, bit1, bit4, bit2) -- top-left, top-right, bottom-left, bottom-right."""
    return ((idx >> 1) & 1, (idx >> 3) & 1, (idx >> 0) & 1, (idx >> 2) & 1)


def bit_cube(mask):
    """{bit_number: value} for a 3-variable function; bit k-1 = 4(1-a)+2(1-b)+(1-c)."""
    out = {}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                n = 1 + 4 * (1 - a) + 2 * (1 - b) + (1 - c)
                out[n] = (mask >> ((a << 2) | (b << 1) | c)) & 1
    return out


# ---- base 2 / base 3 (three-valued) ----------------------------------------
HALF = 0.5   # the third value, between 0 and 1


def fmt3(v):
    return "0" if v == 0 else ("1" if v == 1 else "\u00bd")


def base3(idx, a, b):
    """The forced three-valued extension: AND = min, OR = max, \u00bd otherwise."""
    name = GATES[idx][0]
    if name == "AND":
        return min(a, b)
    if name == "OR":
        return max(a, b)
    if a == HALF or b == HALF:
        return HALF
    i = (int(a) << 1) | int(b)
    return float((idx >> i) & 1)

# ---- the user's own numbering and naming of the 16 functions ---------------
#      his index k reads the four bits as k = sum 2^(bit-1), where
#      bit1 = f(1,1), bit2 = f(1,0), bit3 = f(0,1), bit4 = f(0,0)
USER_TO_MINE = {0: 0, 1: 8, 2: 4, 3: 12, 4: 2, 5: 10, 6: 6, 7: 14,
                8: 1, 9: 9, 10: 5, 11: 13, 12: 3, 13: 11, 14: 7, 15: 15}

USER_NAME = {
    0: "False", 1: "A AND B", 2: "A AND B\u0304", 3: "A",
    4: "A\u0304 AND B", 5: "B", 6: "A XOR B", 7: "A OR B",
    8: "A\u0304 AND B\u0304 (NOR)", 9: "A XNOR B", 10: "B\u0304",
    11: "A OR B\u0304", 12: "A\u0304", 13: "A\u0304 OR B",
    14: "A\u0304 OR B\u0304 (NAND)", 15: "True",
}


def det2(idx):
    """The determinant of the 2x2 block  [[bit3, bit1], [bit4, bit2]]."""
    b1 = (idx >> 3) & 1
    b2 = (idx >> 2) & 1
    b3 = (idx >> 1) & 1
    b4 = (idx >> 0) & 1
    return b3 * b2 - b1 * b4


# ---- von Neumann ordinals: a function as the set of its true assignments ----
def vn_set(idx):
    """The function as a set of ordinals (the minterms where it is true)."""
    ms = minterms(idx)
    return "{" + ", ".join(str(m) for m in ms) + "}" if ms else "{}"


def bit_of(*bits):
    """The user's bit number for an assignment (a, b, c)."""
    if len(bits) == 2:
        a, b = bits
        return 1 + 2 * (1 - a) + (1 - b)
    a, b, c = bits
    return 1 + 4 * (1 - a) + 2 * (1 - b) + (1 - c)


def _evpos(ev):
    """Mouse position as QPointF, Qt5 or Qt6."""
    return QPointF(ev.position()) if QT6 else QPointF(ev.pos())


def revbits(x, n):
    r = 0
    for k in range(n):
        if (x >> k) & 1:
            r |= 1 << (n - 1 - k)
    return r


def mat_of(idx):
    """The 2x2 matrix of a function: [[bit3, bit1], [bit4, bit2]]."""
    b3, b1, b4, b2 = bit_matrix(idx)
    return ((b3, b1), (b4, b2))


def mat_props(idx):
    """(trace, det, eigen1, eigen2, rank) of that 2x2 matrix."""
    (a, b), (c, d) = mat_of(idx)
    tr = a + d
    det = a * d - b * c
    disc = max(tr * tr - 4 * det, 0)
    r = disc ** 0.5
    rank = 2 if det != 0 else (1 if (a or b or c or d) else 0)
    return tr, det, (tr + r) / 2.0, (tr - r) / 2.0, rank


def mat_str(idx):
    (a, b), (c, d) = mat_of(idx)
    return "[[%d, %d], [%d, %d]]" % (a, b, c, d)


def html_lits(s):
    """Render a string in which a negated literal is written 'X\u0304' as HTML,
    drawing each negation white-on-black instead of with a bar."""
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if i + 1 < len(s) and s[i + 1] == "\u0304":
            out.append('<span style="background:#000000;color:#ffffff">'
                       '&nbsp;%s&nbsp;</span>' % ch)
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _half(x):
    """Exact text for a multiple of 1/2 -- never a decimal."""
    n = int(round(x * 2))
    return str(n // 2) if n % 2 == 0 else "%d/2" % n


def eigen_str(idx):
    """Eigenvalues of the 2x2 matrix -- always exact, never rounded."""
    (a, b), (c, d) = mat_of(idx)
    tr = a + d
    det = a * d - b * c
    disc = tr * tr - 4 * det
    if disc < 0:
        return "(complex)"
    r = int(disc ** 0.5)
    if r * r == disc:
        return "%s, %s" % (_half((tr + r) / 2.0), _half((tr - r) / 2.0))
    def root(sign):
        if tr == 0:
            return "\u221a%d/2" % disc if sign > 0 else "\u2212\u221a%d/2" % disc
        return "(%d%s\u221a%d)/2" % (tr, "+" if sign > 0 else "\u2212", disc)
    return "%s, %s" % (root(1), root(-1))


def charpoly_str(idx):
    tr, det, e1, e2, rank = mat_props(idx)
    parts = ["\u03bb\u00b2"]
    if tr:
        parts.append("%s%d\u03bb" % ("\u2212" if tr > 0 else "+", abs(tr)))
    if det:
        parts.append("%s%d" % ("+" if det > 0 else "\u2212", abs(det)))
    return " ".join(parts)


def permanent(idx):
    (a, b), (c, d) = mat_of(idx)
    return a * d + b * c


def rank_gf2(idx):
    (a, b), (c, d) = mat_of(idx)
    rows = [[a % 2, b % 2], [c % 2, d % 2]]
    r = 0
    for col in (0, 1):
        piv = next((i for i in range(r, 2) if rows[i][col]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(2):
            if i != r and rows[i][col]:
                rows[i] = [(rows[i][k] + rows[r][k]) % 2 for k in range(2)]
        r += 1
    return r


def mat_sq_str(idx):
    (a, b), (c, d) = mat_of(idx)
    return "[[%d, %d], [%d, %d]]" % (a * a + b * c, a * b + b * d,
                                     c * a + d * c, c * b + d * d)


def inv_str(idx):
    (a, b), (c, d) = mat_of(idx)
    det = a * d - b * c
    if det == 0:
        return "\u2014"
    return "[[%d, %d], [%d, %d]]/%d" % (d, -b, -c, a, det)


def frob_str(idx):
    (a, b), (c, d) = mat_of(idx)
    s = a * a + b * b + c * c + d * d
    r = int(s ** 0.5)
    return str(r) if r * r == s else "\u221a%d" % s


def weight(idx):
    """How many of the four truth-table slots are 1."""
    return bin(idx).count("1")


def det_gf2(idx):
    """The determinant over GF(2) -- 1 means invertible mod 2."""
    (a, b), (c, d) = mat_of(idx)
    return (a * d - b * c) % 2


def mat_class(idx):
    """The algebraic type: M^2 = I, M^2 = M, M^2 = 0, or none."""
    (a, b), (c, d) = mat_of(idx)
    m2 = (a * a + b * c, a * b + b * d, c * a + d * c, c * b + d * d)
    if m2 == (1, 0, 0, 1):
        return "involution"
    if m2 == (a, b, c, d):
        return "idempotent"
    if m2 == (0, 0, 0, 0):
        return "nilpotent"
    return "\u2014"


def mat_t_str(idx):
    """The Gram matrix M^T M -- off-diagonal is the row dot product."""
    (a, b), (c, d) = mat_of(idx)
    return "[[%d, %d], [%d, %d]]" % (a * a + c * c, a * b + c * d,
                                     a * b + c * d, b * b + d * d)


def _sqrt_str(n):
    r = int(n ** 0.5)
    return str(r) if r * r == n else "\u221a%d" % n


def sing_str(idx):
    """Singular values, exactly -- the square roots of eig(M^T M)."""
    (a, b), (c, d) = mat_of(idx)
    p = a * a + b * b + c * c + d * d
    det = a * d - b * c
    disc = p * p - 4 * det * det
    r = int(disc ** 0.5)
    if r * r == disc:
        return "%s, %s" % (_sqrt_str((p + r) // 2), _sqrt_str((p - r) // 2))
    return "\u221a((%d+\u221a%d)/2), \u221a((%d\u2212\u221a%d)/2)" % (p, disc, p, disc)


FORMAL_NAME = {
    0: "FALSE", 1: "NOR", 2: "NOT A AND B", 3: "NOT A", 4: "A AND NOT B",
    5: "NOT B", 6: "XOR", 7: "NAND", 8: "AND", 9: "XNOR", 10: "B",
    11: "B OR NOT A", 12: "A", 13: "A OR NOT B", 14: "OR", 15: "TRUE",
}


def expr_str(idx):
    """The function written only from a, \u0304a, b, \u0304b -- with its formal
    name in brackets, e.g.  a\u0304 \u2227 b\u0304  (NOR)."""
    return "%s\u0001  (%s)" % (NOTION[idx], FORMAL_NAME[idx])


def is_literal(s, i):
    """True when s[i] is a literal letter rather than part of a word."""
    if "\u0001" in s[:i]:
        return False          # past the sentinel: the formal name, not literals
    ch = s[i]
    if ch not in "ABab":
        return False
    prev = s[i - 1] if i > 0 else ""
    nxt = s[i + 1] if i + 1 < len(s) else ""
    if prev.isascii() and prev.isalpha():
        return False
    if nxt.isascii() and nxt.isalpha():
        return False
    return True


# ---------------------------------------------------------------------------
#  Synthesising all 16 functions inside each of the 17 minimal bases
# ---------------------------------------------------------------------------
_SYN_NAME = {"AND": "and", "OR": "or", "XOR": "xor", "XNOR": "xnor",
             "NAND": "nand", "NOR": "nor"}
_SYN_MIXED = {"B \u2228 A\u0304": "b or not a",
              "A \u2227 B\u0304": "a and not b"}


def _vec(i):
    """The truth vector of function i over (a,b) = 00,01,10,11."""
    return tuple((i >> m) & 1 for m in range(4))


def _apply_bin(ov, x, y):
    return tuple(ov[(xv << 1) | yv] for xv, yv in zip(x, y))


def _paren(e, kind):
    """Wrap a compound operand in brackets; atoms and 'not a' stay bare."""
    return e if kind < 2 else "(%s)" % e


def shortest_in(names, cap=6):
    """Shortest expression for each of the 16 vectors using only `names`.
    Expressions read in words, e.g.  or = not(not a and not b)."""
    best = {_vec(12): ("a", 0), _vec(10): ("b", 0)}
    if "TRUE" in names:
        best.setdefault((1, 1, 1, 1), ("1", 0))
    if "FALSE" in names:
        best.setdefault((0, 0, 0, 0), ("0", 0))
    for _ in range(cap):
        if len(best) >= 16:
            break
        items = list(best.items())
        added = False
        for vec, (expr, kind) in items:
            for nm in names:
                if nm in ("TRUE", "FALSE"):
                    continue
                if nm == "NOT":
                    nv = tuple(1 - v for v in vec)
                    if nv not in best:
                        best[nv] = ("not " + expr if kind == 0
                                    else "not(" + expr + ")", 1)
                        added = True
                    continue
                ov = tuple(CONNECTIVES[nm][1])
                for v2, (e2, k2) in items:
                    nv = _apply_bin(ov, vec, v2)
                    if nv in best:
                        continue
                    if nm in _SYN_MIXED:
                        best[nv] = ("%s(%s, %s)"
                                    % (_SYN_MIXED[nm], expr, e2), 2)
                    else:
                        best[nv] = ("%s %s %s"
                                    % (_paren(expr, kind), _SYN_NAME[nm],
                                       _paren(e2, k2)), 2)
                    added = True
        if not added:
            break
    return {k: v[0] for k, v in best.items()}


_SYN_CACHE = None


def synthesis():
    """For each of the 17 minimal bases, an expression for each of the 16
    functions using only that base's connectives."""
    global _SYN_CACHE
    if _SYN_CACHE is not None:
        return _SYN_CACHE
    mb = minimal_complete_bases()
    bases = []
    for sz in sorted(mb):
        for b in sorted(mb[sz], key=lambda x: sorted(x)):
            bases.append(sorted(b))
    out = []
    for b in bases:
        res = shortest_in(b)
        out.append([res.get(_vec(i), "\u2014") for i in range(16)])
    _SYN_CACHE = (bases, out)
    return _SYN_CACHE


def plain(s):
    """Render the internal negation marker 'X\u0304' as the word 'not X'."""
    out, i = [], 0
    while i < len(s):
        if i + 1 < len(s) and s[i + 1] == "\u0304":
            out.append("not " + s[i])
            i += 2
        elif s[i] == "\u0001":
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


SEPARATE_NAMES = {0, 1, 6, 7, 8, 9, 14, 15}


def expr_cell(idx):
    """Expression, with the formal name on a second line -- but only where the
    name is a distinct connective name, not a restatement of the variables."""
    body = plain(NOTION[idx])
    if idx in SEPARATE_NAMES:
        return body + "\n(" + FORMAL_NAME[idx] + ")"
    return body


# One symbol per function, in the table's own order. The four literals keep
# their letters; the rest use the standard glyphs.
SYMBOL = ["\u22a5", "\u2227", "a \u2227 not b", "a", "not a \u2227 b", "b",
          "\u2295", "\u2228", "\u2193", "\u2299", "not b",
          "a \u2228 not b", "not a", "not a \u2228 b", "\u2191", "\u22a4"]
import re



# ===========================================================================
#  Shared UI helpers
# ===========================================================================

def mono_font(pt=0):
    # build a fresh QFont from the fixed font's family so point sizes apply
    # (systemFont() can carry a pixel size that silently overrides setPointSize).
    fam = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
    f = QFont(fam)
    if pt:
        f.setPointSize(pt)
    return f


def heading(text, size=11):
    lab = QLabel(text)
    f = lab.font()
    f.setPointSize(size)
    f.setWeight(QFont.Weight.DemiBold)
    lab.setFont(f)
    return lab


def body(text):
    lab = QLabel(text)
    lab.setWordWrap(True)
    return lab


def caption(text):
    lab = QLabel(text)
    lab.setWordWrap(True)
    lab.setStyleSheet("color:#666666;")
    return lab


def card(title=None):
    """A titled group box (native look); returns (box, inner_layout)."""
    gb = QGroupBox(title or "")
    lay = QVBoxLayout(gb)
    lay.setContentsMargins(9, 9, 9, 9)
    lay.setSpacing(6)
    return gb, lay


def gray_code(i):
    return i ^ (i >> 1)


def bitstring(value, width):
    return format(value, "0%db" % width)


def function_options():
    """(value, line1, line2) for every one of the 16 functions,
    in the user's own numbering and naming."""
    opts = []
    for k in range(16):
        i = USER_TO_MINE[k]
        opts.append((i, "%d  %s" % (k, USER_NAME[k]), GATES[i][1]))
    return opts


# ===========================================================================
#  Always-visible selectors (no dropdowns)
# ===========================================================================

class Segmented(QWidget):
    """A row of exclusive buttons -- every option visible at once."""

    changed = pyqtSignal(object)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons = []
        self._value = options[0][1] if options else None
        for label, value in options:
            b = QToolButton()
            b.setText(label)
            b.setCheckable(True)
            b.setMinimumWidth(42)
            b.clicked.connect(lambda _=False, v=value: self._select(v))
            self._group.addButton(b)
            lay.addWidget(b)
            self._buttons.append((b, value))
            if value == self._value:
                b.setChecked(True)
        lay.addStretch(1)

    def _select(self, value):
        self._value = value
        self.changed.emit(value)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        for b, v in self._buttons:
            if v == value:
                b.setChecked(True)   # exclusive group unchecks the rest


class TileGrid(QWidget):
    """A grid of exclusive tiles -- every option visible at once."""

    changed = pyqtSignal(object)

    def __init__(self, options, columns=4, parent=None):
        super().__init__(parent)
        self._columns = columns
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons = []
        self._value = None
        self.set_options(options)

    def set_options(self, options):
        for b, _v in self._buttons:
            self._grid.removeWidget(b)
            self._group.removeButton(b)
            b.deleteLater()
        self._buttons = []
        for k, (value, top, sub) in enumerate(options):
            b = QToolButton()
            b.setCheckable(True)
            txt = top if not sub else top + "\n" + sub
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setMinimumHeight(24)
            if "\u0304" in txt:
                lbl = QLabel(html_lits(txt))
                lbl.setTextFormat(Qt.TextFormat.RichText)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFont(mono_font(8))
                lbl.setStyleSheet("background:transparent;")
                lbl.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
                lay = QVBoxLayout(b)
                lay.setContentsMargins(1, 1, 1, 1)
                lay.addWidget(lbl)
            else:
                b.setText(txt)
            b.clicked.connect(lambda _=False, v=value: self._select(v))
            self._group.addButton(b)
            self._grid.addWidget(b, k // self._columns, k % self._columns)
            self._buttons.append((b, value))
        if options:
            self._value = options[0][0]
            self._buttons[0][0].setChecked(True)

    def _select(self, value):
        self._value = value
        self.changed.emit(value)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        for b, v in self._buttons:
            if v == value:
                b.setChecked(True)   # exclusive group unchecks the rest


class LitDelegate(QStyledItemDelegate):
    """Cells read in words ('not a'); a "expr\n(NAME)" cell draws two lines."""

    def paint(self, painter, option, index):
        txt = str(index.data() or "")
        if "\n" not in txt:
            super().paint(painter, option, index)
            return
        top, sub = txt.split("\n", 1)
        r = option.rect
        painter.save()
        painter.setPen(option.palette.text().color())
        painter.drawText(QRectF(r.left(), r.top() + 1, r.width(), r.height() / 2 - 1),
                         Qt.AlignmentFlag.AlignCenter, top)
        f = QFont(option.font)
        f.setPointSize(max(6, f.pointSize() - 1))
        painter.setFont(f)
        painter.setPen(QColor("#6b6b6b"))
        painter.drawText(QRectF(r.left(), r.center().y(), r.width(),
                                r.height() / 2 - 1),
                         Qt.AlignmentFlag.AlignCenter, sub)
        painter.restore()


class MatrixDelegate(QStyledItemDelegate):
    """Draws a [[a,b],[c,d]] cell as an actual bracketed 2x2 matrix."""

    def paint(self, painter, option, index):
        s = str(index.data() or "")
        nums = re.findall(r"-?\d+", s)
        if not s.startswith("[[") or len(nums) != 4:
            super().paint(painter, option, index)
            return
        a, b, c, d = nums
        r = option.rect
        painter.save()
        f = QFont(option.font)
        f.setPointSize(max(8, f.pointSize()))
        painter.setFont(f)
        fm = painter.fontMetrics()
        cw = max(fm.horizontalAdvance("0") + 12, 14)
        ch = fm.height()
        w = 2 * cw
        h = 2 * ch
        x0 = r.center().x() - w / 2.0
        y0 = r.center().y() - h / 2.0
        painter.setPen(QPen(option.palette.text().color(), 1))
        for i, v in enumerate((a, b, c, d)):
            rr, cc = divmod(i, 2)
            painter.drawText(QRectF(x0 + cc * cw, y0 + rr * ch, cw, ch),
                             Qt.AlignmentFlag.AlignCenter, v)
        pn = painter.pen()
        pn.setWidthF(1.2)
        painter.setPen(pn)
        tick = cw * 0.18
        for side, xx in ((0, x0 - 3), (1, x0 + w + 3)):
            painter.drawLine(QPointF(xx, y0), QPointF(xx, y0 + h))
            painter.drawLine(QPointF(xx, y0),
                             QPointF(xx + (tick if side == 0 else -tick), y0))
            painter.drawLine(QPointF(xx, y0 + h),
                             QPointF(xx + (tick if side == 0 else -tick), y0 + h))
        painter.restore()


def _row_key(t, r, col):
    it = t.item(r, col)
    txt = it.text() if it is not None else ""
    try:
        return (0, float(txt))
    except ValueError:
        return (1, txt)


def _reorder(t, order):
    """Rewrite the table's items in the given row order (no sortItems)."""
    ncol = t.columnCount()
    snap = [[t.item(r, c).text() if t.item(r, c) is not None else ""
             for c in range(ncol)] for r in range(t.rowCount())]
    for r, src in enumerate(order):
        for c in range(ncol):
            it = t.item(r, c)
            if it is not None:
                it.setText(snap[src][c])


def _tint_groups(t, col):
    """Shade alternating runs of equal values in `col` so groups are visible."""
    last = object()
    band = 0
    for r in range(t.rowCount()):
        it = t.item(r, col)
        v = it.text() if it is not None else ""
        if v != last:
            band ^= 1
            last = v
        for c in range(t.columnCount()):
            cell = t.item(r, c)
            if cell is not None:
                cell.setBackground(QColor("#f0f0f0") if band else QColor("#ffffff"))


def install_header_actions(t, on_change=None):
    """Clicking a column header cycles:
    none -> sort ascending -> sort descending -> group by that column -> none."""

    h = t.horizontalHeader()
    h.setSectionsClickable(True)
    h.setSortIndicatorShown(True)
    t._sort_state = {}

    def click(col):
        st = (t._sort_state.get(col, 0) + 1) % 4
        t._sort_state = {col: st}
        if st == 0:
            h.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            _reorder(t, sorted(range(t.rowCount()),
                               key=lambda r: _row_key(t, r, 0)))
        else:
            order = sorted(range(t.rowCount()),
                           key=lambda r: _row_key(t, r, col),
                           reverse=(st == 2))
            _reorder(t, order)
            h.setSortIndicator(
                col, Qt.SortOrder.DescendingOrder if st == 2
                else Qt.SortOrder.AscendingOrder)
            if st == 3:
                _tint_groups(t, col)
                return
        if on_change is not None:
            on_change()

    t._sort_click = click
    h.sectionClicked.connect(click)


# ===========================================================================
#  Hypercube widget  (Q_n drawn as a graph)
# ===========================================================================

def cube_positions(n):
    """Normalised (x, y) positions for the 2^n vertices of Q_n, n in 2..4.

    Orientation: the all-zeros vertex (00, 000, 0000) sits bottom-left and the
    all-ones vertex (11, 111, 1111) top-right.  a runs right, b runs up, and
    c is depth (drawn up-right).
    """
    pos = {}
    if n == 2:
        for i in range(4):
            A, B = (i >> 1) & 1, i & 1
            pos[i] = (0.18 + 0.64 * A, 0.18 + 0.64 * (1 - B))
    elif n == 3:
        for i in range(8):
            A, B, C = (i >> 2) & 1, (i >> 1) & 1, i & 1
            pos[i] = (0.08 + A * 0.48 + C * 0.28, 0.88 - B * 0.48 - C * 0.28)
    else:
        # a cube inside a cube: w = 0 outer, w = 1 inner
        base = {}
        for a in (0, 1):
            for b in (0, 1):
                for c in (0, 1):
                    base[(a, b, c)] = (0.10 + a * 0.50 + c * 0.28,
                                       0.88 - b * 0.50 - c * 0.28)
        cx, cy = 0.48, 0.50
        for i in range(16):
            A, B, C, W = (i >> 3) & 1, (i >> 2) & 1, (i >> 1) & 1, i & 1
            bx, by = base[(A, B, C)]
            sc = 1.0 if W == 0 else 0.58
            pos[i] = (cx + sc * (bx - cx), cy + sc * (by - cy))
    return pos


def cube_edges(n):
    return [(i, j) for i in range(1 << n) for j in range(i + 1, 1 << n)
            if bin(i ^ j).count("1") == 1]


def gray_tour(n):
    seq = [gray_code(i) for i in range(1 << n)]
    return seq + [seq[0]]


class HypercubeWidget(QWidget):
    """Draws Q_n; vertices are minterms, edges are single-bit flips."""

    vertexClicked = pyqtSignal(int)
    valuesChanged = pyqtSignal()

    def __init__(self, nvars=3, values=None, parent=None):
        super().__init__(parent)
        self.nvars = nvars
        self.values = list(values) if values else [0] * (1 << nvars)
        self.show_tour = False
        self.show_labels = True
        self.hl = set()
        self._pos = {}
        self.setMinimumSize(200, 132)

    def set_nvars(self, n):
        self.nvars = n
        self.values = [0] * (1 << n)
        self.update()

    def set_values(self, vals):
        self.values = list(vals)
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        W, H = self.width(), self.height()
        p.fillRect(self.rect(), QColor("#ffffff"))
        n = self.nvars
        pad = 40
        S = min(W, H) - 2 * pad
        ox, oy = (W - S) / 2, (H - S) / 2
        norm = cube_positions(n)
        pos = {i: QPointF(ox + pad + norm[i][0] * S, oy + pad + norm[i][1] * S)
               for i in norm}
        self._pos = pos

        tour = set()
        if self.show_tour:
            t = gray_tour(n)
            for a, b in zip(t, t[1:]):
                tour.add((min(a, b), max(a, b)))
        for (i, j) in cube_edges(n):
            on = (i, j) in tour
            p.setPen(QPen(UNSURE_COL if on else GRID, 2.2 if on else 1.0))
            p.drawLine(pos[i], pos[j])

        rr = 9 if n >= 4 else 12
        for i in range(1 << n):
            v = self.values[i] if i < len(self.values) else 0
            r = rr
            if i in self.hl:
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(HL, 3))
                p.drawEllipse(pos[i], r + 5, r + 5)
            p.setBrush(QBrush(TRUE_COL if v else FALSE_COL))
            p.setPen(QPen(QColor("#ffffff"), 1.5))
            p.drawEllipse(pos[i], r, r)
            p.setFont(mono_font(9))
            p.setPen(QPen(QColor("#ffffff")))
            p.drawText(QRectF(pos[i].x() - r, pos[i].y() - r, 2 * r, 2 * r),
                       Qt.AlignmentFlag.AlignCenter, str(v))
            if self.show_labels and n <= 3:
                p.setFont(mono_font(7))
                p.setPen(QPen(MUTED))
                ly = (pos[i].y() + r + 2 if pos[i].y() > H / 2.0
                      else pos[i].y() - r - 16)
                p.drawText(QRectF(pos[i].x() - 26, ly, 52, 14),
                           Qt.AlignmentFlag.AlignCenter, bitstring(i, n))
        if self.show_labels and n <= 3:
            names = "abcd"
            p.setFont(mono_font(9))
            gx = sum(q.x() for q in pos.values()) / len(pos)
            gy = sum(q.y() for q in pos.values()) / len(pos)
            for k in range(n):
                for v in (0, 1):
                    pts = [pos[i] for i in range(1 << n)
                           if ((i >> (n - 1 - k)) & 1) == v]
                    if not pts:
                        continue
                    cx = sum(q.x() for q in pts) / len(pts)
                    cy = sum(q.y() for q in pts) / len(pts)
                    dx, dy = cx - gx, cy - gy
                    dd = (dx * dx + dy * dy) ** 0.5 or 1.0
                    lx = cx + dx / dd * 17.0
                    ly = cy + dy / dd * 17.0
                    fm = p.fontMetrics()
                    lab = names[k] if v else "not " + names[k]
                    w = fm.horizontalAdvance(lab) + 6
                    h = fm.height()
                    rect = QRectF(lx - w / 2, ly - h / 2, w, h)
                    p.setPen(QPen(INK))
                    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, lab)
        p.setFont(mono_font(8))
        p.setPen(QPen(MUTED))
        p.drawText(QRectF(6, 2, W - 12, 16), Qt.AlignmentFlag.AlignLeft,
                   "n = %d     2^%d = %d vertices      %d edges"
                   % (n, n, 1 << n, n * (1 << (n - 1))))
        p.end()

    def set_highlight(self, s):
        self.hl = set(s)
        self.update()

    def mousePressEvent(self, ev):
        q = _evpos(ev)
        best, bd = None, 1e9
        for i, pt in self._pos.items():
            d = (pt.x() - q.x()) ** 2 + (pt.y() - q.y()) ** 2
            if d < bd:
                bd, best = d, i
        if best is not None and bd < 900:
            if best < len(self.values):
                self.values[best] = 1 - self.values[best]
            self.vertexClicked.emit(best)
            self.valuesChanged.emit()
            self.update()


# ===========================================================================
#  The Boolean lattice B_n, drawn by rank  (the "tree")
# ===========================================================================

class LatticeWidget(QWidget):
    """B_n by rank: all-ones at the top, all-zeros at the bottom."""

    nodeClicked = pyqtSignal(int)

    def __init__(self, n=2, parent=None):
        super().__init__(parent)
        self.n = n
        self.hl = set()
        self._pos = {}
        self.setMinimumSize(240, 170)

    def set_n(self, n):
        self.n = n
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor("#ffffff"))
        n = self.n
        W, H = self.width(), self.height()
        padx, pady = 34, 26
        ranks = {}
        for i in range(1 << n):
            ranks.setdefault(bin(i).count("1"), []).append(i)
        pos = {}
        for r in range(n + 1):
            row = sorted(ranks.get(r, []))
            m = len(row)
            y = pady + (n - r) * ((H - 2 * pady) / n)
            for j, v in enumerate(row):
                x = padx + (j + 1) * (W - 2 * padx) / (m + 1)
                pos[v] = QPointF(x, y)
        self._pos = pos
        p.setPen(QPen(GRID, 1))
        for i in range(1 << n):
            for j in range(1 << n):
                if bin(i ^ j).count("1") == 1 and \
                        bin(i).count("1") + 1 == bin(j).count("1"):
                    p.drawLine(pos[i], pos[j])
        for i in range(1 << n):
            pt = pos[i]
            if i in self.hl:
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(HL, 3))
                p.drawEllipse(pt, 9, 9)
            p.setBrush(QBrush(QColor("#e8e8e8")))
            p.setPen(QPen(QColor("#8a8a8a"), 1))
            p.drawEllipse(pt, 4, 4)
            p.setFont(mono_font(7))
            p.setPen(QPen(INK))
            p.drawText(QRectF(pt.x() - 24, pt.y() - 17, 48, 12),
                       Qt.AlignmentFlag.AlignCenter, bitstring(i, n))
        p.end()

    def set_highlight(self, s):
        self.hl = set(s)
        self.update()

    def mousePressEvent(self, ev):
        q = _evpos(ev)
        best, bd = None, 1e9
        for i, pt in self._pos.items():
            d = (pt.x() - q.x()) ** 2 + (pt.y() - q.y()) ** 2
            if d < bd:
                bd, best = d, i
        if best is not None and bd < 900:
            self.nodeClicked.emit(best)


# ===========================================================================
#  The von Neumann ordinals
# ===========================================================================

class VNWidget(QWidget):
    """The ordinals as sets of their predecessors (von Neumann)."""

    rowClicked = pyqtSignal(int)

    def __init__(self, n=2, parent=None):
        super().__init__(parent)
        self.n = n
        self.hl = set()
        self.setMinimumSize(180, 170)

    def set_n(self, n):
        self.n = n
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#ffffff"))
        n = self.n
        total = 1 << n
        show = min(total, 16)
        y = 8
        p.setFont(mono_font(9))
        for m in range(show):
            if m in self.hl:
                p.fillRect(QRectF(4, y, self.width() - 8, 17), QColor(224, 165, 58, 70))
            p.setPen(QPen(INK))
            txt = "%2d = {%s}" % (m, ", ".join(str(k) for k in range(m)))
            p.drawText(QRectF(8, y, self.width() - 16, 16),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       txt)
            y += 17
        if total > show:
            p.setPen(QPen(MUTED))
            p.drawText(QRectF(8, y, self.width() - 16, 16),
                       Qt.AlignmentFlag.AlignLeft, "\u2026  up to %d" % (total - 1))
        p.end()

    def set_highlight(self, s):
        self.hl = set(s)
        self.update()

    def mousePressEvent(self, ev):
        q = _evpos(ev)
        m = int((q.y() - 8) // 17)
        if 0 <= m < min(1 << self.n, 16):
            self.rowClicked.emit(m)


# ===========================================================================
#  Venn diagram widget
# ===========================================================================
#
#  The n-set Venn diagram is the plane cut into 2^n regions, one per minterm.
#  Regions are built as real geometry with QPainterPath boolean operations, so
#  what is filled is exactly the atom -- not a painted approximation.
#
#  Two and three sets use circles (the flat limit).  Four and five sets use
#  ellipses: a pair of circles meets in at most 2 points, so four circles give
#  at most n^2-n+2 = 14 regions and cannot reach the 16 a 4-set diagram needs;
#  ellipses meet in up to 4, which lifts the limit to five sets.  The ellipse
#  arrangements below were found and verified by sampling -- every one of the
#  2^n regions is present.

def _circle(cx, cy, r):
    return {"k": "c", "cx": cx, "cy": cy, "r": r}


def _ellipse(cx, cy, a, b, ang):
    return {"k": "e", "cx": cx, "cy": cy, "a": a, "b": b, "ang": ang}


def _rot_ellipses(n, base_deg, R, a, b, phi_deg):
    out = []
    for i in range(n):
        th = math.radians(base_deg + 360.0 / n * i)
        out.append(_ellipse(R * math.cos(th), R * math.sin(th), a, b,
                            th + math.radians(phi_deg)))
    return out


def venn_shapes(n):
    """The curves for an n-set diagram, in a shared normalised space (y up)."""
    if n == 2:
        return [_circle(0.40, 0.52, 0.30), _circle(0.61, 0.52, 0.30)]
    if n == 3:
        out = []
        for ang in (90, 210, 330):
            a = math.radians(ang)
            out.append(_circle(0.5 + 0.16 * math.cos(a),
                               0.52 + 0.16 * math.sin(a), 0.30))
        return out
    if n == 4:
        return _rot_ellipses(4, 351.4518, 0.25590, 1.61601, 0.40382, 25.9659)
    if n == 5:
        return _rot_ellipses(5, 266.3543, 0.47209, 1.17293, 0.46845, 5.2164)
    raise ValueError("unsupported set count: %d" % n)


def _shape_contains(sh, x, y):
    if sh["k"] == "c":
        return (x - sh["cx"]) ** 2 + (y - sh["cy"]) ** 2 <= sh["r"] ** 2
    dx, dy = x - sh["cx"], y - sh["cy"]
    c, s = math.cos(sh["ang"]), math.sin(sh["ang"])
    xr = dx * c + dy * s
    yr = -dx * s + dy * c
    return (xr / sh["a"]) ** 2 + (yr / sh["b"]) ** 2 <= 1.0


def _shape_bbox(sh):
    if sh["k"] == "c":
        r = sh["r"]
        return (sh["cx"] - r, sh["cy"] - r, sh["cx"] + r, sh["cy"] + r)
    a, b, ang = sh["a"], sh["b"], sh["ang"]
    w = math.hypot(a * math.cos(ang), b * math.sin(ang))
    h = math.hypot(a * math.sin(ang), b * math.cos(ang))
    return (sh["cx"] - w, sh["cy"] - h, sh["cx"] + w, sh["cy"] + h)


def _shape_path(sh):
    p = QPainterPath()
    if sh["k"] == "c":
        p.addEllipse(QPointF(sh["cx"], sh["cy"]), sh["r"], sh["r"])
    else:
        p.addEllipse(QPointF(0.0, 0.0), sh["a"], sh["b"])
        t = QTransform()
        t.translate(sh["cx"], sh["cy"])
        t.rotate(math.degrees(sh["ang"]))
        p = t.map(p)
    return p


def _shape_edge_point(sh, ucx, ucy):
    """A point on the shape boundary, outwards from the diagram centre."""
    dx, dy = sh["cx"] - ucx, sh["cy"] - ucy
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    if sh["k"] == "c":
        return (sh["cx"] + ux * sh["r"], sh["cy"] + uy * sh["r"])
    c, s = math.cos(sh["ang"]), math.sin(sh["ang"])
    xr = ux * c + uy * s
    yr = -ux * s + uy * c
    t = 1.0 / math.sqrt((xr / sh["a"]) ** 2 + (yr / sh["b"]) ** 2)
    return (sh["cx"] + ux * t, sh["cy"] + uy * t)


class VennWidget(QWidget):
    """Venn diagram of 2..5 sets; regions are minterms, clickable."""

    atomClicked = pyqtSignal(int)

    def __init__(self, nvars=2, highlight=None, parent=None):
        super().__init__(parent)
        self.nvars = nvars
        self.highlight = set(highlight or [])
        self.setMinimumSize(240, 152)
        self._shapes = []
        self._paths = {}
        self._anchors = {}
        self._transform = QTransform()
        self._inv = QTransform()
        self._rebuild()

    def set_nvars(self, n):
        self.nvars = n
        self.highlight = set()
        self._rebuild()
        self.update()

    def set_highlight(self, masks):
        self.highlight = set(masks)
        self.update()

    # -- geometry ----------------------------------------------------------
    def _rebuild(self):
        n = self.nvars
        self._shapes = venn_shapes(n)

        bx0 = min(_shape_bbox(s)[0] for s in self._shapes)
        by0 = min(_shape_bbox(s)[1] for s in self._shapes)
        bx1 = max(_shape_bbox(s)[2] for s in self._shapes)
        by1 = max(_shape_bbox(s)[3] for s in self._shapes)
        pad = 0.06 * max(bx1 - bx0, by1 - by0)
        self._box = (bx0 - pad, by0 - pad, bx1 + pad, by1 + pad)
        self._ucx = (bx0 + bx1) / 2.0
        self._ucy = (by0 + by1) / 2.0

        W, H = max(self.width(), 2), max(self.height(), 2)
        bw = self._box[2] - self._box[0]
        bh = self._box[3] - self._box[1]
        m = 14
        scale = min((W - 2 * m) / bw, (H - 2 * m) / bh)
        ox = (W - scale * bw) / 2.0
        oy = (H - scale * bh) / 2.0
        # normalised (y up) -> widget (y down)
        t = QTransform(scale, 0.0, 0.0, -scale,
                       ox - self._box[0] * scale,
                       oy + self._box[3] * scale)
        self._transform = t
        self._inv, _ = t.inverted()

        # universe + atom paths (built in normalised space)
        uni = QPainterPath()
        uni.addRect(QRectF(self._box[0], self._box[1], bw, bh))
        shape_paths = [_shape_path(s) for s in self._shapes]
        self._paths = {}
        for mask in range(1 << n):
            p = QPainterPath(uni)
            for k in range(n):
                p = p.intersected(shape_paths[k]) if (mask >> k) & 1 \
                    else p.subtracted(shape_paths[k])
            self._paths[mask] = p

        # label anchors: deepest interior point of each atom
        best = {}
        steps = 90 if n <= 3 else 120
        for ix in range(1, steps):
            for iy in range(1, steps):
                qx = self._box[0] + ix / float(steps) * bw
                qy = self._box[1] + iy / float(steps) * bh
                msk = 0
                depth = 1e9
                for k, s in enumerate(self._shapes):
                    inside = _shape_contains(s, qx, qy)
                    if inside:
                        msk |= 1 << k
                    if s["k"] == "c":
                        d = math.hypot(qx - s["cx"], qy - s["cy"])
                        edge = (s["r"] - d) if inside else (d - s["r"])
                    else:
                        ddx, ddy = qx - s["cx"], qy - s["cy"]
                        c, sn = math.cos(s["ang"]), math.sin(s["ang"])
                        xr = ddx * c + ddy * sn
                        yr = -ddx * sn + ddy * c
                        rho = math.sqrt((xr / s["a"]) ** 2 + (yr / s["b"]) ** 2)
                        edge = (1.0 - rho) if inside else (rho - 1.0)
                    depth = min(depth, edge)
                if msk not in best or depth > best[msk][0]:
                    best[msk] = (depth, QPointF(qx, qy))
        self._anchors = {m: v[1] for m, v in best.items()}

    def resizeEvent(self, ev):
        self._rebuild()

    # -- painting ----------------------------------------------------------
    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor("#ffffff"))
        T = self._transform

        for mask, path in self._paths.items():
            if mask in self.highlight:
                p.fillPath(T.map(path), QColor(224, 165, 58, 90))

        p.setBrush(Qt.BrushStyle.NoBrush)
        ub = self._box
        p.setPen(QPen(QColor("#9a9a9a"), 1.1, Qt.PenStyle.DashLine))
        p.drawRect(T.mapRect(QRectF(ub[0], ub[1],
                                    ub[2] - ub[0], ub[3] - ub[1])))
        p.setPen(QPen(ACCENT, 1.4))
        for s in self._shapes:
            p.drawPath(T.map(_shape_path(s)))


        nf = QFont(); nf.setPointSize(10); nf.setWeight(QFont.Weight.DemiBold)
        p.setFont(nf)
        p.setPen(QPen(ACCENT))
        names = "ABCDEFGH"
        for k, s in enumerate(self._shapes):
            ex, ey = _shape_edge_point(s, self._ucx, self._ucy)
            sp = T.map(QPointF(ex, ey))
            p.drawText(QRectF(sp.x() - 9, sp.y() - 9, 18, 18),
                       Qt.AlignmentFlag.AlignCenter, names[k])
        p.end()

    def mousePressEvent(self, ev):
        pos = QPointF(ev.position()) if QT6 else QPointF(ev.pos())
        np = self._inv.map(pos)   # widget point -> normalised space
        m = 0
        for k, s in enumerate(self._shapes):
            if _shape_contains(s, np.x(), np.y()):
                m |= 1 << k
        self.atomClicked.emit(m)


# ===========================================================================
#  Reusable: build a read-only table
# ===========================================================================

def make_table(headers, rows, width=None, height=None):
    t = QTableWidget(len(rows), len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.setFont(mono_font(10))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(r, c, item)
    t.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    if width:
        t.setMaximumWidth(width)
    if height:
        t.setMinimumHeight(height)
        t.setMaximumHeight(height)
        t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    return t


# ===========================================================================
#  Tab: Gates & Truth Tables
# ===========================================================================

# ===========================================================================

def pattern_values(n, kind):
    vals = []
    for i in range(1 << n):
        bits = [(i >> k) & 1 for k in range(n)]
        if kind == "all-0":
            v = 0
        elif kind == "all-1":
            v = 1
        elif kind == "parity (XOR)":
            v = sum(bits) % 2
        elif kind == "AND of all":
            v = 1 if all(bits) else 0
        elif kind == "OR of all":
            v = 1 if any(bits) else 0
        elif kind == "majority":
            v = 1 if sum(bits) > n / 2 else 0
        else:
            v = 0
        vals.append(v)
    return vals


class HypercubeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.cube = HypercubeWidget(3)
        root.addWidget(self.cube, 1)

        self.nvars = 3
        self.facts = QLabel()
        self.facts.setFont(mono_font(9))
        root.addWidget(self.facts)
        self._refresh()

    def _pattern_options(self, n):
        opts = []
        if n == 2:
            for i in range(16):
                opts.append((("gate", i), "%d %s" % (i, GATES[i][0]), GATES[i][1]))
        for k in ("parity (XOR)", "AND of all", "OR of all", "majority", "all-0", "all-1"):
            if n % 2 == 0 and k == "majority":
                continue
            opts.append((("named", k), k, ""))
        return opts

    def set_dim(self, n):
        self.nvars = n
        self.cube.set_nvars(n)
        self._refresh()

    def _refresh(self, *_):
        n = self.nvars
        self.cube.set_values([0] * (1 << n))
        self.facts.setText(
            "vertices 2^%d = %d     edges %d     degree %d"
            % (n, 1 << n, n * (1 << (n - 1)), n))


# ===========================================================================
#  Tab: Venn
# ===========================================================================

class VennTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.venn = VennWidget(2)
        root.addWidget(self.venn, 1)

        self.nvars = 2
        ctrl, cl = card("Venn")
        self.atom = QLabel("click a region")
        self.atom.setFont(mono_font(9))
        cl.addWidget(self.atom)
        root.addWidget(ctrl)

        self.venn.atomClicked.connect(self._on_atom)
        self.set_sets(2)

    def set_sets(self, n):
        self.nvars = n
        self.venn.set_nvars(n)
        self._refresh()

    def _refresh(self, *_):
        self.venn.set_highlight(set())

    def _on_atom(self, mask):
        n = self.nvars
        atoms = []
        for k in range(n):
            atoms.append("abcde"[k] if (mask >> k) & 1 else "abcde"[k] + "\u0304")
        self.atom.setText("atom   " + html_lits(" \u2229 ".join(atoms)))


# ===========================================================================
#  The 16 functions, all representations merged into one table
# ===========================================================================

def _all_reps_table():
    cols = ["#", "symbol", "expression", "matrix", "det", "trace", "eigen",
            "rank", "code", "SOP", "ANF", "Walsh", "set", "NPN"]
    t = QTableWidget(16, len(cols))
    t.setHorizontalHeaderLabels(cols)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    for c in range(len(cols)):
        t.horizontalHeader().setSectionResizeMode(
            c, QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
    t.setColumnWidth(2, 210)
    t.verticalHeader().setMinimumSectionSize(26)
    t.verticalHeader().setDefaultSectionSize(30)
    t.setWordWrap(True)
    t.setStyleSheet("QTableWidget::item{padding:0px;}")
    t.setItemDelegate(LitDelegate(t))
    t.setItemDelegateForColumn(3, MatrixDelegate(t))
    t.setFont(mono_font(8))
    t.setMinimumHeight(292)
    for k in range(16):
        i = USER_TO_MINE[k]
        tr, det, e1, e2, rank = mat_props(i)
        cells = [k, SYMBOL[k], expr_cell(i), mat_str(i), det, tr,
                 eigen_str(i), rank,
                 format(k, "04b"), plain(sop_string(i)),
                 plain(anf_string(i).lower()),
                 " ".join("%+d" % c for c in walsh2(i)), plain(GATES[i][2]),
                 NPN_CLASS[i]]
        for c, v in enumerate(cells):
            it = QTableWidgetItem(str(v))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(k, c, it)
    return t


def _properties_table():
    t = QTableWidget(16, 6)
    t.setHorizontalHeaderLabels(["#", "T\u2080", "T\u2081", "M", "D", "L"])
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    for _c in range(6):
        t.horizontalHeader().setSectionResizeMode(_c, QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setMinimumSectionSize(26)
    t.verticalHeader().setDefaultSectionSize(30)
    t.setWordWrap(True)
    t.setStyleSheet("QTableWidget::item{padding:0px;}")
    t.setItemDelegate(LitDelegate(t))
    t.setFont(mono_font(8))
    t.setMinimumHeight(292)
    for k in range(16):
        i = USER_TO_MINE[k]
        cells = [k] + ["\u2713" if fn(i) else ""
                       for fn in (in_T0, in_T1, in_M, in_D, in_L)]
        for c, v in enumerate(cells):
            it = QTableWidgetItem(str(v))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(k, c, it)
    return t


def _bases_table():
    bases = minimal_complete_bases()
    rows = []
    for size in sorted(bases):
        for s in sorted(bases[size], key=lambda x: sorted(x)):
            rows.append((size, " + ".join(sorted(s))))
    t = QTableWidget(len(rows), 2)
    t.setHorizontalHeaderLabels(["n", "basis"])
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setMinimumSectionSize(14)
    t.verticalHeader().setDefaultSectionSize(16)
    t.setStyleSheet("QTableWidget::item{padding:0px;}")
    t.setItemDelegate(LitDelegate(t))
    t.setFont(mono_font(8))
    t.setMinimumHeight(309)
    for r, (sz, bs) in enumerate(rows):
        it0 = QTableWidgetItem(str(sz))
        it0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setItem(r, 0, it0)
        it1 = QTableWidgetItem(bs)
        it1.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                             Qt.AlignmentFlag.AlignVCenter)
        t.setItem(r, 1, it1)
    return t


# ===========================================================================
#  Tab: the tables  --  functions on top, then properties / bases / connectives
# ===========================================================================

class TablesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(8)

        self.sub = QTabWidget()
        self.sub.setDocumentMode(True)
        self.sub.tabBar().setExpanding(True)

        fc, fl = card("the 16 functions   (two variables)")
        self.rtable = _all_reps_table()
        self.rtable.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        fl.addWidget(self.rtable, 1)
        self.sub.addTab(fc, "representations")

        mc, ml = card("the 2\u00d72 matrix of each function"
                      "   \u2014   [[bit3, bit1], [bit4, bit2]]"
                      "      eigenvalues (1\u00b1\u221a5)/2 are \u03c6 and \u22121/\u03c6")
        self.mtable = _matrix_component()
        ml.addWidget(self.mtable, 1)
        self.sub.addTab(mc, "matrix")

        uc, ul = card("the 16 functions written inside each of the 17 "
                      "minimal complete bases")
        self.stable = _synth_table()
        ul.addWidget(self.stable, 1)
        _bases, _ = synthesis()
        legend = QLabel("   ".join("%d %s" % (i + 1, " + ".join(b))
                                   for i, b in enumerate(_bases)))
        legend.setFont(mono_font(8))
        legend.setWordWrap(True)
        legend.setStyleSheet("color:#666666;")
        ul.addWidget(legend)
        self.sub.addTab(uc, "universal")

        for _t in (self.rtable, self.mtable):
            install_header_actions(
                _t, on_change=lambda: self.set_highlight(getattr(self, "_mins", set())))
        root.addWidget(self.sub, 1)

    def set_highlight(self, mins):
        self._mins = set(mins)
        mins = set(mins)
        for t in (self.rtable, self.mtable):
            for k in range(16):
                i = USER_TO_MINE[k]
                hot = bool(mins) and set(minterms(i)) == mins
                for c in range(t.columnCount()):
                    it = t.item(k, c)
                    if it is not None:
                        it.setBackground(QColor("#f7e2b8") if hot
                                         else QColor("#ffffff"))


def _matrix_component():
    cols = ["#", "matrix", "weight", "det", "trace", "char poly",
            "eigenvalues", "rank", "rank GF(2)", "det GF(2)", "class",
            "M\u1d40M", "\u03c3", "inverse", "\u2016M\u2016"]
    t = QTableWidget(16, len(cols))
    t.setHorizontalHeaderLabels(cols)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    for c in range(len(cols)):
        t.horizontalHeader().setSectionResizeMode(
            c, QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.setItemDelegateForColumn(2, MatrixDelegate(t))
    t.setItemDelegateForColumn(11, MatrixDelegate(t))
    t.setFont(mono_font(9))
    for k in range(16):
        i = USER_TO_MINE[k]
        tr, det, e1, e2, rank = mat_props(i)
        cells = [k, mat_str(i), weight(i), det, tr, charpoly_str(i),
                 eigen_str(i), rank, rank_gf2(i), det_gf2(i), mat_class(i),
                 mat_t_str(i), sing_str(i), inv_str(i), frob_str(i)]
        for c, v in enumerate(cells):
            it = QTableWidgetItem(str(v))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(k, c, it)
    return t


# ===========================================================================
#  Tab: Universal -- the complete combinations of the connectives
# ===========================================================================

def _synth_table():
    """Rows: the 16 functions. Columns: the 17 minimal bases. Each cell is the
    function written using only that base's connectives."""
    bases, out = synthesis()
    t = QTableWidget(16, len(bases) + 1)
    t.setHorizontalHeaderLabels(["function \u2193 / base \u2192"]
                                + [str(i + 1) for i in range(len(bases))])
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    t.setFont(mono_font(8))
    t.setItemDelegate(LitDelegate(t))
    t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    for j in range(1, len(bases) + 1):
        t.horizontalHeader().setSectionResizeMode(j, QHeaderView.ResizeMode.ResizeToContents)
    t.verticalHeader().setMinimumSectionSize(18)
    t.verticalHeader().setDefaultSectionSize(21)
    for k in range(16):
        i = USER_TO_MINE[k]
        it = QTableWidgetItem(expr_cell(i))
        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        t.setItem(k, 0, it)
        for j in range(len(bases)):
            c = QTableWidgetItem(out[j][k])
            c.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t.setItem(k, j + 1, c)
    return t


class PropertiesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)
        pc, pl = card("Properties   T\u2080  T\u2081  M  D  L")
        pl.addWidget(_properties_table(), 1)
        row.addWidget(pc, 1)
        bc, bl = card("The 17 minimal bases (two-input connectives)")
        bl.addWidget(_bases_table(), 1)
        row.addWidget(bc, 1)
        gc, gl = card("Connectives")
        h = QHBoxLayout()
        h.setSpacing(18)
        cols = [QVBoxLayout() for _ in range(3)]
        for c in cols:
            c.setSpacing(5)
        self.boxes = {}
        for k, name in enumerate(CONNECTIVES):
            cb = QCheckBox(plain(name))
            cb.stateChanged.connect(self._check)
            self.boxes[name] = cb
            cols[k % 3].addWidget(cb)
        for c in cols:
            c.addStretch(1)
            h.addLayout(c)
        h.addStretch(1)
        gl.addLayout(h)
        self.verdict = QLabel()
        self.verdict.setWordWrap(True)
        gl.addWidget(self.verdict)
        gl.addStretch(1)
        row.addWidget(gc, 1)
        root.addLayout(row, 1)
        self.boxes["NAND"].setChecked(True)
        self._check()

    def _check(self, *_):
        chosen = [n for n, cb in self.boxes.items() if cb.isChecked()]
        if not chosen:
            self.verdict.setText("Pick at least one connective.")
            return
        ok, blocked = standard_complete(chosen)
        if ok:
            self.verdict.setText(
                "<b>Functionally complete</b> \u2014 escapes all of "
                "T\u2080, T\u2081, M, D, L.")
        else:
            self.verdict.setText(
                "<b>Not complete</b> \u2014 every chosen connective lies inside "
                "<b>%s</b>." % ", ".join(blocked))


# ===========================================================================
#  Application icon
# ===========================================================================

def make_app_icon():
    pm = QPixmap(64, 64)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#0f6cbd"))
    p.drawRoundedRect(QRectF(3, 3, 58, 58), 13, 13)

    white = QColor("#ffffff")
    p.setPen(QPen(white, 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    # input / output stubs
    p.drawLine(QPointF(13, 27), QPointF(21, 27))
    p.drawLine(QPointF(13, 37), QPointF(21, 37))
    p.drawLine(QPointF(45, 32), QPointF(52, 32))
    # the AND-gate body
    body = QPainterPath()
    body.moveTo(21, 22)
    body.lineTo(33, 22)
    body.arcTo(QRectF(21, 22, 22, 20), 90, -180)
    body.lineTo(21, 42)
    body.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(white))
    p.drawPath(body)
    p.end()
    return QIcon(pm)


# ===========================================================================
#  Overview -- the bit / trit representations, with the two levers
# ===========================================================================

FACE_POS = [("na", 0, 1), ("nc", 1, 1), ("a", 2, 1), ("c", 3, 1),
            ("b", 1, 0), ("nb", 1, 2)]
FACE_LABEL = {"a": "a", "na": "a\u0304", "b": "b", "nb": "b\u0304",
              "c": "c", "nc": "c\u0304"}


def face_values(mask, lit):
    """The four values on the face named by `lit` of a 3-variable function."""
    out = []
    for p_ in (1, 0):
        for q in (0, 1):
            if lit == "a":
                a, b, c = 1, p_, q
            elif lit == "na":
                a, b, c = 0, p_, q
            elif lit == "b":
                a, b, c = p_, 1, q
            elif lit == "nb":
                a, b, c = p_, 0, q
            elif lit == "c":
                a, b, c = p_, q, 1
            else:
                a, b, c = p_, q, 0
            out.append((mask >> ((a << 2) | (b << 1) | c)) & 1)
    return out


class BitMatrixWidget(QWidget):
    """A 2-input function as a 2x2 block of bits, or a 3x3 block of trits."""

    def __init__(self, idx=0, base=2, parent=None):
        super().__init__(parent)
        self.idx = idx
        self.base = base
        self.setMinimumSize(96, 28 if base == 2 else 44)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#ffffff"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        if self.base == 3:
            vals = [0, HALF, 1]
            cw = self.width() / 3.0
            ch = self.height() / 3.0
            for r, bv in enumerate(reversed(vals)):
                for c, av in enumerate(vals):
                    v = base3(self.idx, av, bv)
                    rect = QRectF(c * cw, r * ch, cw, ch)
                    if v == 1:
                        p.fillRect(rect.adjusted(1, 1, -1, -1), QColor(47, 125, 79, 30))
                    elif v == HALF:
                        p.fillRect(rect.adjusted(1, 1, -1, -1), QColor(138, 109, 30, 26))
                    p.setPen(QPen(GRID, 1))
                    p.drawRect(rect)
                    p.setFont(mono_font(max(9, int(min(cw, ch) * 0.5))))
                    p.setPen(QPen(INK if v else QColor("#c2c2c2")))
                    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, fmt3(v))
        else:
            tl, tr, bl, br = bit_matrix(self.idx)
            cw = self.width() / 2.0
            ch = self.height() / 2.0
            for v, c, r in [(tl, 0, 0), (tr, 1, 0), (bl, 0, 1), (br, 1, 1)]:
                rect = QRectF(c * cw, r * ch, cw, ch)
                if v:
                    p.fillRect(rect.adjusted(1, 1, -1, -1), QColor(47, 125, 79, 30))
                p.setPen(QPen(GRID, 1))
                p.drawRect(rect)
                p.setFont(mono_font(max(11, int(min(cw, ch) * 0.5))))
                p.setPen(QPen(INK if v else QColor("#c2c2c2")))
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(v))
        p.end()


class FaceCubeWidget(QWidget):
    """A 3-input function as a cube whose six faces are the literals."""

    def __init__(self, mask=0, parent=None):
        super().__init__(parent)
        self.mask = mask
        self.setMinimumSize(196, 150)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#ffffff"))
        W, H = self.width(), self.height()
        sq = min(W / 4.0, H / 3.0)
        ox = (W - sq * 4) / 2.0
        oy = (H - sq * 3) / 2.0
        for lit, cc, rr in FACE_POS:
            x, y = ox + cc * sq, oy + rr * sq
            p.setPen(QPen(QColor("#8a8a8a"), 1))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRectF(x, y, sq, sq))
            p.setFont(mono_font(8))
            p.setPen(QPen(INK))
            p.drawText(QRectF(x, y, sq, 12), Qt.AlignmentFlag.AlignCenter,
                       FACE_LABEL[lit])
            vals = face_values(self.mask, lit)
            cw, ch = sq / 2.0, (sq - 12) / 2.0
            for k, v in enumerate(vals):
                r2, c2 = divmod(k, 2)
                cell = QRectF(x + c2 * cw, y + 12 + r2 * ch, cw, ch)
                if v:
                    p.fillRect(cell.adjusted(1, 1, -1, -1), QColor(47, 125, 79, 30))
                p.setPen(QPen(GRID, 1))
                p.drawRect(cell)
                p.setFont(mono_font(8))
                p.setPen(QPen(INK if v else QColor("#c2c2c2")))
                p.drawText(cell, Qt.AlignmentFlag.AlignCenter, str(v))
        p.end()


class RepresentationTab(QWidget):
    selChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nvars = 2
        self.base = 2
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(6)

        self.lits = set()
        self.extra = set()
        self.barh = QWidget()
        self.barl = QHBoxLayout(self.barh)
        self.barl.setContentsMargins(0, 0, 0, 0)
        self.barl.setSpacing(4)
        root.addWidget(self.barh)

        self.venn = VennTab()
        self.cube = HypercubeTab()
        self.lat = LatticeWidget(2)
        self.venn.venn.atomClicked.connect(self._venn_click)
        self.cube.cube.valuesChanged.connect(self._values_changed)
        self.lat.nodeClicked.connect(self._node_click)
        reps = QHBoxLayout()
        reps.setSpacing(10)
        reps.addWidget(self._panel("Venn", self.venn), 1)
        reps.addWidget(self._panel("cube  (hypercube)", self.cube), 1)
        reps.addWidget(self._panel("tree  (lattice)", self.lat), 1)
        rh = QWidget()
        rh.setLayout(reps)
        rh.setMinimumHeight(270)
        root.addWidget(rh, 1)

        self._apply_n(2)
        self._build()

    def _panel(self, title, widget):
        box, lay = card(title)
        lay.addWidget(widget, 1)
        return box

    def _apply_n(self, n):
        self.nvars = n
        self.lits = set()
        self.extra = set()
        self.venn.set_sets(n)
        self.cube.set_dim(min(n, 4))
        self.lat.set_n(n)
        self._build_bar()
        self._apply_sel()

    def _build_bar(self):
        while self.barl.count():
            it = self.barl.takeAt(0)
            w = it.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self.vbtns = {}
        lab = QLabel("variable:")
        lab.setFont(mono_font(9))
        self.barl.addWidget(lab)
        for k in range(self.nvars):
            for lit in (1, 0):
                b = QToolButton()
                b.setText("abcd"[k] if lit else "not " + "abcd"[k])
                b.setCheckable(True)
                b.setFont(mono_font(9))
                b.setStyleSheet("QToolButton:checked{background:#e0a53a;"
                                "color:#000000;}")
                b.clicked.connect(lambda _=False, kk=k, ll=lit: self._lit_click(kk, ll))
                self.vbtns[(k, lit)] = b
                self.barl.addWidget(b)
        self.barl.addStretch(1)

    def _sel_mins(self):
        n = self.nvars
        mins = set(range(1 << n))
        for (k, lit) in self.lits:
            mins &= {i for i in range(1 << n)
                     if ((i >> (n - 1 - k)) & 1) == lit}
        if not self.lits:
            mins = set()
        return mins | self.extra

    def _lit_click(self, k, lit):
        key = (k, lit)
        if key in self.lits:
            self.lits.discard(key)
        else:
            self.lits.add(key)
        self._apply_sel()

    def _venn_click(self, mask):
        self._toggle(revbits(mask, self.nvars))

    def _node_click(self, i):
        self._toggle(i)

    def _toggle(self, i):
        if i in self.extra:
            self.extra.discard(i)
        else:
            self.extra.add(i)
        self._apply_sel()

    def _values_changed(self):
        self._apply_sel()

    def _apply_sel(self):
        n = self.nvars
        mins = self._sel_mins()
        vals = getattr(self.cube.cube, "values", [])
        ones = {i for i, v in enumerate(vals) if v}
        self.venn.venn.set_highlight({revbits(i, n) for i in ones})
        self.cube.cube.set_highlight(mins)
        self.lat.set_highlight(ones)
        for (k, lit), b in self.vbtns.items():
            b.setChecked((k, lit) in self.lits)
        self.selChanged.emit(mins)

    def set_vars(self, n):
        self._apply_n(n)
        self._build()

    def set_base(self, b):
        self.base = b
        self._build()

    def _build(self):
        pass

STYLE = """
QWidget {
    font-family: "Segoe UI", "Noto Sans", "DejaVu Sans", sans-serif;
    font-size: 12px; color: #1a1a1a;
}
QMainWindow { background: #ffffff; }

QMenuBar { background: #f0f0f0; border-bottom: 1px solid #d8d8d8; }
QMenuBar::item { padding: 4px 10px; background: transparent; }
QMenuBar::item:selected { background: #e0e0e0; }
QMenu { background: #ffffff; border: 1px solid #c4c4c4; }
QMenu::item { padding: 5px 22px 5px 12px; }
QMenu::item:selected { background: #e0e0e0; color: #000000; }

#TopBar { background: #f0f0f0; border-bottom: 1px solid #d8d8d8; }
#Brand { font-size: 14px; font-weight: 600; color: #1a1a1a; }
QListWidget#Nav { background: transparent; border: none; outline: 0; }
QListWidget#Nav::item { padding: 6px 14px; color: #333333; }
QListWidget#Nav::item:hover:!selected { background: #e6e6e6; }
QListWidget#Nav::item:selected { background: #d6d6d6; color: #000000; }

#PageHeader { font-size: 14px; font-weight: 600; color: #1a1a1a; }
#HeaderRule { background: #d8d8d8; }

QGroupBox {
    border: 1px solid #d0d0d0; background: #ffffff; margin-top: 10px;
    padding: 7px 9px 9px 9px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 9px; padding: 0 3px; color: #333333; font-weight: 600;
}

QPushButton {
    background: #ececec; border: 1px solid #bdbdbd; padding: 4px 14px; color: #1a1a1a;
}
QPushButton:hover { background: #f2f2f2; }
QPushButton:pressed { background: #dcdcdc; }

QToolButton {
    background: #ffffff; border: 1px solid #c4c4c4; padding: 4px 6px; color: #333333;
}
QToolButton:hover { background: #f0f0f0; }
QToolButton:checked { background: #d6d6d6; border: 1px solid #8a8a8a; font-weight: 600; }

QComboBox, QSpinBox, QLineEdit {
    background: #ffffff; border: 1px solid #bdbdbd; padding: 3px 6px;
}
QHeaderView::section {
    background: #ececec; border: none; border-right: 1px solid #d8d8d8;
    border-bottom: 1px solid #d0d0d0; padding: 4px 6px; color: #333333; font-weight: 600;
}
QTableWidget { background: #ffffff; gridline-color: #e0e0e0; border: 1px solid #c4c4c4; }
QCheckBox { spacing: 6px; }
QStatusBar { background: #f0f0f0; color: #555555; border-top: 1px solid #d8d8d8; }
QStatusBar::item { border: none; }
"""


def make_page(title, content):
    page = QWidget()
    lay = QVBoxLayout(page)
    lay.setContentsMargins(20, 16, 20, 18)
    lay.setSpacing(10)
    head = QLabel(title)
    head.setObjectName("PageHeader")
    lay.addWidget(head)
    rule = QFrame()
    rule.setObjectName("HeaderRule")
    rule.setFixedHeight(1)
    lay.addWidget(rule)
    lay.addWidget(content, 1)
    return page


# ===========================================================================
#  Main window
# ===========================================================================

# ===========================================================================
#  Main window
# ===========================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logic")
        self.setWindowIcon(make_app_icon())

        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        top = QFrame()
        top.setObjectName("TopBar")
        tl = QHBoxLayout(top)
        tl.setContentsMargins(14, 6, 14, 6)
        tl.setSpacing(10)
        t = QLabel("Logic")
        t.setObjectName("Brand")
        tl.addWidget(t)
        tl.addSpacing(24)
        tl.addWidget(QLabel("variables"))
        self.varsel = Segmented([("2", 2), ("3", 3)])
        self.varsel.set_value(2)
        self.varsel.changed.connect(self._set_vars)
        tl.addWidget(self.varsel)
        tl.addStretch(1)
        outer.addWidget(top)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setExpanding(True)

        self.rep = RepresentationTab()
        self.tables = TablesTab()
        self.props = PropertiesTab()
        self.tabs.addTab(self.rep, "Representation")
        self.tabs.addTab(self.tables, "Tables")
        self.tabs.addTab(self.props, "Properties")
        self.rep.selChanged.connect(self.tables.set_highlight)
        outer.addWidget(self.tabs, 1)
        self.setCentralWidget(central)

        mb = self.menuBar()
        fm = mb.addMenu("&File")
        act = QAction("E&xit", self)
        act.setShortcut("Ctrl+Q")
        act.triggered.connect(self.close)
        fm.addAction(act)
        hm = mb.addMenu("&Help")
        ab = QAction("&About", self)
        ab.triggered.connect(self._about)
        hm.addAction(ab)
        self.statusBar().showMessage("Logic")

    def _set_vars(self, n):
        self.rep.set_vars(n)

    def _set_base(self, b):
        self.rep.set_base(b)

    def _about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About Logic")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("<b>Logic</b>")
        msg.setInformativeText(
            "Representation, the function tables, and the five properties.\n\n"
            "A desktop tool for the Logic project.")
        msg.exec()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Logic")
    app.setApplicationDisplayName("Logic")
    app.setStyleSheet(STYLE)
    app.setFont(QFont("Segoe UI", 9))
    win = MainWindow()
    win.setMinimumSize(1040, 700)
    win.resize(1340, 860)
    win.show()
    return app.exec() if QT6 else app.exec_()


if __name__ == "__main__":
    sys.exit(main())
