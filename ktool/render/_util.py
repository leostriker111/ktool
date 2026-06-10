"""Utilidades de renderizado."""

from __future__ import annotations


def _esc(s):
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def _attr(s):
    return _esc(s).replace('"', "&quot;").replace("\n", "&#10;")
