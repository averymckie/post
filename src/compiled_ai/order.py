"""Order: the forced-precedence graph and the derivation order.

The precedes atoms form a directed graph over events. Its transitive reduction
is the forced-precedence graph: an edge survives only where a source clause
states an order that no other chain of clauses already implies. The
derivation order is the unique lexicographic topological order of that graph.
A cycle is an ordering contradiction and is reported with its edges sorted.
"""

from __future__ import annotations

from .model import Atom, Ordering


def order(atoms: list[Atom]) -> Ordering:
    import networkx as nx

    g: "nx.DiGraph[str]" = nx.DiGraph()
    for a in sorted((a for a in atoms if a.predicate == "precedes"), key=lambda a: a.id):
        g.add_edge(a.args[0], a.args[1])
    if g.number_of_nodes() == 0:
        return Ordering(order=(), forced=(), cycle=())
    if not nx.is_directed_acyclic_graph(g):
        first = min(g.nodes)
        cyc = nx.find_cycle(g, source=first)
        return Ordering(order=(), forced=(), cycle=tuple(sorted((u, v) for u, v, *_ in cyc)))
    reduced = nx.transitive_reduction(g)
    forced = tuple(sorted((u, v) for u, v in reduced.edges))
    seq = tuple(nx.lexicographical_topological_sort(reduced, key=str))
    return Ordering(order=seq, forced=forced, cycle=())
