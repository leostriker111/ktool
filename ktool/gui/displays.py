"""Displays insertables (7 segmentos, LED)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog
from .. import theme


def _hbar(x1, x2, y, t):
    h = t / 2
    return [x1, y, x1 + h, y - h, x2 - h, y - h, x2, y, x2 - h, y + h, x1 + h, y + h]


def _vbar(x, y1, y2, t):
    h = t / 2
    return [x, y1, x + h, y1 + h, x + h, y2 - h, x, y2, x - h, y2 - h, x - h, y1 + h]


def _seg7_defs():
    t, xL, xR, yT, yM, yB = 13, 26, 86, 24, 84, 144
    defs = [
        ("a", _hbar(xL, xR, yT, t)),
        ("b", _vbar(xR, yT, yM, t)),
        ("c", _vbar(xR, yM, yB, t)),
        ("d", _hbar(xL, xR, yB, t)),
        ("e", _vbar(xL, yM, yB, t)),
        ("f", _vbar(xL, yT, yM, t)),
        ("g", _hbar(xL, xR, yM, t)),
    ]
    return defs, 112, 168


class DisplayWidget:
    """Display sencillo (7 segmentos o LED) que enciende segun el estado activo.
    Cada segmento/LED tiene una etiqueta (editable) que lo conecta con la salida
    del mismo nombre."""

    def __init__(self, app, parent, kind):
        self.app = app
        self.kind = kind
        self.segments = []  # [{'name','poly','text','tag'}]
        title = {"7seg": "7 segmentos", "led": "LED"}[kind]
        self.frame = ttk.Frame(parent, relief="ridge", borderwidth=2, padding=3)
        self.frame.pack(side=tk.TOP, fill=tk.X, pady=4)
        head = ttk.Frame(self.frame)
        head.pack(fill=tk.X)
        ttk.Label(head, text=title, font=("", 9, "bold")).pack(side=tk.LEFT)
        ttk.Button(head, text="x", width=2, command=self.remove).pack(side=tk.RIGHT)
        if kind == "7seg":
            defs, w, h = _seg7_defs()
        else:
            defs, w, h = [], 86, 96
        self.canvas = tk.Canvas(self.frame, width=w, height=h, bg=theme.DISP_BG, highlightthickness=0)
        self.canvas.pack()
        if kind == "7seg":
            self._draw_segments(defs)
        else:
            self._draw_led()

    @staticmethod
    def _centroid(poly):
        xs, ys = poly[0::2], poly[1::2]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def _add_seg(self, name, poly_id, text_id, tag):
        seg = {"name": name, "poly": poly_id, "text": text_id, "tag": tag}
        self.segments.append(seg)
        self.canvas.tag_bind(tag, "<Button-1>", lambda e, s=seg: self._rename(s))

    def _draw_segments(self, defs):
        for i, (name, poly) in enumerate(defs):
            tag = f"s{i}"
            pid = self.canvas.create_polygon(poly, fill=theme.SEG_OFF, outline="#000", tags=(tag,))
            cx, cy = self._centroid(poly)
            tid = self.canvas.create_text(cx, cy, text=name, fill=theme.NAME_FG,
                                          font=("Consolas", 8, "bold"), tags=(tag,))
            self._add_seg(name, pid, tid, tag)

    def _draw_led(self):
        pid = self.canvas.create_oval(18, 14, 68, 64, fill=theme.SEG_OFF, outline="#000", width=2, tags=("L",))
        tid = self.canvas.create_text(43, 80, text="L", fill=theme.NAME_FG,
                                      font=("Consolas", 9, "bold"), tags=("L",))
        self._add_seg("L", pid, tid, "L")

    def _rename(self, seg):
        new = simpledialog.askstring(
            "Nombre del segmento/LED",
            "Se conecta con la salida del mismo nombre:",
            initialvalue=seg["name"], parent=self.app.root,
        )
        if not new or not new.strip():
            return
        seg["name"] = new.strip()
        self.canvas.itemconfig(seg["text"], text=seg["name"])
        self.app._refresh_displays()
        self.app._touch()

    def to_dict(self):
        return {"kind": self.kind, "segments": [s["name"] for s in self.segments]}

    def set_names(self, names):
        for seg, name in zip(self.segments, names):
            seg["name"] = str(name)
            self.canvas.itemconfig(seg["text"], text=seg["name"])

    def relight(self, name_value):
        for seg in self.segments:
            on = name_value.get(seg["name"]) == 1
            self.canvas.itemconfig(seg["poly"], fill=theme.SEG_ON if on else theme.SEG_OFF)
            self.canvas.itemconfig(seg["text"], fill="#0a0a0a" if on else theme.NAME_FG)

    def remove(self):
        self.frame.destroy()
        if self in self.app.displays:
            self.app.displays.remove(self)
