"""Puente de Newton entre el árbol validado y SymPy."""
import ast

import sympy as sp
from sympy.printing.str import StrPrinter

from ...domain.models import InputError, ResourceLimitError
from ...parsing.numbers import parse_number


class FunctionNotation(StrPrinter):
    def _print_log(self, expr):
        return f"ln({self._print(expr.args[0])})"

    def _print_Abs(self, expr):
        return f"abs({self._print(expr.args[0])})"

    def _print_sign(self, expr):
        argument = self._print(expr.args[0])
        return f"(({argument})/abs({argument}))"

    def _print_Exp1(self, expr):
        return "e"


def symbolic_expression(tree, ctx, x=None, *, check=None):
    if x is None:
        x = sp.Symbol("x", real=True)
    functions = {name: getattr(sp, name) for name in ("sin", "cos", "tan", "asin", "acos", "atan", "exp")}
    functions.update(ln=sp.log, abs=sp.Abs, factorial=sp.factorial)
    constants = {"x": x, "pi": sp.pi, "e": sp.E, "Ans": sp.S.Zero}

    def convert(node):
        ctx.tick()
        if isinstance(node, ast.Constant):
            return sp.Rational(parse_number(node._literal))
        if isinstance(node, ast.Name):
            return constants[node.id]
        if isinstance(node, ast.UnaryOp):
            operand = visit(node.operand)
            return sp.Mul(-1, operand, evaluate=False) if isinstance(node.op, ast.USub) else operand
        if isinstance(node, ast.Call):
            arg = visit(node.args[0])
            name = node.func.id
            if name == "log":
                return sp.Mul(sp.log(arg, evaluate=False), 1 / sp.log(10), evaluate=False)
            if name == "sqrt":
                return sp.Pow(arg, sp.S.Half, evaluate=False)
            return functions[name](arg, evaluate=False)
        a, b = visit(node.left), visit(node.right)
        if isinstance(node.op, ast.Add):
            return sp.Add(a, b, evaluate=False)
        if isinstance(node.op, ast.Sub):
            return sp.Add(a, sp.Mul(-1, b, evaluate=False), evaluate=False)
        if isinstance(node.op, ast.Mult):
            return sp.Mul(a, b, evaluate=False)
        if isinstance(node.op, ast.Div):
            return sp.Mul(a, sp.Pow(b, -1, evaluate=False), evaluate=False)
        if b.is_Rational and abs(b) > 100:
            raise ResourceLimitError("La potencia supera el rango de evaluación de Newton.")
        return sp.Pow(a, b, evaluate=False)

    def visit(node):
        expression = convert(node)
        if check is not None:
            check(node, expression)
        return expression

    if sum(1 for _ in ast.walk(tree)) > 160:
        raise ResourceLimitError("La función es demasiado extensa para derivación simbólica.")
    return visit(tree)


def derivative_text(tree, ctx):
    x = sp.Symbol("x", real=True)
    expression = symbolic_expression(tree, ctx, x)
    try:
        derived = sp.diff(expression, x)
    except (ValueError, NotImplementedError) as error:
        raise InputError("No se pudo obtener una derivada real admitida. Ingresá f'(x).") from error
    if derived.has(sp.Derivative, sp.zoo, sp.nan, sp.oo, -sp.oo, sp.I):
        raise InputError("No se pudo obtener una derivada real admitida. Ingresá f'(x).")
    return FunctionNotation().doprint(derived)
