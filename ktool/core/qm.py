"""Quine-McCluskey: implicantes primos y cobertura minima (Petrick)."""

from __future__ import annotations


def _combine(a, b):
    diff = 0
    res = []
    for x, y in zip(a, b):
        if x != y:
            diff += 1
            res.append("-")
        else:
            res.append(x)
    return "".join(res) if diff == 1 else None


def pattern_minterms(pattern):
    """Todos los minterms cubiertos por un patron tipo '10-1'."""
    dash_pos = [i for i, c in enumerate(pattern) if c == "-"]
    n = len(pattern)
    base = int(pattern.replace("-", "0"), 2)
    out = set()
    for combo in range(1 << len(dash_pos)):
        v = base
        for b, i in enumerate(dash_pos):
            if (combo >> b) & 1:
                v |= 1 << (n - 1 - i)
        out.add(v)
    return out


def literal_count(pattern):
    return sum(1 for c in pattern if c != "-")


def prime_implicants(terms, nbits):
    """terms = minterms U dontcares (los que pueden combinarse)."""
    patterns = {format(t, f"0{nbits}b") for t in terms}
    primes = set()
    while patterns:
        used = set()
        nxt = set()
        plist = list(patterns)
        for i in range(len(plist)):
            for j in range(i + 1, len(plist)):
                c = _combine(plist[i], plist[j])
                if c is not None:
                    nxt.add(c)
                    used.add(plist[i])
                    used.add(plist[j])
        for p in patterns:
            if p not in used:
                primes.add(p)
        patterns = nxt
    return primes


def _minimal_sets(sets):
    """Absorcion: quita conjuntos que sean superconjunto de otro."""
    items = sorted(sets, key=len)
    keep = []
    for s in items:
        if not any(k <= s for k in keep):
            keep.append(s)
    return keep


def _petrick(pis, cover_map, required):
    clauses = []
    for m in required:
        clause = frozenset(p for p in pis if m in cover_map[p])
        if clause:
            clauses.append(clause)
    products = [frozenset()]
    for clause in clauses:
        new = set()
        for prod in products:
            for pi in clause:
                new.add(prod | {pi})
        products = _minimal_sets(new)
    if not products:
        return set()
    best = min(
        products,
        key=lambda s: (len(s), sum(literal_count(p) for p in s)),
    )
    return set(best)


def cover(primes, required):
    """Selecciona implicantes primos que cubren 'required' (los unos reales)."""
    pis = list(primes)
    required = set(required)
    cover_map = {p: pattern_minterms(p) & required for p in pis}
    chosen = set()
    remaining = set(required)

    # implicantes esenciales (iterado)
    while remaining:
        essentials = set()
        for m in list(remaining):
            covering = [p for p in pis if m in cover_map[p]]
            if len(covering) == 1:
                essentials.add(covering[0])
        if not essentials:
            break
        for p in essentials:
            chosen.add(p)
            remaining -= cover_map[p]

    if remaining:
        live = [p for p in pis if p not in chosen]
        chosen |= _petrick(live, cover_map, remaining)
    return chosen


def minimize(minterms, dontcares, nbits, required):
    """Regresa lista ordenada de patrones que cubre 'required'.
    'required' = unos (SOP) o ceros (POS). dontcares se usan para combinar."""
    required = set(required)
    if not required:
        return []
    terms = set(minterms) | set(dontcares)
    primes = prime_implicants(terms, nbits)
    chosen = cover(primes, required)
    return sorted(chosen)
