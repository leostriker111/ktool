"""Exporta una ecuacion (Solution) a varios lenguajes de descripcion."""

from __future__ import annotations

from .simplify import literal_pairs

LANG_ORDER = ["Matematico", "Verilog", "VHDL", "ABEL", "Logisim", "C", "Python", "LaTeX"]


def _wrap(lits, op):
    return lits[0] if len(lits) == 1 else "(" + op.join(lits) + ")"


SPECS = {
    "Matematico": {
        "var": lambda v, c: v + "'" if c else v,
        "and_term": lambda l: "".join(l),
        "or_join": lambda t: " + ".join(t),
        "or_term": lambda l: "(" + " + ".join(l) + ")",
        "and_join": lambda t: "".join(t),
        "xor": " ^ ",
        "inv": lambda b: "(" + b + ")'",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"{n} = {r}",
    },
    "Verilog": {
        "var": lambda v, c: "~" + v if c else v,
        "and_term": lambda l: _wrap(l, " & "),
        "or_join": lambda t: " | ".join(t),
        "or_term": lambda l: _wrap(l, " | "),
        "and_join": lambda t: " & ".join(t),
        "xor": " ^ ",
        "inv": lambda b: "~(" + b + ")",
        "const": {0: "1'b0", 1: "1'b1"},
        "assign": lambda n, r: f"assign {n} = {r};",
    },
    "VHDL": {
        "var": lambda v, c: "not " + v if c else v,
        "and_term": lambda l: _wrap(l, " and "),
        "or_join": lambda t: " or ".join(t),
        "or_term": lambda l: _wrap(l, " or "),
        "and_join": lambda t: " and ".join(t),
        "xor": " xor ",
        "inv": lambda b: "not (" + b + ")",
        "const": {0: "'0'", 1: "'1'"},
        "assign": lambda n, r: f"{n} <= {r};",
    },
    "ABEL": {
        "var": lambda v, c: "!" + v if c else v,
        "and_term": lambda l: _wrap(l, " & "),
        "or_join": lambda t: " # ".join(t),
        "or_term": lambda l: _wrap(l, " # "),
        "and_join": lambda t: " & ".join(t),
        "xor": " $ ",
        "inv": lambda b: "!(" + b + ")",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"{n} = {r};",
    },
    "Logisim": {
        "var": lambda v, c: "~" + v if c else v,
        "and_term": lambda l: " ".join(l),
        "or_join": lambda t: " + ".join(t),
        "or_term": lambda l: l[0] if len(l) == 1 else "(" + " + ".join(l) + ")",
        "and_join": lambda t: " ".join(t),
        "xor": " ^ ",
        "inv": lambda b: "~(" + b + ")",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"{n} = {r}",
    },
    "C": {
        "var": lambda v, c: "!" + v if c else v,
        "and_term": lambda l: _wrap(l, " && "),
        "or_join": lambda t: " || ".join(t),
        "or_term": lambda l: _wrap(l, " || "),
        "and_join": lambda t: " && ".join(t),
        "xor": " ^ ",
        "inv": lambda b: "!(" + b + ")",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"bool {n} = {r};",
    },
    "Python": {
        "var": lambda v, c: "not " + v if c else v,
        "and_term": lambda l: _wrap(l, " and "),
        "or_join": lambda t: " or ".join(t),
        "or_term": lambda l: _wrap(l, " or "),
        "and_join": lambda t: " and ".join(t),
        "xor": " ^ ",
        "inv": lambda b: "not (" + b + ")",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"{n} = {r}",
    },
    "LaTeX": {
        "var": lambda v, c: "\\overline{" + v + "}" if c else v,
        "and_term": lambda l: "".join(l),
        "or_join": lambda t: " + ".join(t),
        "or_term": lambda l: "\\left(" + " + ".join(l) + "\\right)",
        "and_join": lambda t: "".join(t),
        "xor": " \\oplus ",
        "inv": lambda b: "\\overline{" + b + "}",
        "const": {0: "0", 1: "1"},
        "assign": lambda n, r: f"{n} = {r}",
    },
}


def render(solution, name, lang):
    s = SPECS[lang]
    if solution.const is not None:
        return s["assign"](name, s["const"][solution.const])

    if solution.form == "xor":
        body = s["xor"].join(s["var"](v, False) for v in solution.xor_vars)
        rhs = s["inv"](body) if solution.xnor else body
        return s["assign"](name, rhs)

    if solution.form == "sop":
        if not solution.patterns:
            return s["assign"](name, s["const"][0])
        terms = []
        for p in solution.patterns:
            lits = [s["var"](v, c) for v, c in literal_pairs(p, solution.variables)]
            terms.append(s["and_term"](lits))
        return s["assign"](name, s["or_join"](terms))

    # pos
    if not solution.patterns:
        return s["assign"](name, s["const"][1])
    terms = []
    for p in solution.patterns:
        lits = [s["var"](v, c) for v, c in literal_pairs(p, solution.variables, polarity_invert=True)]
        terms.append(s["or_term"](lits))
    return s["assign"](name, s["and_join"](terms))


def render_all(solution, name):
    """Devuelve lista de (lenguaje, codigo) para la solucion dada."""
    return [(lang, render(solution, name, lang)) for lang in LANG_ORDER]
