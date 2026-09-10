"""Two separate AST-to-solver encoders for quantifier-free linear Int/Real/Bool.

No eval, SMT script execution, floats, quantifiers, division, or nonlinear terms.
Both encoders share the *accepted AST*, so agreement is not semantic review.
"""
from fractions import Fraction
import cvc5
from cvc5 import Kind
import z3
from .io import InputError, digest


def sort_of(expr, declarations):
    if type(expr) is bool:
        return "Bool"
    if type(expr) is int:
        return "Int"
    if isinstance(expr, str):
        if expr not in declarations:
            raise InputError(f"Undeclared variable: {expr}")
        return declarations[expr]
    if not isinstance(expr, dict) or len(expr) != 1:
        raise InputError("Expressions must be booleans, integers, variable names or one-key AST objects")
    op, args = next(iter(expr.items()))
    if op == "rat":
        if not isinstance(args, str):
            raise InputError("Rationals must be exact fraction strings")
        try:
            Fraction(args)
        except (ValueError, ZeroDivisionError) as e:
            raise InputError("Invalid rational") from e
        return "Real"
    if not isinstance(args, list):
        raise InputError(f"{op} expects an array")
    n = len(args)
    if op not in {"and", "or", "not", "implies", "=", "!=", "<", "<=", ">", ">=", "+", "-", "*"}:
        raise InputError(f"Unsupported operator: {op}")
    if (op == "not" and n != 1) or (op not in {"and", "or", "+", "not"} and n != 2) or (op == "+" and n < 1):
        raise InputError(f"Invalid arity for {op}")
    kinds = [sort_of(a, declarations) for a in args]
    if op in {"and", "or", "not", "implies"}:
        if any(k != "Bool" for k in kinds):
            raise InputError(f"Nonboolean operand of {op}")
        return "Bool"
    if op in {"=", "!="} and all(k == "Bool" for k in kinds):
        return "Bool"
    if any(k == "Bool" for k in kinds):
        raise InputError("Boolean used as a number")
    if op == "*" and not any(type(a) is int or (isinstance(a, dict) and set(a) == {"rat"}) for a in args):
        raise InputError("Nonlinear multiplication is unsupported")
    if op in {"=", "!=", "<", "<=", ">", ">="}:
        return "Bool"
    return "Real" if "Real" in kinds else "Int"


def conjunction(expressions):
    return {"and": list(expressions)}


def validate_formula(expr, declarations):
    if any(t not in {"Bool", "Int", "Real"} for t in declarations.values()):
        raise InputError("Variable types must be Bool, Int or Real")
    if sort_of(expr, declarations) != "Bool":
        raise InputError("Top-level constraint must be boolean")


def z3_query(declarations, expression, timeout_ms=3000):
    validate_formula(expression, declarations)
    constructors = {"Bool": z3.Bool, "Int": z3.Int, "Real": z3.Real}
    symbols = {name: constructors[t](name) for name, t in declarations.items()}

    def encode(x):
        if type(x) is bool:
            return z3.BoolVal(x)
        if type(x) is int:
            return z3.IntVal(x)
        if isinstance(x, str):
            return symbols[x]
        op, a = next(iter(x.items()))
        if op == "rat":
            f = Fraction(a)
            return z3.RealVal(f"{f.numerator}/{f.denominator}")
        v = [encode(i) for i in a]
        if op == "and": return z3.And(*v)
        if op == "or": return z3.Or(*v)
        if op == "not": return z3.Not(v[0])
        if op == "implies": return z3.Implies(*v)
        if op == "=": return v[0] == v[1]
        if op == "!=": return v[0] != v[1]
        if op == "<": return v[0] < v[1]
        if op == "<=": return v[0] <= v[1]
        if op == ">": return v[0] > v[1]
        if op == ">=": return v[0] >= v[1]
        if op == "+": return z3.Sum(*v)
        if op == "-": return v[0] - v[1]
        if op == "*": return v[0] * v[1]
        raise InputError(op)

    solver = z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(encode(expression))
    decision = solver.check()
    result = {"engine": "z3", "status": str(decision), "smt2": solver.to_smt2()}
    if decision == z3.sat:
        model = solver.model()
        result["model"] = {k: str(model.eval(v, model_completion=True)) for k, v in symbols.items()}
    if decision == z3.unknown:
        result["reason"] = solver.reason_unknown()
    return result


def cvc5_query(declarations, expression, timeout_ms=3000):
    validate_formula(expression, declarations)
    tm = cvc5.TermManager()
    solver = cvc5.Solver(tm)
    solver.setLogic("QF_LIRA")
    solver.setOption("produce-models", "true")
    solver.setOption("tlimit-per", str(timeout_ms))
    sorts = {"Bool": tm.getBooleanSort(), "Int": tm.getIntegerSort(), "Real": tm.getRealSort()}
    symbols = {k: tm.mkConst(sorts[t], k) for k, t in declarations.items()}

    def encode(x):
        if type(x) is bool: return tm.mkBoolean(x)
        if type(x) is int: return tm.mkInteger(str(x))
        if isinstance(x, str): return symbols[x]
        op, args = next(iter(x.items()))
        if op == "rat":
            f = Fraction(args)
            return tm.mkReal(f"{f.numerator}/{f.denominator}")
        children = [encode(a) for a in args]
        if op in {"and", "or"} and not children:
            return tm.mkBoolean(op == "and")
        if op in {"and", "or", "+"} and len(children) == 1:
            return children[0]
        if op not in {"and", "or", "not", "implies"} and any(c.getSort().isReal() for c in children):
            children = [tm.mkTerm(Kind.TO_REAL, c) if c.getSort().isInteger() else c for c in children]
        kinds = {"and": Kind.AND, "or": Kind.OR, "not": Kind.NOT, "implies": Kind.IMPLIES,
                 "=": Kind.EQUAL, "!=": Kind.DISTINCT, "<": Kind.LT, "<=": Kind.LEQ,
                 ">": Kind.GT, ">=": Kind.GEQ, "+": Kind.ADD, "-": Kind.SUB, "*": Kind.MULT}
        return tm.mkTerm(kinds[op], *children)

    term = encode(expression)
    solver.assertFormula(term)
    decision = solver.checkSat()
    result = {"engine": "cvc5", "status": str(decision), "term": str(term)}
    if decision.isSat():
        result["model"] = {k: str(solver.getValue(v)) for k, v in symbols.items()}
    if decision.isUnknown():
        result["reason"] = str(decision.getUnknownExplanation())
    return result


def solve_pair(declarations, expression, timeout_ms=3000):
    a = z3_query(declarations, expression, timeout_ms)
    b = cvc5_query(declarations, expression, timeout_ms)
    if a["status"] != b["status"]:
        status = "ENGINE_DISAGREEMENT"
    elif a["status"] not in {"sat", "unsat"}:
        status = "UNKNOWN"
    else:
        status = a["status"]
    return {"status": status, "query_hash": digest({"variables": declarations, "expression": expression}),
            "variables": declarations, "expression": expression, "z3": a, "cvc5": b}


def implication(declarations, antecedent, consequent, timeout_ms=3000):
    domain = solve_pair(declarations, antecedent, timeout_ms)
    if domain["status"] != "sat":
        return {"status": "VACUOUS" if domain["status"] == "unsat" else domain["status"], "domain": domain}
    counterexample = solve_pair(declarations, conjunction([antecedent, {"not": [consequent]}]), timeout_ms)
    status = {"unsat": "PROVED", "sat": "COUNTEREXAMPLE"}.get(counterexample["status"], counterexample["status"])
    return {"status": status, "domain": domain, "counterexample_query": counterexample}
