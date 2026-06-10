"""Layout de K-map."""

from __future__ import annotations


def gray(i):
    return i ^ (i >> 1)


def kmap_layout(nvars):
    """Devuelve (row_vars, col_vars, n_rows, n_cols)."""
    # H4: calculable instead of hardcoded dict
    row_vars = list(range(nvars // 2))
    col_vars = list(range(nvars // 2, nvars))
    return row_vars, col_vars, 1 << len(row_vars), 1 << len(col_vars)


def _group_bits(gray_code, var_positions, nvars):
    """Para un codigo gray de un grupo (fila o columna), regresa
    {posicion_variable_global: bit}."""
    k = len(var_positions)
    out = {}
    for idx, vpos in enumerate(var_positions):
        bit = (gray_code >> (k - 1 - idx)) & 1
        out[vpos] = bit
    return out


def cell_index(row, col, nvars):
    """minterm que cae en la celda (row, col) del K-map."""
    row_vars, col_vars, _, _ = kmap_layout(nvars)
    assign = {}
    assign.update(_group_bits(gray(row), row_vars, nvars))
    assign.update(_group_bits(gray(col), col_vars, nvars))
    value = 0
    for vpos, bit in assign.items():
        if bit:
            value |= 1 << (nvars - 1 - vpos)
    return value


def pattern_matches_row(pattern, row, nvars):
    row_vars, _, _, _ = kmap_layout(nvars)
    bits = _group_bits(gray(row), row_vars, nvars)
    for vpos, bit in bits.items():
        c = pattern[vpos]
        if c != "-" and int(c) != bit:
            return False
    return True


def pattern_matches_col(pattern, col, nvars):
    _, col_vars, _, _ = kmap_layout(nvars)
    bits = _group_bits(gray(col), col_vars, nvars)
    for vpos, bit in bits.items():
        c = pattern[vpos]
        if c != "-" and int(c) != bit:
            return False
    return True
