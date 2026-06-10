"""Tokenizador (scanner)."""

from __future__ import annotations


class Token:
    def __init__(self, kind, val=None):
        self.kind = kind
        self.val = val

    def __repr__(self):
        return f"{self.kind}:{self.val}" if self.val else self.kind


_SYMBOLS = {
    '+': "OR", '|': "OR",
    '*': "AND", '.': "AND", '&': "AND",
    '^': "XOR",
    '!': "NOT", '~': "NOT",
    "'": "POST",
    '(': "LP",
    ')': "RP"
}


def tokenize(text):
    toks = []
    i = 0
    s = text
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < len(s) and (s[j].isalnum() or s[j] == "_"):
                j += 1
            name = s[i:j]
            toks.append(Token("VAR", name))
            i = j
            continue
        if c in "01":
            toks.append(Token("CONST", int(c)))
            i += 1
            continue
        if c in _SYMBOLS:
            toks.append(Token(_SYMBOLS[c]))
            i += 1
            continue
        raise ValueError(f"caracter invalido en expresion: {c!r}")
    return toks
