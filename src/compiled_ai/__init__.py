"""compiled_ai: source procedures to a cited first-order-logic base.

    read        every character of the source with its position
    parse       UDPipe dependency parse per sentence, with character ranges
    tables      token tables and the citation index (conversion operator)
    fol         first-order-logic atoms: event, agent, patient, theme,
                obligatory, negated, precedes (compilation operator)
    normalize   closed-class pronoun resolution against the document role
                assignment; inanimate subjects routed agent -> theme
    check       byte-exact citations; fragments flagged for adjudication
    adjudicate  the analyst's rejections
    reconcile   precedes atoms as difference logic in Z3
    order       forced-precedence graph and derivation order
    seal        per-atom digests and the manifest digest
"""

__version__ = "0.2.0"
