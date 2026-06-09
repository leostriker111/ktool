"""Arma el documento HTML con todos los resultados."""

from __future__ import annotations

import os
import tempfile
import webbrowser

from .simplify import solve_output, shared_terms
from . import render_kmap, render_circuit


def _esc(s):
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


class Options:
    def __init__(
        self,
        form="auto",        # 'sop' | 'pos' | 'auto' | 'both'
        kmap=True,
        circuit=True,
        table=True,
        shared=True,
        title="Resultados ktool",
    ):
        self.form = form
        self.kmap = kmap
        self.circuit = circuit
        self.table = table
        self.shared = shared
        self.title = title


def _forms_to_show(opt, best):
    if opt.form == "both":
        return ["sop", "pos"]
    if opt.form in ("sop", "pos"):
        return [opt.form]
    return [best.form]  # auto


def _truth_table_html(table):
    has_notes = any(n for n in table.notes)
    head = ["#"] + table.variables + list(table.outputs.keys())
    if has_notes:
        head.append("nota")
    ths = "".join(f"<th>{_esc(h)}</th>" for h in head)
    rows = []
    for i in range(table.rows):
        cells = [f"<td class='idx'>{i}</td>"]
        for b in table.bits(i):
            cells.append(f"<td>{b}</td>")
        for name in table.outputs:
            v = table.outputs[name][i]
            cls = "dc" if v == "x" else ("one" if v == 1 else "zero")
            cells.append(f"<td class='{cls}'>{v}</td>")
        if has_notes:
            cells.append(f"<td class='note'>{_esc(table.notes[i])}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table class='tt'><thead><tr>{ths}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_report(table, opt=None):
    opt = opt or Options()
    solutions = {
        name: solve_output(vals, table.variables)
        for name, vals in table.outputs.items()
    }

    body = [f"<h1>{_esc(opt.title)}</h1>"]
    body.append(
        f"<p class='meta'>{table.nvars} variables "
        f"({', '.join(table.variables)}) &middot; {len(table.outputs)} salida(s)</p>"
    )

    if opt.table:
        body.append("<h2>Tabla de verdad</h2>")
        body.append(_truth_table_html(table))

    # terminos compartidos
    if opt.shared and len(table.outputs) > 1:
        for form in (["sop", "pos"] if opt.form == "both" else
                     [opt.form if opt.form in ("sop", "pos") else "sop"]):
            sh = shared_terms(solutions, table.variables, form)
            if sh:
                body.append(f"<h2>Terminos reutilizables ({form.upper()})</h2>")
                body.append("<table class='shared'><thead><tr>"
                            "<th>Termino (compuerta)</th><th>Usado en</th></tr></thead><tbody>")
                for d in sh:
                    body.append(
                        f"<tr><td><code>{_esc(d['term'])}</code></td>"
                        f"<td>{', '.join(map(_esc, d['outputs']))}</td></tr>"
                    )
                body.append("</tbody></table>")
                body.append("<p class='hint'>Estas compuertas pueden compartirse entre salidas "
                            "para ahorrar componentes.</p>")

    # por salida
    for name, vals in table.outputs.items():
        sol = solutions[name]
        body.append("<div class='outcard'>")
        body.append(f"<h2>Salida <code>{_esc(name)}</code></h2>")

        # ecuaciones
        body.append("<div class='eqs'>")
        body.append(
            f"<div><b>SOP:</b> <code>{_esc(name)} = {_esc(sol['sop'].equation)}</code> "
            f"<span class='cost'>({sol['sop'].cost()[0]} comp, {sol['sop'].cost()[1]} lit)</span></div>"
        )
        body.append(
            f"<div><b>POS:</b> <code>{_esc(name)} = {_esc(sol['pos'].equation)}</code> "
            f"<span class='cost'>({sol['pos'].cost()[0]} comp, {sol['pos'].cost()[1]} lit)</span></div>"
        )
        body.append(
            f"<div class='best'>&#9733; Mejor por costo: <b>{sol['best'].form.upper()}</b> &rarr; "
            f"<code>{_esc(name)} = {_esc(sol['best'].equation)}</code></div>"
        )
        if sol["parity"]:
            body.append(
                f"<div class='xor'>&#8853; XOR/XNOR: <code>{_esc(name)} = {_esc(sol['parity']['equation'])}</code></div>"
            )
        body.append("</div>")

        forms = _forms_to_show(opt, sol["best"])

        if opt.kmap:
            body.append("<div class='maps'>")
            for form in forms:
                s = sol[form]
                pats = s.patterns if s.const is None else []
                body.append("<div class='mapwrap'>")
                body.append(f"<div class='maplabel'>K-map {form.upper()}</div>")
                body.append(render_kmap.kmap_svg(vals, table.variables, pats))
                if pats:
                    body.append("<div class='legend'>"
                                + render_kmap.group_legend(pats, table.variables, form)
                                + "</div>")
                body.append("</div>")
            body.append("</div>")

        if opt.circuit:
            body.append("<div class='circuits'>")
            for form in forms:
                body.append("<div class='cwrap'>")
                body.append(f"<div class='maplabel'>Circuito {form.upper()}</div>")
                body.append(render_circuit.circuit_svg(sol[form], name))
                body.append("</div>")
            body.append("</div>")

        body.append("</div>")  # outcard

    return _wrap_html(opt.title, "\n".join(body))


_CSS = """
body{font-family:Georgia,serif;margin:24px;color:#222;background:#fafafa;}
h1{font-size:24px;} h2{font-size:18px;border-bottom:1px solid #ccc;padding-bottom:3px;margin-top:26px;}
h3{font-size:15px;}
code{font-family:Consolas,monospace;background:#eef;padding:1px 4px;border-radius:3px;}
.meta{color:#666;}
table{border-collapse:collapse;margin:8px 0;}
.tt td,.tt th{border:1px solid #999;padding:3px 9px;text-align:center;font-size:13px;}
.tt th{background:#e8e8e8;}
.tt .idx{color:#888;} .tt .one{background:#e9f5e9;font-weight:bold;}
.tt .dc{background:#fff3cd;color:#b8860b;} .tt .note{text-align:left;font-style:italic;}
.shared td,.shared th{border:1px solid #aaa;padding:4px 10px;font-size:13px;}
.shared th{background:#e8e8e8;}
.eqs{background:#fff;border:1px solid #ddd;border-radius:6px;padding:10px;margin:8px 0;line-height:1.7;}
.cost{color:#888;font-size:12px;}
.best{margin-top:6px;color:#1a7a1a;}
.xor{color:#7a1a7a;}
.maps,.circuits{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start;}
.mapwrap,.cwrap{background:#fff;border:1px solid #ddd;border-radius:6px;padding:10px;}
.maplabel{font-weight:bold;font-size:13px;margin-bottom:6px;}
.legend{margin-top:8px;font-size:12px;}
.outcard{margin-bottom:18px;}
.hint{color:#666;font-size:12px;font-style:italic;}
"""


def _wrap_html(title, body):
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{_esc(title)}</title><style>{_CSS}</style></head>"
        f"<body>{body}</body></html>"
    )


def save_report(html, path=None, open_browser=False):
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".html", prefix="ktool_")
        os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    if open_browser:
        webbrowser.open("file://" + os.path.abspath(path))
    return path
