"""Interfaz grafica (Tkinter) estilo 32x8 con multiples salidas y notas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from . import core, expr
from .core import TruthTable, default_vars
from .report import Options, build_report, save_report
from .simplify import solve_output, shared_terms

CYCLE = {0: 1, 1: "x", "x": 0}
CELL_BG = {0: "#f3f3f3", 1: "#cdebcd", "x": "#fff0c2"}
CELL_FG = {0: "#333", 1: "#176117", "x": "#9a6b00"}


def out_names(count):
    return ["Y"] if count == 1 else [f"Y{i+1}" for i in range(count)]


class App:
    def __init__(self, root):
        self.root = root
        root.title("ktool - simplificador de logica digital")
        root.geometry("1080x720")

        self.nvars = tk.IntVar(value=3)
        self.nouts = tk.IntVar(value=1)
        self.notes_on = tk.BooleanVar(value=False)
        self.form = tk.StringVar(value="auto")

        self.values = []      # values[out][row]
        self.cells = []       # buttons
        self.note_entries = []

        self._build_controls()
        self._build_table_area()
        self._build_bottom()
        self.rebuild_table()

    # ---------- controles ----------
    def _build_controls(self):
        bar = ttk.Frame(self.root, padding=8)
        bar.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(bar, text="Variables:").pack(side=tk.LEFT)
        sp1 = ttk.Spinbox(bar, from_=2, to=6, width=3, textvariable=self.nvars,
                          command=self.rebuild_table)
        sp1.pack(side=tk.LEFT, padx=(2, 12))

        ttk.Label(bar, text="Salidas:").pack(side=tk.LEFT)
        sp2 = ttk.Spinbox(bar, from_=1, to=10, width=3, textvariable=self.nouts,
                          command=self.rebuild_table)
        sp2.pack(side=tk.LEFT, padx=(2, 12))

        ttk.Checkbutton(bar, text="Columna notas", variable=self.notes_on,
                        command=self.rebuild_table).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(bar, text="Forma:").pack(side=tk.LEFT)
        ttk.OptionMenu(bar, self.form, "auto", "auto", "sop", "pos", "both").pack(
            side=tk.LEFT, padx=(2, 12))

        ttk.Button(bar, text="Ecuaciones", command=self.show_equations).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Generar documento", command=self.generate).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Limpiar", command=self.clear_values).pack(side=tk.LEFT, padx=4)

        # barra de expresion
        bar2 = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        bar2.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(bar2, text="Expresion:").pack(side=tk.LEFT)
        self.expr_entry = ttk.Entry(bar2, width=42)
        self.expr_entry.pack(side=tk.LEFT, padx=4)
        self.expr_entry.insert(0, "A'B + C")
        ttk.Label(bar2, text="-> salida:").pack(side=tk.LEFT)
        self.expr_target = ttk.Combobox(bar2, width=5, state="readonly")
        self.expr_target.pack(side=tk.LEFT, padx=4)
        ttk.Button(bar2, text="Evaluar y llenar", command=self.fill_from_expr).pack(side=tk.LEFT)
        ttk.Label(bar2, text="  (AND: ab a*b | OR: + | NOT: ' ! | XOR: ^)",
                  foreground="#777").pack(side=tk.LEFT)

    def _build_table_area(self):
        wrap = ttk.Frame(self.root)
        wrap.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8)
        self.canvas = tk.Canvas(wrap, highlightthickness=0)
        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _build_bottom(self):
        frame = ttk.LabelFrame(self.root, text="Resultados", padding=6)
        frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)
        self.result = tk.Text(frame, height=9, font=("Consolas", 10), wrap="none")
        self.result.pack(fill=tk.X)

    # ---------- construccion de tabla ----------
    def rebuild_table(self):
        try:
            n = max(2, min(6, int(self.nvars.get())))
            k = max(1, min(10, int(self.nouts.get())))
        except (tk.TclError, ValueError):
            return
        rows = 1 << n
        variables = default_vars(n)
        names = out_names(k)

        # preserva valores previos
        old = self.values
        self.values = []
        for oi in range(k):
            col = []
            for r in range(rows):
                v = 0
                if oi < len(old) and r < len(old[oi]):
                    v = old[oi][r]
                col.append(v)
            self.values.append(col)

        for w in self.table_frame.winfo_children():
            w.destroy()
        self.cells = [[None] * rows for _ in range(k)]
        self.note_entries = []

        # encabezados
        col = 0
        ttk.Label(self.table_frame, text="#", width=4, anchor="center",
                  relief="solid", borderwidth=1).grid(row=0, column=col, sticky="nsew")
        col += 1
        for v in variables:
            ttk.Label(self.table_frame, text=v, width=3, anchor="center",
                      relief="solid", borderwidth=1).grid(row=0, column=col, sticky="nsew")
            col += 1
        out_start = col
        for name in names:
            ttk.Label(self.table_frame, text=name, width=4, anchor="center",
                      relief="solid", borderwidth=1,
                      background="#dde7f7").grid(row=0, column=col, sticky="nsew")
            col += 1
        if self.notes_on.get():
            ttk.Label(self.table_frame, text="nota", width=10, anchor="center",
                      relief="solid", borderwidth=1).grid(row=0, column=col, sticky="nsew")
            notes_col = col

        for r in range(rows):
            gr = r + 1
            tk.Label(self.table_frame, text=str(r), width=4, relief="solid", borderwidth=1,
                     bg="#efefef", fg="#888").grid(row=gr, column=0, sticky="nsew")
            c = 1
            for b in core.TruthTable(n).bits(r):
                tk.Label(self.table_frame, text=str(b), width=3, relief="solid",
                         borderwidth=1, bg="#fbfbfb").grid(row=gr, column=c, sticky="nsew")
                c += 1
            for oi in range(k):
                v = self.values[oi][r]
                btn = tk.Button(self.table_frame, text=str(v), width=4, relief="solid",
                                borderwidth=1, bg=CELL_BG[v], fg=CELL_FG[v],
                                command=lambda o=oi, row=r: self.cycle(o, row))
                btn.grid(row=gr, column=out_start + oi, sticky="nsew")
                self.cells[oi][r] = btn
            if self.notes_on.get():
                e = ttk.Entry(self.table_frame, width=12)
                e.grid(row=gr, column=notes_col, sticky="nsew")
                self.note_entries.append(e)

        self.expr_target["values"] = names
        self.expr_target.current(0)

    def cycle(self, oi, row):
        v = CYCLE[self.values[oi][row]]
        self.values[oi][row] = v
        btn = self.cells[oi][row]
        btn.config(text=str(v), bg=CELL_BG[v], fg=CELL_FG[v])

    def clear_values(self):
        for oi in range(len(self.values)):
            for r in range(len(self.values[oi])):
                self.values[oi][r] = 0
                self.cells[oi][r].config(text="0", bg=CELL_BG[0], fg=CELL_FG[0])

    # ---------- acciones ----------
    def _current_table(self):
        n = max(2, min(6, int(self.nvars.get())))
        variables = default_vars(n)
        names = out_names(max(1, min(10, int(self.nouts.get()))))
        outputs = {names[oi]: list(self.values[oi]) for oi in range(len(names))}
        notes = None
        if self.notes_on.get() and self.note_entries:
            notes = [e.get() for e in self.note_entries]
        return TruthTable(n, variables, outputs, notes)

    def fill_from_expr(self):
        text = self.expr_entry.get().strip()
        if not text:
            return
        n = max(2, min(6, int(self.nvars.get())))
        variables = default_vars(n)
        try:
            ast = expr.parse(text)
            used = set()
            expr.collect_vars(ast, used)
            unknown = used - set(variables)
            if unknown:
                raise ValueError(f"variables fuera de A..{variables[-1]}: {', '.join(sorted(unknown))}")
        except Exception as e:
            messagebox.showerror("Expresion invalida", str(e))
            return
        target = self.expr_target.get()
        names = out_names(max(1, min(10, int(self.nouts.get()))))
        oi = names.index(target)
        rows = 1 << n
        for r in range(rows):
            env = {variables[k]: (r >> (n - 1 - k)) & 1 for k in range(n)}
            v = expr.evaluate(ast, env)
            self.values[oi][r] = v
            self.cells[oi][r].config(text=str(v), bg=CELL_BG[v], fg=CELL_FG[v])

    def show_equations(self):
        table = self._current_table()
        sols = {n: solve_output(v, table.variables) for n, v in table.outputs.items()}
        lines = [f"{table.nvars} variables: {', '.join(table.variables)}", ""]
        for name, sol in sols.items():
            lines.append(f"[{name}]")
            lines.append(f"  SOP : {name} = {sol['sop'].equation}   ({sol['sop'].cost()[0]} comp, {sol['sop'].cost()[1]} lit)")
            lines.append(f"  POS : {name} = {sol['pos'].equation}   ({sol['pos'].cost()[0]} comp, {sol['pos'].cost()[1]} lit)")
            lines.append(f"  best: {sol['best'].form.upper()} -> {name} = {sol['best'].equation}")
            if sol["parity"]:
                lines.append(f"  xor : {name} = {sol['parity']['equation']}")
            lines.append("")
        if len(table.outputs) > 1:
            sh = shared_terms(sols, table.variables, "sop")
            if sh:
                lines.append("[terminos reutilizables (SOP)]")
                for d in sh:
                    lines.append(f"  {d['term']:<14} -> {', '.join(d['outputs'])}")
        self.result.delete("1.0", tk.END)
        self.result.insert("1.0", "\n".join(lines))

    def generate(self):
        table = self._current_table()
        opt = Options(form=self.form.get(), title="Resultados ktool")
        html = build_report(table, opt)
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile="ktool_resultado.html",
        )
        if not path:
            path = None
        saved = save_report(html, path, open_browser=True)
        self.show_equations()
        messagebox.showinfo("Documento generado", f"Guardado en:\n{saved}")


def launch():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
