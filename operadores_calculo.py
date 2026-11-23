"""Operadores exactos del editor de Cálculo."""
import ast

import sympy as sp

from curso import polynomial
from motor_matematico.algorithms.linear.context import integer
from motor_matematico.parsing.numbers import parse_number


def limit(data, context):
    x = sp.Symbol("x", real=True)
    point = sp.Rational(parse_number(data["punto"]))
    direction = data["lado"]
    if direction not in ("-", "+"):
        raise ValueError("Elegí el lado de aproximación.")
    source = data["expresion"].strip()
    try:
        tree = ast.parse(source.replace("^", "**"), mode="eval").body
    except SyntaxError as error:
        raise ValueError("Revisá la expresión del límite.") from error
    normalized = source.replace("^", "**")
    if isinstance(tree, ast.BinOp) and isinstance(tree.op, ast.Div):
        numerator = polynomial(ast.get_source_segment(normalized, tree.left), (x,))
        denominator = polynomial(ast.get_source_segment(normalized, tree.right), (x,))
    else:
        numerator, denominator = polynomial(source, (x,)), sp.Integer(1)
    if denominator == 0:
        raise ValueError("El denominador no puede ser idénticamente cero.")
    reduced = sp.cancel(numerator / denominator)
    bound = rf"x\to {sp.latex(point)}^{{{direction}}}"
    context.emit("limite", "Simplificar la función racional para estudiar los valores cercanos al punto.",
                 {"punto": str(point), "lado": direction}, sp.latex(reduced))
    result = sp.limit(reduced, x, point, dir=direction)
    formula = rf"\lim_{{{bound}}} {sp.latex(reduced)} = {sp.latex(result)}"
    context.emit("limite_lateral", "Evaluar el límite por el lado elegido.", {"limite": str(result)}, formula)
    return {"limite": str(result), "formula_latex": formula}


def partial(data, context):
    x, y = sp.symbols("x y", real=True)
    variables = {"x": (x, y), "y": (y, x)}
    if data["variable"] not in variables:
        raise ValueError("Elegí x o y para la derivada parcial.")
    variable, constant = variables[data["variable"]]
    source = polynomial(data["expresion"], (x, y))
    derivative = sp.diff(source, variable)
    formula = rf"\frac{{\partial}}{{\partial {variable}}}\left({sp.latex(source)}\right)={sp.latex(derivative)}"
    context.emit("derivada_parcial", f"Derivar respecto de {variable} manteniendo {constant} constante.",
                 {"variable": str(variable), "constante": str(constant)}, formula)
    return {"derivada": str(derivative), "formula_latex": formula}
