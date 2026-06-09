"""Formato de ecuaciones, deteccion XOR/XNOR, reuso de terminos y costo."""

from __future__ import annotations

from . import qm


def term_literals(pattern, variables, polarity_invert=False):
    """Patron '10-1' -> lista de literales. polarity_invert para sumandos POS."""
    lits = []
    for i, c in enumerate(pattern):
        if c == "-":
            continue
        v = variables[i]
        one_is_true = (c == "1") != polarity_invert
        lits.append(v if one_is_true else v + "'")
    return lits


def format_product(pattern, variables):
    lits = term_literals(pattern, variables)
    return "".join(lits) if lits else "1"


def format_sum(pattern, variables):
    lits = term_literals(pattern, variables, polarity_invert=True)
    return "(" + " + ".join(lits) + ")" if lits else "0"


class Solution:
    """Resultado de minimizar una salida en una forma (SOP o POS)."""

    def __init__(self, form, patterns, variables, const=None):
        self.form = form  # 'sop' | 'pos'
        self.patterns = patterns
        self.variables = variables
        self.const = const  # 0 / 1 cuando es constante

    @property
    def equation(self):
        if self.const is not None:
            return str(self.const)
        if not self.patterns:
            return "0" if self.form == "sop" else "1"
        if self.form == "sop":
            terms = [format_product(p, self.variables) for p in self.patterns]
            return " + ".join(terms)
        terms = [format_sum(p, self.variables) for p in self.patterns]
        return "".join(terms)

    def cost(self):
        """(compuertas, literales) aprox. Para elegir la forma mas barata."""
        if self.const is not None or not self.patterns:
            return (0, 0)
        literals = sum(qm.literal_count(p) for p in self.patterns)
        multi = [p for p in self.patterns if qm.literal_count(p) > 1]
        inner_gates = len(multi)  # AND (sop) u OR (pos) de >1 literal
        outer = 1 if len(self.patterns) > 1 else 0
        return (inner_gates + outer, literals)


def solve_output(values, variables):
    """Devuelve dict con soluciones SOP y POS y la recomendada por costo."""
    nbits = len(variables)
    minterms = [i for i, v in enumerate(values) if v == 1]
    zeros = [i for i, v in enumerate(values) if v == 0]
    dontcares = [i for i, v in enumerate(values) if v == "x"]

    if not minterms:
        sop = Solution("sop", [], variables, const=0)
        pos = Solution("pos", [], variables, const=0)
    elif not zeros:
        sop = Solution("sop", [], variables, const=1)
        pos = Solution("pos", [], variables, const=1)
    else:
        sop_pat = qm.minimize(minterms, dontcares, nbits, required=minterms)
        pos_pat = qm.minimize(zeros, dontcares, nbits, required=zeros)
        sop = Solution("sop", sop_pat, variables)
        pos = Solution("pos", pos_pat, variables)

    best = sop if sop.cost() <= pos.cost() else pos
    return {
        "sop": sop,
        "pos": pos,
        "best": best,
        "parity": detect_parity(values, variables),
    }


def detect_parity(values, variables):
    """Si la funcion es XOR/XNOR de un subconjunto de variables, lo regresa.
    Devuelve dict {subset: [nombres], xnor: bool, equation: str} o None."""
    n = len(variables)
    cares = [(i, v) for i, v in enumerate(values) if v in (0, 1)]
    if not cares:
        return None
    best = None
    for subset in range(1, 1 << n):
        mask = 0
        for k in range(n):
            if (subset >> k) & 1:
                mask |= 1 << (n - 1 - k)
        ok_xor = ok_xnor = True
        for i, v in cares:
            parity = bin(i & mask).count("1") & 1
            if v != parity:
                ok_xor = False
            if v != (parity ^ 1):
                ok_xnor = False
            if not ok_xor and not ok_xnor:
                break
        if ok_xor or ok_xnor:
            cnt = bin(subset).count("1")
            if cnt >= 2 and (best is None or cnt < best[0]):
                names = [variables[k] for k in range(n) if (subset >> k) & 1]
                best = (cnt, names, ok_xnor and not ok_xor)
    if best is None:
        return None
    _, names, is_xnor = best
    body = " ^ ".join(names)
    eq = f"({body})'" if is_xnor else body
    return {"subset": names, "xnor": is_xnor, "equation": eq}


def shared_terms(solutions, variables, form="sop"):
    """Encuentra patrones que aparecen en >=2 salidas (compuertas reutilizables).
    solutions = dict nombre_salida -> dict de solve_output."""
    seen = {}
    for out_name, sol in solutions.items():
        s = sol[form]
        if s.const is not None:
            continue
        for p in s.patterns:
            if qm.literal_count(p) < 2:
                continue  # un literal no es compuerta reutilizable
            seen.setdefault(p, []).append(out_name)
    shared = []
    for p, outs in seen.items():
        if len(outs) >= 2:
            text = format_product(p, variables) if form == "sop" else format_sum(p, variables)
            shared.append({"pattern": p, "outputs": outs, "term": text})
    shared.sort(key=lambda d: (-len(d["outputs"]), d["term"]))
    return shared
