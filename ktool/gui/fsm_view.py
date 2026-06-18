"""Ventana para diseñar una maquina de estados (FSM) desde la interfaz.

Es un editor de formulario + dos areas de texto (estados y transiciones) que se
arman en una `Machine` y se mandan al mismo motor que la CLI. Ventana aparte para
no tocar la tabla combinacional.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from ..fsm import Machine, flipflops
from ..render.fsm_report import build_fsm_report, save_report
from .. import io as ktio

_STATES_HINT = "un estado por linea:  nombre, codigo, etiqueta, salida\n  ej:  S7, 111, R, 0000101   (etiqueta y salida son opcionales)"
_TRANS_HINT = "una transicion por linea:  origen, entrada, destino\n  ej:  S7, 0, S6     contador sin entradas:  S0, , S1"

_DEMO = {
    "name": "Contador 0-3",
    "kind": "moore",
    "inputs": "",
    "state_bits": "Q1, Q0",
    "outputs": "",
    "ff": "T",
    "states": "S0, 00, 0\nS1, 01, 1\nS2, 10, 2\nS3, 11, 3",
    "transitions": "S0, , S1\nS1, , S2\nS2, , S3\nS3, , S0",
}


def _csv(text):
    return [t.strip() for t in text.split(",") if t.strip()]


class FsmWindow:
    def __init__(self, root):
        self.win = tk.Toplevel(root)
        self.win.title("ktool - maquina de estados")
        self.win.geometry("760x680")
        self._build()
        self._fill(_DEMO)

    def _build(self):
        top = ttk.Frame(self.win, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        self.e_name = self._field(top, "Nombre:", 0, 0, width=24)
        self.cb_kind = ttk.Combobox(top, width=8, state="readonly", values=["moore", "mealy"])
        self.cb_kind.set("moore")
        ttk.Label(top, text="Tipo:").grid(row=0, column=2, sticky="e", padx=(12, 2))
        self.cb_kind.grid(row=0, column=3, sticky="w")
        self.cb_ff = ttk.Combobox(top, width=6, state="readonly", values=list(flipflops.KINDS))
        self.cb_ff.set("JK")
        ttk.Label(top, text="Flip-flop:").grid(row=0, column=4, sticky="e", padx=(12, 2))
        self.cb_ff.grid(row=0, column=5, sticky="w")

        self.e_inputs = self._field(top, "Entradas (CSV):", 1, 0, width=24)
        self.e_bits = self._field(top, "Bits de estado:", 1, 2, width=20)
        self.e_outputs = self._field(top, "Salidas (CSV):", 2, 0, width=24)
        ttk.Label(top, text="(entradas vacio = contador libre; MSB primero)",
                  foreground="#888").grid(row=2, column=2, columnspan=4, sticky="w", padx=12)

        mid = ttk.Frame(self.win, padding=(8, 0))
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ttk.Label(mid, text="Estados", font=("", 9, "bold")).pack(anchor="w")
        ttk.Label(mid, text=_STATES_HINT, foreground="#888", justify="left").pack(anchor="w")
        self.txt_states = tk.Text(mid, height=9, font=("Consolas", 10))
        self.txt_states.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        ttk.Label(mid, text="Transiciones", font=("", 9, "bold")).pack(anchor="w")
        ttk.Label(mid, text=_TRANS_HINT, foreground="#888", justify="left").pack(anchor="w")
        self.txt_trans = tk.Text(mid, height=8, font=("Consolas", 10))
        self.txt_trans.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.status = ttk.Label(self.win, text="", foreground="#a00", padding=(8, 0))
        self.status.pack(side=tk.TOP, fill=tk.X)

        bar = ttk.Frame(self.win, padding=8)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(bar, text="Generar reporte", command=self.generate).pack(side=tk.LEFT)
        ttk.Button(bar, text="Cargar .json", command=self.load).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text="Guardar .json", command=self.save).pack(side=tk.LEFT)
        ttk.Button(bar, text="Cerrar", command=self.win.destroy).pack(side=tk.RIGHT)

    def _field(self, parent, label, row, col, width=20):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="e", padx=(0, 2), pady=2)
        e = ttk.Entry(parent, width=width)
        e.grid(row=row, column=col + 1, sticky="w", pady=2)
        return e

    # -- datos --
    def _to_dict(self):
        d = {
            "doc_type": "fsm",
            "name": self.e_name.get().strip() or "Maquina",
            "kind": self.cb_kind.get(),
            "inputs": _csv(self.e_inputs.get()),
            "state_bits": _csv(self.e_bits.get()),
            "outputs": _csv(self.e_outputs.get()),
            "states": [],
            "transitions": [],
        }
        for ln in self.txt_states.get("1.0", tk.END).splitlines():
            if not ln.strip():
                continue
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) < 2:
                raise ValueError(f"estado invalido (faltan campos): {ln!r}")
            st = {"name": parts[0], "code": parts[1]}
            if len(parts) >= 3 and parts[2]:
                st["label"] = parts[2]
            if len(parts) >= 4 and parts[3]:
                st["out"] = parts[3]
            d["states"].append(st)
        for ln in self.txt_trans.get("1.0", tk.END).splitlines():
            if not ln.strip():
                continue
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) != 3:
                raise ValueError(f"transicion invalida (usa origen, entrada, destino): {ln!r}")
            d["transitions"].append({"from": parts[0], "in": parts[1], "to": parts[2]})
        return d

    def _machine(self):
        return Machine.from_dict(self._to_dict())

    def _fill(self, src):
        self.e_name.delete(0, tk.END); self.e_name.insert(0, src.get("name", ""))
        self.cb_kind.set(src.get("kind", "moore") if src.get("kind") in ("moore", "mealy") else "moore")
        self.cb_ff.set(src.get("ff", "JK"))
        def join(v):
            return ", ".join(v) if isinstance(v, list) else str(v or "")
        self.e_inputs.delete(0, tk.END); self.e_inputs.insert(0, join(src.get("inputs")))
        self.e_bits.delete(0, tk.END); self.e_bits.insert(0, join(src.get("state_bits")))
        self.e_outputs.delete(0, tk.END); self.e_outputs.insert(0, join(src.get("outputs")))
        self.txt_states.delete("1.0", tk.END)
        self.txt_trans.delete("1.0", tk.END)
        if isinstance(src.get("states"), list):
            lines = []
            for s in src["states"]:
                row = [s.get("name", ""), s.get("code", "")]
                if s.get("label"):
                    row.append(s["label"])
                if s.get("out"):
                    row.append(s["out"] if len(row) >= 3 else "")
                    if len(row) == 3:  # habia code+name pero no label: rellena label
                        row = [s.get("name", ""), s.get("code", ""), "", s["out"]]
                lines.append(", ".join(row))
            self.txt_states.insert("1.0", "\n".join(lines))
        else:
            self.txt_states.insert("1.0", src.get("states", ""))
        if isinstance(src.get("transitions"), list):
            lines = [f"{t.get('from','')}, {t.get('in','')}, {t.get('to','')}"
                     for t in src["transitions"]]
            self.txt_trans.insert("1.0", "\n".join(lines))
        else:
            self.txt_trans.insert("1.0", src.get("transitions", ""))

    # -- acciones --
    def generate(self):
        self.status.config(text="")
        try:
            machine = self._machine()
        except (ValueError, KeyError) as e:
            self.status.config(text=f"Error: {e}")
            return
        try:
            html = build_fsm_report(machine, ff_kind=self.cb_ff.get())
        except (ValueError, KeyError) as e:
            self.status.config(text=f"Error al generar: {e}")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("HTML", "*.html")],
            initialfile="reporte_fsm.html") or None
        saved = save_report(html, path, open_browser=True)
        messagebox.showinfo("Reporte generado", f"Guardado en:\n{saved}", parent=self.win)

    def save(self):
        try:
            d = self._to_dict()
        except (ValueError, KeyError) as e:
            self.status.config(text=f"Error: {e}")
            return
        d["ff"] = self.cb_ff.get()
        path = filedialog.asksaveasfilename(
            defaultextension=ktio.EXT,
            filetypes=[("Fuente ktool", "*.ktool.json"), ("JSON", "*.json")],
            initialfile="maquina" + ktio.EXT)
        if not path:
            return
        try:
            ktio.save(d, path)
        except OSError as e:
            self.status.config(text=f"No se pudo guardar: {e}")
            return
        messagebox.showinfo("Guardado", f"Fuente guardado en:\n{path}", parent=self.win)

    def load(self):
        path = filedialog.askopenfilename(
            filetypes=[("Fuente ktool", "*.ktool.json *.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            src = ktio.load(path)
        except (OSError, ValueError) as e:
            self.status.config(text=f"No se pudo abrir: {e}")
            return
        if ktio.doc_type(src) != "fsm":
            messagebox.showinfo("No es una maquina",
                                "Ese archivo es una tabla combinacional, no una maquina.",
                                parent=self.win)
            return
        self._fill(src)
        self.status.config(text=f"Cargado: {path}")
