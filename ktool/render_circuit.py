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


def _xor_gate(x, y, w, h):
    body = _or_path(x + 5, y, w - 5, h)
    return (
        f'<path d="{body}" fill="#222" stroke="#000"/>'
        f'<path d="M {x},{y} Q {x + w*0.30},{y + h/2} {x},{y + h}" '
        f'fill="none" stroke="#000" stroke-width="1.6"/>'
    )


def _not_gate(x, y, h):
    return (
        f'<path d="M {x},{y} L {x},{y + h} L {x + h*0.85},{y + h/2} Z" '
        f'fill="#222" stroke="#000"/>'
        f'<circle cx="{x + h*0.85 + 4}" cy="{y + h/2}" r="4" fill="white" stroke="#000"/>'
    )


def solution_terms(solution):
    """Lista de terminos como listas de literales (str)."""
    invert = solution.form == "pos"
    terms = []
    for p in solution.patterns:
        lits = term_literals(p, solution.variables, polarity_invert=invert)
        terms.append(lits or ["1"])
    return terms


def _xor_chain_svg(solution, output_name):
    vs = solution.xor_vars
    k = len(vs)
    gate_w, gate_h, gap = 44, 40, 66
    y = 48
    x0 = 70
    gates = max(1, k - 1)
    width = x0 + gates * (gate_w + gap) + (40 if solution.xnor else 0) + 60
    height = y + gate_h + 50

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'font-family="Georgia, serif">'
    ]
    prev_out = None
    gx = x0
    for j in range(gates):
        top_y = y + gate_h * 0.3
        bot_y = y + gate_h * 0.72
        s.append(_xor_gate(gx, y, gate_w, gate_h))
        # entrada superior
        if prev_out is None:
            s.append(f'<line x1="{gx-30}" y1="{top_y}" x2="{gx}" y2="{top_y}" stroke="#000" stroke-width="1.5"/>')
            s.append(f'<text x="{gx-36}" y="{top_y+4}" font-size="13" text-anchor="end">{_esc(vs[0])}</text>')
        else:
            s.append(f'<line x1="{prev_out[0]}" y1="{prev_out[1]}" x2="{gx}" y2="{top_y}" stroke="#000" stroke-width="1.5"/>')
        # entrada inferior (variable nueva)
        new_var = vs[1] if prev_out is None else vs[j + 1]
        s.append(f'<line x1="{gx-30}" y1="{bot_y}" x2="{gx}" y2="{bot_y}" stroke="#000" stroke-width="1.5"/>')
        s.append(f'<text x="{gx-36}" y="{bot_y+4}" font-size="13" text-anchor="end">{_esc(new_var)}</text>')
        prev_out = (gx + gate_w, y + gate_h / 2)
        gx += gate_w + gap

    out_x, out_y = prev_out
    if solution.xnor:
        s.append(f'<line x1="{out_x}" y1="{out_y}" x2="{out_x+18}" y2="{out_y}" stroke="#000" stroke-width="1.5"/>')
        s.append(_not_gate(out_x + 18, out_y - 12, 24))
        out_x = out_x + 18 + 24 * 0.85 + 8
    s.append(f'<line x1="{out_x}" y1="{out_y}" x2="{out_x+34}" y2="{out_y}" stroke="#000" stroke-width="1.5"/>')
    s.append(f'<text x="{out_x+40}" y="{out_y+5}" font-size="15">{_esc(output_name)}</text>')
    s.append("</svg>")
    return "\n".join(s)


def circuit_svg(solution, output_name="Y"):
    form = solution.form
    if solution.const is not None:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="60" '
            f'font-family="Georgia">'
            f'<text x="10" y="35" font-size="16">{_esc(output_name)} = '
            f'constante {solution.const}</text></svg>'
        )

    if form == "xor":
        return _xor_chain_svg(solution, output_name)

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


def build_shared_circuit(named_sops):
    """Circuito combinado en SOP con compuertas AND compartidas entre salidas.

    named_sops: lista de (nombre, Solution sop).
    Devuelve (svg, gates) donde gates = [{'id','term','outputs'}].
    """
    rails = []
    gate_terms = []        # {'lits','outputs'}
    gate_index = {}
    out_plan = []          # (name, inputs, const)
    for name, sol in named_sops:
        if sol.const is not None:
            out_plan.append((name, [], sol.const))
            continue
        terms = solution_terms(sol)
        if not terms:
            out_plan.append((name, [], 0))
            continue
        inputs = []
        for lits in terms:
            for lit in lits:
                if lit not in rails:
                    rails.append(lit)
            if len(lits) == 1:
                inputs.append(("lit", lits[0]))
            else:
                key = tuple(lits)
                if key not in gate_index:
                    gate_index[key] = len(gate_terms)
                    gate_terms.append({"lits": list(lits), "outputs": []})
                gi = gate_index[key]
                if name not in gate_terms[gi]["outputs"]:
                    gate_terms[gi]["outputs"].append(name)
                inputs.append(("gate", gi))
        out_plan.append((name, inputs, None))

    rail_gap, x0, top, gate_w = 26, 16, 46, 46
    rail_x = {lit: x0 + i * rail_gap for i, lit in enumerate(rails)}
    rails_right = x0 + len(rails) * rail_gap + 30

    and_pos = []
    y = top
    for g in gate_terms:
        gh = max(26, len(g["lits"]) * 14)
        and_pos.append((rails_right, y, gh))
        y += gh + 18
    and_bottom = y
    and_out_x = rails_right + gate_w

    x_or = and_out_x + 130
    or_gate_w = 46
    slots = []
    oy = top
    for name, inputs, const in out_plan:
        if const is not None:
            slots.append({"name": name, "kind": "const", "y": oy, "h": 24, "const": const})
            oy += 42
        elif len(inputs) == 1:
            slots.append({"name": name, "kind": "direct", "y": oy, "h": 24, "inputs": inputs})
            oy += 42
        else:
            h = max(28, len(inputs) * 15)
            slots.append({"name": name, "kind": "or", "y": oy, "h": h, "inputs": inputs})
            oy += h + 22
    out_bottom = oy
    x_out = x_or + or_gate_w + 80
    height = max(and_bottom, out_bottom) + 26
    width = x_out + 90
    bottom_channel = height - 14

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'font-family="Georgia, serif">'
    ]
    for lit in rails:
        x = rail_x[lit]
        s.append(f'<line x1="{x}" y1="34" x2="{x}" y2="{bottom_channel}" stroke="#bbb" stroke-width="1"/>')
        s.append(f'<text x="{x}" y="26" font-size="13" text-anchor="middle">{_esc(lit)}</text>')

    and_out_pts = []
    for gi, (gx, gy, gh) in enumerate(and_pos):
        lits = gate_terms[gi]["lits"]
        s.append(f'<path d="{_and_path(gx, gy, gate_w, gh)}" fill="#222" stroke="#000"/>')
        s.append(f'<text x="{gx + 6}" y="{gy - 3}" font-size="10" fill="#555">G{gi + 1}</text>')
        n = len(lits)
        for k, lit in enumerate(lits):
            iy = gy + gh * (k + 1) / (n + 1)
            rx = rail_x[lit]
            s.append(f'<circle cx="{rx}" cy="{iy}" r="3" fill="#000"/>')
            s.append(f'<line x1="{rx}" y1="{iy}" x2="{gx}" y2="{iy}" stroke="#000" stroke-width="1.4"/>')
        and_out_pts.append((and_out_x, gy + gh / 2))

    def route(inp, tx, ty, k):
        ch = tx - 22 - k * 7
        if inp[0] == "gate":
            sx, sy = and_out_pts[inp[1]]
            s.append(f'<circle cx="{sx}" cy="{sy}" r="2.5" fill="#000"/>')
            s.append(f'<line x1="{sx}" y1="{sy}" x2="{ch}" y2="{sy}" stroke="#000" stroke-width="1.4"/>')
            s.append(f'<line x1="{ch}" y1="{sy}" x2="{ch}" y2="{ty}" stroke="#000" stroke-width="1.4"/>')
            s.append(f'<line x1="{ch}" y1="{ty}" x2="{tx}" y2="{ty}" stroke="#000" stroke-width="1.4"/>')
        else:
            rx = rail_x[inp[1]]
            s.append(f'<circle cx="{rx}" cy="{bottom_channel}" r="2.5" fill="#000"/>')
            s.append(f'<line x1="{rx}" y1="{bottom_channel}" x2="{ch}" y2="{bottom_channel}" stroke="#000" stroke-width="1.4"/>')
            s.append(f'<line x1="{ch}" y1="{bottom_channel}" x2="{ch}" y2="{ty}" stroke="#000" stroke-width="1.4"/>')
            s.append(f'<line x1="{ch}" y1="{ty}" x2="{tx}" y2="{ty}" stroke="#000" stroke-width="1.4"/>')

    for slot in slots:
        name, y, h = slot["name"], slot["y"], slot["h"]
        if slot["kind"] == "const":
            s.append(f'<text x="{x_out - 30}" y="{y + 16}" font-size="14">{_esc(name)} = {slot["const"]}</text>')
            continue
        if slot["kind"] == "or":
            cy = y + h / 2
            s.append(f'<path d="{_or_path(x_or, y, or_gate_w, h)}" fill="#222" stroke="#000"/>')
            ninp = len(slot["inputs"])
            for k, inp in enumerate(slot["inputs"]):
                iy = y + h * (k + 1) / (ninp + 1)
                route(inp, x_or, iy, k)
            s.append(f'<line x1="{x_or + or_gate_w}" y1="{cy}" x2="{x_out}" y2="{cy}" stroke="#000" stroke-width="1.5"/>')
            s.append(f'<text x="{x_out + 6}" y="{cy + 5}" font-size="15">{_esc(name)}</text>')
        else:  # direct
            cy = y + 12
            route(slot["inputs"][0], x_out, cy, 0)
            s.append(f'<text x="{x_out + 6}" y="{cy + 5}" font-size="15">{_esc(name)}</text>')

    s.append("</svg>")
    gates = [
        {"id": f"G{i + 1}", "term": "".join(g["lits"]), "outputs": list(g["outputs"])}
        for i, g in enumerate(gate_terms)
    ]
    return "\n".join(s), gates
