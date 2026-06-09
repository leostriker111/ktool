"""Parser de expresiones booleanas -> tabla de verdad.

Operadores:
    NOT   !a   ~a   a'        (mayor precedencia)
    AND   a*b  a.b  a&b  ab   (concatenacion = AND)
    XOR   a^b
    OR    a+b  a|b            (menor precedencia)
Parentesis ( ). Constantes 0 y 1. XNOR = (a^b)'.
"""

from __future__ import annotations


class _Tok:
    def __init__(self, kind, val=None):
        self.kind = kind
        self.val = val

    def __repr__(self):
        return f"{self.kind}:{self.val}" if self.val else self.kind


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
            toks.append(_Tok("VAR", name))
            i = j
            continue
        if c in "01":
            toks.append(_Tok("CONST", int(c)))
            i += 1
            continue
        if c in "+|":
            toks.append(_Tok("OR"))
        elif c in "*.&":
            toks.append(_Tok("AND"))
        elif c == "^":
            toks.append(_Tok("XOR"))
        elif c in "!~":
            toks.append(_Tok("NOT"))
        elif c == "'":
            toks.append(_Tok("POST"))
        elif c == "(":
            toks.append(_Tok("LP"))
        elif c == ")":
            toks.append(_Tok("RP"))
        else:
            raise ValueError(f"caracter invalido en expresion: {c!r}")
        i += 1
    return toks


# AST: ('var', name) ('const', v) ('not', a) ('and', a, b) ('or', a, b) ('xor', a, b)

class _Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def peek(self):
        return self.toks[self.pos] if self.pos < len(self.toks) else None

    def eat(self):
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def parse(self):
        node = self.parse_or()
        if self.peek() is not None:
            raise ValueError("expresion mal formada")
        return node

    def parse_or(self):
        node = self.parse_xor()
        while self.peek() and self.peek().kind == "OR":
            self.eat()
            node = ("or", node, self.parse_xor())
        return node

    def parse_xor(self):
        node = self.parse_and()
        while self.peek() and self.peek().kind == "XOR":
            self.eat()
            node = ("xor", node, self.parse_and())
        return node

    def _starts_operand(self, t):
        return t is not None and t.kind in ("VAR", "CONST", "NOT", "LP")

    def parse_and(self):
        node = self.parse_not()
        while True:
            t = self.peek()
            if t is None:
                break
            if t.kind == "AND":
                self.eat()
                node = ("and", node, self.parse_not())
            elif self._starts_operand(t):  # concatenacion implicita
                node = ("and", node, self.parse_not())
            else:
                break
        return node

    def parse_not(self):
        t = self.peek()
        if t and t.kind == "NOT":
            self.eat()
            return ("not", self.parse_not())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_atom()
        while self.peek() and self.peek().kind == "POST":
            self.eat()
            node = ("not", node)
        return node

    def parse_atom(self):
        t = self.eat()
        if t is None:
            raise ValueError("se esperaba un operando")
        if t.kind == "VAR":
            return ("var", t.val)
        if t.kind == "CONST":
            return ("const", t.val)
        if t.kind == "LP":
            node = self.parse_or()
            close = self.eat()
            if close is None or close.kind != "RP":
                raise ValueError("falta ')'")
            return node
        raise ValueError(f"operando inesperado: {t}")


def parse(text):
    return _Parser(tokenize(text)).parse()


def collect_vars(node, acc):
    if node[0] == "var":
        acc.add(node[1])
    elif node[0] in ("not",):
        collect_vars(node[1], acc)
    elif node[0] in ("and", "or", "xor"):
        collect_vars(node[1], acc)
        collect_vars(node[2], acc)


def evaluate(node, env):
    k = node[0]
    if k == "var":
        return env[node[1]]
    if k == "const":
        return node[1]
    if k == "not":
        return 1 - evaluate(node[1], env)
    a = evaluate(node[1], env)
    if k == "and":
        return a & evaluate(node[2], env)
    if k == "or":
        return a | evaluate(node[2], env)
    if k == "xor":
        return a ^ evaluate(node[2], env)
    raise ValueError(f"nodo desconocido: {k}")


def build_output(text, nvars=None):
    """Devuelve (variables_ordenadas, valores) para todas las combinaciones."""
    ast = parse(text)
    found = set()
    collect_vars(ast, found)
    variables = sorted(found)
    if nvars is not None and nvars > len(variables):
        # rellena con variables sin usar para respetar el tamano pedido
        from .core import VAR_NAMES

        extra = [v for v in VAR_NAMES if v not in variables][: nvars - len(variables)]
        variables = sorted(variables + extra)
    n = len(variables)
    vals = []
    for i in range(1 << n):
        env = {variables[k]: (i >> (n - 1 - k)) & 1 for k in range(n)}
        vals.append(evaluate(ast, env))
    return variables, vals
