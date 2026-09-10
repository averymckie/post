"""Public diagnostic entry points for independently encoded integer feasibility.

These project-owned adapters are disclosed. Generated differential tests of them
do not qualify all framework primitives or remove P344's adapter gate.
"""
from .logic import z3_query, cvc5_query


def z3_integer_interval(lower: int, upper: int, coefficient: int, target: int) -> str:
    expression = {"and": [{">=": ["x", lower]}, {"<=": ["x", upper]},
                          {"=": [{"*": [coefficient, "x"]}, target]}]}
    return z3_query({"x": "Int"}, expression)["status"]


def cvc5_integer_interval(lower: int, upper: int, coefficient: int, target: int) -> str:
    expression = {"and": [{">=": ["x", lower]}, {"<=": ["x", upper]},
                          {"=": [{"*": [coefficient, "x"]}, target]}]}
    return cvc5_query({"x": "Int"}, expression)["status"]
