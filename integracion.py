"""Reglas elementales, sustitución y comprobación de primitivas reales."""
import sympy as sp

from calculo_i import R, X, function, interval, require_interval
from motor_matematico.domain.models import DomainError


def step(ctx, message, formula='', **evidence):
    ctx.emit('calculo_ii', message, evidence, formula)


def latex(value):
    return sp.latex(value)


def integral_tex(f, a, b, variable=X):
    return rf'\int_{{{latex(a)}}}^{{{latex(b)}}}\left({latex(f)}\right)\,d{latex(variable)}'


def verify(f, primitive, domain, ctx, variable=X):
    # En un intervalo donde h no se anula, d ln|h|/dx = h'/h.
    logs = {log: sp.log(log.args[0].args[0], evaluate=False)
            for log in primitive.atoms(sp.log) if log.args[0].func == sp.Abs}
    difference = sp.diff(primitive.xreplace(logs), variable) - f
    reduced = sp.simplify(difference)
    if reduced != 0 and sp.trigsimp(reduced) != 0:
        raise DomainError('No se pudo comprobar la primitiva en los intervalos indicados.')
    step(ctx, 'Derivar la primitiva en cada intervalo del dominio, con una constante independiente por intervalo.',
         rf'F^\prime({latex(variable)})={latex(f)}', dominio=str(domain), diferencia='0')


def primitive_result(f, primitive, domain, ctx):
    verify(f, primitive, domain, ctx)
    return {'primitiva': str(primitive) + ' + C', 'dominio': str(domain),
            'formula_latex': latex(primitive) + '+C'}


def elementary(f, variable=X, ctx=None):
    """Integrar sumas de potencias, exponenciales y seno/coseno afines."""
    result = sp.S.Zero
    for term in sp.Add.make_args(f):
        coefficient, core = term.as_independent(variable, as_Add=False)
        if core == 1:
            primitive, rule = coefficient*variable, 'constante'
            slope = sp.S.One
        else:
            if core.func in (sp.exp, sp.sin, sp.cos):
                argument = core.args[0]
                transformed = {sp.exp:sp.exp, sp.sin:lambda z: -sp.cos(z), sp.cos:sp.sin}[core.func]
                antiderivative, rule = transformed(argument), core.func.__name__
            else:
                argument, power = core.as_base_exp()
                if not power.is_Rational:
                    raise DomainError('La regla elemental requiere una potencia racional o seno, coseno o exp afines.')
                if power == -1:
                    antiderivative, rule = sp.log(sp.Abs(argument)), 'logaritmo de valor absoluto'
                else:
                    antiderivative, rule = argument**(power+1)/(power+1), 'potencia'
            slope = sp.diff(argument, variable)
            if slope == 0 or slope.has(variable):
                raise DomainError('Para esta regla el argumento debe ser afín. Probá elegir una sustitución.')
            primitive = coefficient*antiderivative/slope
        if ctx is not None:
            step(ctx, f'Aplicar la regla de {rule} a este término.',
                 rf'\int {latex(term)}\,d{latex(variable)}={latex(primitive)}+C',
                 coeficiente=str(coefficient), ajuste_afin=str(1/slope))
        result += primitive
    return result


def shared_primitive(data, out, ctx):
    """Desarrollar y certificar el mismo resultado que consume el historial."""
    f, domain, _ = function(data['expresion'], ctx)
    if domain.interior == sp.EmptySet:
        raise DomainError('La función requiere un intervalo real para integrar.')
    primitive, _, _ = function(out['primitiva_sin_constante'], ctx)
    # Mostrar la regla operativa cuando la forma canónica admite el desarrollo elemental.
    try:
        elementary(sp.expand(f, power_base=False), ctx=ctx)
    except DomainError:
        pass
    verify(f, primitive, domain, ctx)
    out.update(dominio=str(domain), formula_latex=latex(primitive) + '+C')


def substitution(data, ctx):
    f, domain, _ = function(data['expresion'], ctx)
    inner, inner_domain, _ = function(data['sustitucion'], ctx)
    domain &= inner_domain
    slope = sp.diff(inner, X)
    if slope == 0 or domain.interior == sp.EmptySet:
        raise DomainError('Elegí una sustitución variable en un intervalo real común.')
    u = sp.Symbol('u', real=True)
    adjusted = sp.factor(sp.cancel(f/slope))
    quotient = adjusted.subs(sp.factor(inner), u)
    if quotient.has(X) and inner.is_polynomial(X):
        numerator, denominator = sp.fraction(adjusted)
        if numerator.is_polynomial(X) and denominator.is_polynomial(X):
            relation = sp.Poly(inner-u, X, domain=sp.QQ.frac_field(u)) if all(
                c.is_Rational for c in sp.Poly(inner, X).all_coeffs()) else None
            if relation is not None:
                quotient = sp.cancel(sp.rem(numerator, relation.as_expr(), X)/sp.rem(denominator, relation.as_expr(), X))
    if quotient.has(X) or quotient.has(sp.zoo, sp.nan):
        raise DomainError('Elegí u de modo que f(x)/(du/dx) pueda escribirse solo en u.')
    step(ctx, 'Elegir u y expresar el diferencial.', rf'u={latex(inner)},\quad du={latex(slope)}\,dx')
    step(ctx, 'Ajustar el integrando y expresarlo en u.',
         rf'\int {latex(f)}\,dx=\int {latex(quotient)}\,du', integrando_en_u=str(quotient))
    in_u = elementary(sp.expand(quotient, power_base=False), u, ctx)
    primitive = in_u.subs(u, inner)
    step(ctx, 'Regresar a x antes de evaluar o escribir la constante.', latex(primitive) + '+C')
    result = primitive_result(f, primitive, domain, ctx)
    if data.get('inferior') is not None or data.get('superior') is not None:
        if not str(data.get('inferior', '')).strip() or not str(data.get('superior', '')).strip():
            raise ValueError('Ingresá ambos extremos para evaluar la integral definida.')
        a, b, region = interval(data)
        require_interval(domain, region)
        value = sp.simplify(primitive.subs(X,b)-primitive.subs(X,a))
        step(ctx, 'Evaluar los extremos después de regresar a x.', integral_tex(f,a,b) + '=' + latex(value))
        result['valor'] = str(value)
    return result


def shared_definite(data, out, ctx):
    from motor_matematico.algorithms.calculo import analizar
    from motor_matematico.algorithms.numerical.symbolic import symbolic_expression

    if not out.get('expresion'):
        step(ctx, 'Usar Simpson adaptativo cuando las reglas admitidas no dan una primitiva.',
             tolerancia=out.get('tolerancia_absoluta'), aproximacion=out['valor'])
        return
    f, primitive = (symbolic_expression(analizar(source,variable=True),ctx)
                    for source in (data['expresion'],out['expresion']))
    a, b = (sp.simplify(symbolic_expression(analizar(data[key]),ctx)) for key in ('inferior','superior'))
    Fa, Fb = (sp.simplify(primitive.subs(X,point)) for point in (a,b))
    step(ctx, 'El motor comprobó la continuidad en el intervalo. Escribir una primitiva.',
         rf'F(x)={latex(primitive)}')
    step(ctx, 'Aplicar el teorema fundamental y restar las evaluaciones en orden.',
         integral_tex(f,a,b)+rf'=F({latex(b)})-F({latex(a)})={latex(Fb)}-\left({latex(Fa)}\right)',
         inferior=str(Fa), superior=str(Fb), valor=out['valor'], exactitud=out['exactitud'])
