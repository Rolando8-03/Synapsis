"""Métodos con desarrollo algebraico para Cálculo II."""
import sympy as sp

from calculo_i import X, function
from integracion import elementary, latex, primitive_result, step
from motor_matematico.domain.models import DomainError


def by_parts(data, ctx):
    f, domain, _ = function(data['expresion'], ctx)
    f = sp.factor(f)
    candidates = [term for term in sp.Mul.make_args(f) if term.func in (sp.exp, sp.sin, sp.cos, sp.log)]
    if len(candidates) != 1:
        raise DomainError('Ingresá un polinomio multiplicado por exp, seno, coseno afines o ln(x).')
    base = candidates[0]
    polynomial = sp.cancel(f/base)
    if not polynomial.is_polynomial(X) or sp.degree(polynomial,X) > 12:
        raise DomainError('El factor polinómico debe tener grado de hasta 12.')
    if base == sp.log(X):
        u, dv = base, polynomial
        du, v = sp.diff(u,X), elementary(sp.expand(dv))
        remainder = sp.cancel(v*du)
        step(ctx, 'Elegir u logarítmica e integrar el factor polinómico.',
             rf'u={latex(u)},\quad dv={latex(dv)}\,dx,\quad du={latex(du)}\,dx,\quad v={latex(v)}')
        step(ctx, 'Sustituir en uv menos la integral de v du.',
             rf'{latex(u*v)}-\int {latex(remainder)}\,dx')
        primitive = u*v - elementary(sp.expand(remainder),ctx=ctx)
    else:
        u, dv = polynomial, base
        primitive, sign = sp.S.Zero, 1
        while u != 0:
            du, v = sp.diff(u,X), elementary(dv)
            step(ctx, 'Elegir el polinomio como u para reducir su grado al derivar.',
                 rf'u={latex(u)},\quad dv={latex(dv)}\,dx,\quad du={latex(du)}\,dx,\quad v={latex(v)}')
            step(ctx, 'Sustituir en uv menos la integral de v du.',
                 rf'{latex(u*v)}-\int {latex(v*du)}\,dx')
            primitive += sign*u*v
            u, dv, sign = du, v, -sign
    primitive = sp.factor(primitive)
    step(ctx, 'Simplificar los términos obtenidos por partes.', latex(primitive) + '+C')
    return primitive_result(f, primitive, domain, ctx)


def partial_fractions(data, ctx):
    original, domain, _ = function(data['expresion'], ctx)
    f = sp.cancel(original)
    numerator, denominator = sp.fraction(f)
    try:
        p, q = (sp.Poly(part,X,domain=sp.QQ) for part in (numerator,denominator))
    except (sp.PolynomialError, sp.CoercionFailed) as error:
        raise DomainError('Ingresá un cociente de polinomios con coeficientes racionales.') from error
    if not 1 <= q.degree() <= 8 or p.degree() > 20:
        raise DomainError('Usá un denominador no constante de grado hasta 8 y numerador de grado hasta 20.')
    p, q = p.mul_ground(1/q.LC()), q.monic()
    whole, remainder = p.div(q)
    denominator = q.as_expr()
    _, factors = q.factor_list()
    if any(factor.degree()!=1 or power!=1 for factor,power in factors):
        raise DomainError('Este desarrollo admite factores lineales simples.')
    if whole:
        step(ctx, 'Dividir el numerador por el denominador para separar la parte polinómica.',
             latex(f) + '=' + latex(whole.as_expr()) + '+' + latex(remainder.as_expr()/denominator),
             cociente=str(whole.as_expr()), residuo=str(remainder.as_expr()))
    factored = sp.Mul(*(factor.as_expr()**power for factor,power in factors))
    step(ctx, 'Factorizar el denominador y conservar las exclusiones de la función original.',
         latex(denominator) + '=' + latex(factored), dominio=str(domain))
    unknowns = iter(sp.symbols(f'A_1:{q.degree()+1}'))
    template = [(next(unknowns),factor,power) for factor,power in factors]
    expanded = sum(n*q.exquo(factor**power).as_expr() for n,factor,power in template)
    identity = remainder.as_expr() - expanded
    coefficients = sp.Poly(identity,X).all_coeffs()
    step(ctx, 'Multiplicar la descomposición por el denominador e igualar los numeradores.',
         latex(remainder.as_expr())+'='+latex(expanded))
    parameters = sorted(identity.free_symbols-{X}, key=str)
    matrix, rhs = sp.linear_eq_to_matrix(coefficients, parameters)
    values = matrix.inv() * rhs
    solved = dict(zip(parameters,values))
    equations = r'\quad '.join(latex(equation)+'=0' for equation in coefficients)
    step(ctx, 'Igualar coeficientes de potencias de x y resolver el sistema.', equations,
         coeficientes={str(key):str(value) for key,value in solved.items()})
    decomposition = whole.as_expr() + sum(n.subs(solved)/factor.as_expr()**power for n,factor,power in template)
    reconstructed = sp.cancel(decomposition*denominator)
    if reconstructed != p.as_expr():
        raise DomainError('La descomposición debe reconstruir exactamente el numerador.')
    step(ctx, 'Reconstruir el numerador antes de integrar.',
         rf'\left({latex(decomposition)}\right)\left({latex(factored)}\right)={latex(reconstructed)}')
    primitive = elementary(decomposition, ctx=ctx)
    return {**primitive_result(original, primitive, domain, ctx), 'descomposicion':str(decomposition),
            'numerador_reconstruido':str(reconstructed)}
