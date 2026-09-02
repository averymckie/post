"""Step 9, order: the precedence of the steps. Symbolic.

Edges come from precedence statements (before, after) and from clocks (the
trigger comes before the subject). The order is the unique lexicographic
topological order, so ties break the same way every time. A cycle is an
ordering contradiction in the source and is reported with its edges sorted.
"""

from __future__ import annotations

from collections.abc import Iterable

from .model import Statement, Strict


class Ordering(Strict):
    order: tuple[str, ...]
    edges: tuple[tuple[str, str, str], ...]  # (before, after, sentence id)
    cycle: tuple[tuple[str, str], ...]


def edges_from(statements: Iterable[Statement]) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for st in statements:
        p = st.proposal
        if p.kind == "precedence" and p.before and p.after:
            out.append((p.before, p.after, st.sentence.id))
        if p.clock is not None and p.clock.trigger and p.clock.subject and p.clock.trigger != p.clock.subject:
            out.append((p.clock.trigger, p.clock.subject, st.sentence.id))
    return sorted(set(out))


def order(edges: list[tuple[str, str, str]]) -> Ordering:
    import networkx as nx  # compiler-only dependency

    g: "nx.DiGraph[str]" = nx.DiGraph()
    for before, after, _ in sorted(edges):
        g.add_edge(before, after)
    for node in sorted(g.nodes):
        g.nodes[node]["name"] = node
    try:
        seq = tuple(nx.lexicographical_topological_sort(g, key=str))
        return Ordering(order=seq, edges=tuple(sorted(edges)), cycle=())
    except nx.NetworkXUnfeasible:
        first = min(g.nodes)
        cyc = nx.find_cycle(g, source=first)
        return Ordering(order=(), edges=tuple(sorted(edges)), cycle=tuple(sorted((a, b) for a, b, *_ in cyc)))
