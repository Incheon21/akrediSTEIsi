"""Evaluate scoring expressions without executing Python code."""

import ast
import math
import operator

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_COMPARE = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}
_FUNCTIONS = {"min": min, "max": max}
_MATH = {
    name: getattr(math, name)
    for name in (
        "sqrt",
        "log",
        "log10",
        "exp",
        "floor",
        "ceil",
        "fabs",
        "pow",
    )
}


def evaluate_formula(expression: str, variables: dict) -> float | bool:
    """Accept numeric arithmetic, comparisons, booleans and approved functions."""
    if len(expression) > 1024:
        raise ValueError("Formula too long")
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 128:
        raise ValueError("Formula too complex")

    def number(value):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Expected a finite number")
        return float(value)

    def visit(node):
        if isinstance(node, ast.Constant):
            return number(node.value)
        if isinstance(node, ast.Name):
            return number(variables[node.id])
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            return number(
                _BINARY[type(node.op)](
                    number(visit(node.left)), number(visit(node.right))
                )
            )
        if isinstance(node, ast.UnaryOp):
            value = visit(node.operand)
            if isinstance(node.op, ast.Not):
                return not value
            if isinstance(node.op, ast.UAdd):
                return number(value)
            if isinstance(node.op, ast.USub):
                return -number(value)
        if isinstance(node, ast.Compare):
            left = visit(node.left)
            for op, right_node in zip(node.ops, node.comparators):
                if type(op) not in _COMPARE:
                    raise ValueError("Unsupported comparison")
                right = visit(right_node)
                if not _COMPARE[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(visit(value) for value in node.values)
            if isinstance(node.op, ast.Or):
                return any(visit(value) for value in node.values)
        if isinstance(node, ast.Call) and not node.keywords:
            function = None
            if isinstance(node.func, ast.Name):
                function = _FUNCTIONS.get(node.func.id)
            elif (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "math"
            ):
                function = _MATH.get(node.func.attr)
            if function is not None:
                return number(function(*(number(visit(arg)) for arg in node.args)))
        raise ValueError("Unsupported formula syntax")

    return visit(tree.body)
