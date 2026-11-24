"""Descripción simbólica del cálculo de Newton-Raphson para su vista."""

from fractions import Fraction
import ast

from ..algorithms.calculo import analizar
from ..algorithms.linear.context import Context
from ..algorithms.numerical.functions import Function
from ..algorithms.numerical.symbolic import symbolic_expression
from ..domain.models import ResourceLimitError
from .derivative_view import expression_tex


def exact_root(function, approximation, tolerance):
    """Devuelve una expresión exacta que corresponde a la aproximación lograda."""
    import sympy as sp

    x = sp.Symbol("x", real=True)
    value = Fraction(approximation)
    tol = Fraction(tolerance)
    coefficients = function.polynomial
    if coefficients is not None:
        if not any(coefficients.values()) or max(coefficients) > 12:
            return None
        if any(max(c.numerator.bit_length(), c.denominator.bit_length()) > 128
               for c in coefficients.values()):
            return None
        polynomial = sp.Poly.from_dict(
            {degree: sp.Rational(coefficient) for degree, coefficient in coefficients.items()}, x
        )
        if polynomial.degree() <= 2:
            candidates = polynomial.real_roots()
        else:
            # Las raíces racionales de factores lineales y los radicales de
            # factores cuadráticos se pueden mostrar en una forma breve.
            candidates = [
                root for factor, _ in polynomial.factor_list()[1] if factor.degree() <= 2
                for root in factor.real_roots()
            ]
    else:
        # Comprueba candidatos simples sin llamar a un solucionador general.
        rational = sp.Rational(value.limit_denominator(128))
        multiple = sp.Rational(Fraction(float(value) / float(sp.pi)).limit_denominator(16))
        expression = symbolic_expression(function.tree, function.ctx, x)
        candidates = []
        for candidate in (rational, multiple * sp.pi):
            if abs(sp.N(candidate - sp.Rational(value), 30)) <= sp.Rational(tol):
                if expression.subs(x, candidate).doit().is_zero is True:
                    candidates.append(candidate)
        if not candidates and sum(1 for _ in ast.walk(function.tree)) <= 14:
            calls = list(expression.atoms(sp.exp, sp.log))
            if len(calls) == 1:
                call = calls[0]
                parameter = sp.Dummy(real=True)
                isolated = expression.xreplace({call: parameter})
                if not isolated.has(x) and isolated.is_polynomial(parameter) and call.args[0].is_polynomial(x):
                    if sp.degree(isolated, parameter) == sp.degree(call.args[0], x) == 1:
                        target, = sp.solve(isolated, parameter)
                        if target.is_real and (call.func == sp.log or target.is_positive):
                            inverse = sp.log(target) if call.func == sp.exp else sp.exp(target)
                            candidates = sp.solve(call.args[0] - inverse, x)
    if not candidates:
        return None
    root = min(candidates, key=lambda candidate: abs(sp.N(candidate - sp.Rational(value), 30)))
    if abs(sp.N(root - sp.Rational(value), 30)) <= sp.Rational(tol):
        return {"expresion": str(root), "latex": sp.latex(root)}
    return None


def describe_newton(data, response):
    result = response["result"]
    function = Function(data["expresion"], Context(collect_steps=False))
    metadata = response["metadata"]
    metadata["funcion_latex"] = expression_tex(function.tree)
    point = r"\left(\NEWTONPOINT\right)"
    metadata["funcion_sustitucion"] = expression_tex(function.tree, at_x=point)
    if result.get("derivada"):
        derivative = analizar(result["derivada"], variable=True)
        metadata["derivada_latex"] = expression_tex(derivative)
        metadata["derivada_sustitucion"] = expression_tex(derivative, at_x=point)
    if response["status"] == "ok" and data.get("criterio") == "paso_absoluto":
        try:
            result["raiz_exacta"] = exact_root(function, result["aproximacion"], result["tolerancia_x"])
        except (ArithmeticError, ValueError, NotImplementedError, ResourceLimitError):
            result["raiz_exacta"] = None
