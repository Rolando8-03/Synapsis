"""Analizador de polinomios con sintaxis acotada y coeficientes exactos."""
import ast
import re

import sympy as sp

from .numbers import parse_number


def polynomial(source, variables):
    """Construir polinomios desde nodos permitidos sin ejecutar texto del usuario."""
    text = str(source).strip().replace('−', '-').replace('·', '*').replace('^', '**')
    if not text or len(text) > 500:
        raise ValueError('Escribí un polinomio de hasta 500 caracteres.')
    names = {str(symbol): symbol for symbol in variables}
    text = re.sub(r'(?<=[0-9)])(?=(?:[a-df-zA-DF-Z(]|[eE](?![+-]?\d)))', '*', text)
    text = re.sub(r'(?<=[A-Za-z])(?=\()', '*', text)
    try:
        tree = ast.parse(text, mode='eval')
    except SyntaxError as error:
        raise ValueError('Revisá la expresión. Usá * para multiplicar y ^ para elevar.') from error
    if sum(1 for _ in ast.walk(tree)) > 110:
        raise ValueError('La expresión supera el tamaño permitido.')

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = parse_number(ast.get_source_segment(text, node))
            return sp.Rational(value.numerator, value.denominator)
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = visit(node.operand)
            return -operand if isinstance(node.op, ast.USub) else operand
        if not isinstance(node, ast.BinOp):
            raise ValueError('Usá números, variables declaradas y operaciones de polinomios.')
        a, b = visit(node.left), visit(node.right)
        if isinstance(node.op, ast.Add):
            value = a + b
        elif isinstance(node.op, ast.Sub):
            value = a - b
        elif isinstance(node.op, ast.Mult):
            value = a * b
        elif isinstance(node.op, ast.Div) and b.is_Rational and b != 0:
            value = a / b
        elif isinstance(node.op, ast.Pow) and b.is_Integer and 0 <= b <= 8:
            value = a ** int(b)
        else:
            raise ValueError('Usá exponentes enteros entre 0 y 8 y divisores constantes no nulos.')
        if value.is_Rational:
            if max(int(value.p).bit_length(), int(value.q).bit_length()) > 384:
                raise ValueError('Los coeficientes individuales son demasiado grandes.')
            return value
        if isinstance(node.op, (ast.Mult, ast.Pow)):
            a_poly = sp.Poly(a, *variables)
            increment = int(b)*a_poly.total_degree() if isinstance(node.op, ast.Pow) else a_poly.total_degree()+sp.Poly(b,*variables).total_degree()
            if increment > 8 or (len(a_poly.terms()) > 12 and not b.is_Rational):
                raise ValueError('El polinomio intermedio es demasiado grande.')
        poly = sp.Poly(value, *variables)
        if len(poly.terms()) > 70 or poly.total_degree() > 8:
            raise ValueError('Se admiten hasta 70 términos y grado total 8.')
        if any(max(int(coef.p).bit_length(), int(coef.q).bit_length()) > 384 for coef in poly.coeffs()):
            raise ValueError('Los coeficientes individuales son demasiado grandes.')
        return poly.as_expr()

    return visit(tree.body)
