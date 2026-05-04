import operator
import re

OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
}

FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
}


def evaluate(expr: str, context: dict) -> float | bool:
    if expr.strip() in context:
        return context[expr.strip()]
    expr = expr.strip()
    for sym, op in OPERATORS.items():
        if f" {sym} " in expr:
            left, right = expr.split(f" {sym} ", 1)
            return op(
                _eval_part(left.strip(), context), _eval_part(right.strip(), context)
            )
    return _eval_part(expr, context)


def _eval_part(part: str, context: dict) -> float | bool:
    part = part.strip()
    if part in context:
        val = context[part]
        return (
            float(val)
            if isinstance(val, (int, float, str))
            and str(val).replace(".", "").replace("-", "").isdigit()
            else val
        )
    try:
        return float(part)
    except ValueError:
        pass
    if part.startswith("(") and part.endswith(")"):
        return evaluate(part[1:-1], context)
    func_match = re.match(r"(\w+)\((.+)\)", part)
    if func_match:
        fname, args = func_match.groups()
        if fname in FUNCTIONS:
            vals = [evaluate(a.strip(), context) for a in args.split(",")]
            return FUNCTIONS[fname](vals[0] if len(vals) == 1 else vals)
    return 0.0
