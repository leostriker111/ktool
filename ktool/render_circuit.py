"""Render del circuito a SVG: rieles de literales + compuertas AND/OR."""

from __future__ import annotations

from .simplify import term_literals


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def _and_path(x, y, w, h):
    r = h / 2
    return (
        f'M {x},{y} L {x + w - r},{y} '
        f'A {r},{r} 0 0 1 {x + w - r},{y + h} '
        f'L {x},{y + h} Z'
    )


def _or_path(x, y, w, h):
    return (
        f'M {x},{y} Q {x + w*0.45},{y} {x + w},{y + h/2} '
        f'Q {x + w*0.45},{y + h} {x},{y + h} '
        f'Q {x + w*0.32},{y + h/2} {x},{y} Z'
    )


def solution_terms(solution):
    """Lista de terminos como listas de literales (str)."""
    invert = solution.form == "pos"
    terms = []
    for p in solution.patterns:
        lits = term_literals(p, solution.variables, polarity_invert=invert)
        terms.append(lits or ["1"])
    return terms


def circuit_svg(solution, output_name="Y"):
    form = solution.form
    if solution.const is not None:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="60" '
            f'font-family="Georgia">'
            f'<text x="10" y="35" font-size="16">{_esc(output_name)} = '
            f'constante {solution.const}</text></svg>'
        )

    terms = solution_terms(solution)
    if not terms:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="50">'
            f'<text x="10" y="30" font-family="Georgia" font-size="15">{_esc(output_name)} = 0</text></svg>'
        )

    inner_gate = "and" if form == "sop" else "or"
    outer_gate = "or" if form == "sop" else "and"

    # literales usados (rieles)
    literals = []
    for t in terms:
        for lit in t:
            if lit not in literals:
                literals.append(lit)
    literals.sort(key=lambda s: (s.rstrip("'"), s.endswith("'")))

    rail_gap = 28
    x0 = 16
    rail_x = {lit: x0 + i * rail_gap for i, lit in enumerate(literals)}
    rails_right = x0 + len(literals) * rail_gap + 24

    gate_w = 48
    top_pad = 40
    term_h = []
    term_y = []
    y = top_pad
    for t in terms:
        h = max(28, len(t) * 16)
        term_y.append(y)
        term_h.append(h)
        y += h + 26
    bottom = y + 20

    or_x = rails_right + gate_w + 60
    or_h = max(36, len(terms) * 18)
    or_y = (term_y[0] + term_y[-1] + term_h[-1]) / 2 - or_h / 2
    out_x = or_x + gate_w + 40

    width = out_x + 70
    height = max(bottom, or_y + or_h + 30)

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'font-family="Georgia, serif">'
    ]

    # rieles verticales con etiqueta arriba
    for lit in literals:
        x = rail_x[lit]
        s.append(
            f'<line x1="{x}" y1="34" x2="{x}" y2="{bottom}" stroke="#bbb" stroke-width="1"/>'
        )
        s.append(
            f'<text x="{x}" y="26" font-size="13" text-anchor="middle">{_esc(lit)}</text>'
        )

    single_term = len(terms) == 1

    for j, t in enumerate(terms):
        gy = term_y[j]
        gh = term_h[j]
        gx = rails_right
        out_point_x = gx + gate_w
        out_point_y = gy + gh / 2

        if len(t) == 1:
            # un literal: conexion directa al riel, sin compuerta
            lit = t[0]
            x = rail_x[lit]
            s.append(
                f'<circle cx="{x}" cy="{out_point_y}" r="3" fill="#000"/>'
            )
            s.append(
                f'<line x1="{x}" y1="{out_point_y}" x2="{out_point_x}" y2="{out_point_y}" '
                f'stroke="#000" stroke-width="1.5"/>'
            )
        else:
            path = _and_path(gx, gy, gate_w, gh) if inner_gate == "and" else _or_path(gx, gy, gate_w, gh)
            s.append(f'<path d="{path}" fill="#222" stroke="#000"/>')
            ninp = len(t)
            for k, lit in enumerate(t):
                iy = gy + gh * (k + 1) / (ninp + 1)
                x = rail_x[lit]
                s.append(f'<circle cx="{x}" cy="{iy}" r="3" fill="#000"/>')
                s.append(
                    f'<line x1="{x}" y1="{iy}" x2="{gx}" y2="{iy}" '
                    f'stroke="#000" stroke-width="1.5"/>'
                )

        if single_term:
            s.append(
                f'<line x1="{out_point_x}" y1="{out_point_y}" x2="{out_x}" y2="{out_point_y}" '
                f'stroke="#000" stroke-width="1.5"/>'
            )
            s.append(
                f'<text x="{out_x + 6}" y="{out_point_y + 5}" font-size="15">{_esc(output_name)}</text>'
            )

    if not single_term:
        # compuerta final
        opath = _or_path(or_x, or_y, gate_w, or_h) if outer_gate == "or" else _and_path(or_x, or_y, gate_w, or_h)
        s.append(f'<path d="{opath}" fill="#222" stroke="#000"/>')
        for j in range(len(terms)):
            iy = or_y + or_h * (j + 1) / (len(terms) + 1)
            oy = term_y[j] + term_h[j] / 2
            ox = rails_right + gate_w
            # salida de la compuerta interna hacia la final
            s.append(
                f'<line x1="{ox}" y1="{oy}" x2="{or_x - 8}" y2="{oy}" '
                f'stroke="#000" stroke-width="1.5"/>'
            )
            s.append(
                f'<line x1="{or_x - 8}" y1="{oy}" x2="{or_x - 8}" y2="{iy}" '
                f'stroke="#000" stroke-width="1.5"/>'
            )
            s.append(
                f'<line x1="{or_x - 8}" y1="{iy}" x2="{or_x}" y2="{iy}" '
                f'stroke="#000" stroke-width="1.5"/>'
            )
        oy = or_y + or_h / 2
        s.append(
            f'<line x1="{or_x + gate_w}" y1="{oy}" x2="{out_x}" y2="{oy}" '
            f'stroke="#000" stroke-width="1.5"/>'
        )
        s.append(
            f'<text x="{out_x + 6}" y="{oy + 5}" font-size="15">{_esc(output_name)}</text>'
        )

    s.append("</svg>")
    return "\n".join(s)
