"""compiled_ai: compile regulatory text into checked, sealed, deterministic rules.

The chain, one module per step:

1. read       every character of the source with its position          (symbolic)
2. cut        sentences with their positions                            (symbolic)
3. propose    a typed statement per sentence, drafted by a model        (neural)
4. check      the mechanical items: byte-exact quote, defined actor,    (symbolic)
              connective table, reserved decision
5. confirm    one recorded human answer per sentence                    (human)
6. generate   a rule function per confirmed statement                   (neural)
7. prove      type check and property tests                             (symbolic)
8. reconcile  consistency of the rule set, minimal conflicting set      (symbolic)
9. order      precedence of the steps                                   (symbolic)
10. seal      a digest per rule from its source bytes                   (symbolic)
11. run       a case in, a proof or a list of reasons out               (symbolic, no model)

Nothing in `compiled_ai.runtime` imports a model client. `tests/test_boundary.py`
enforces that.
"""

__version__ = "0.1.0"
