"""Métodos con desarrollo algebraico para Cálculo II."""
import sympy as sp

from calculo_i import R, X, condition_set, exact, function
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
    if any(factor.degree()>2 or (factor.degree()==2 and (power!=1 or sp.discriminant(factor)>=0))
           for factor,power in factors):
        raise DomainError('Usá factores lineales o cuadráticos irreducibles de multiplicidad uno y discriminante negativo.')
    if whole:
        step(ctx, 'Dividir el numerador por el denominador para separar la parte polinómica.',
             latex(f) + '=' + latex(whole.as_expr()) + '+' + latex(remainder.as_expr()/denominator),
             cociente=str(whole.as_expr()), residuo=str(remainder.as_expr()))
    factored = sp.Mul(*(factor.as_expr()**power for factor,power in factors))
    step(ctx, 'Factorizar el denominador y conservar las exclusiones de la función original.',
         latex(denominator) + '=' + latex(factored), dominio=str(domain))
    unknowns = iter(sp.symbols(f'A_1:{q.degree()+1}'))
    template = []
    for factor, multiplicity in factors:
        for power in range(1,multiplicity+1):
            n = sum(next(unknowns)*X**k for k in range(factor.degree()-1,-1,-1))
            template.append((n,factor,power))
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
    primitive = elementary(whole.as_expr(),ctx=ctx) if whole else sp.S.Zero
    for n, factor, power in template:
        d, numerator = factor.as_expr(), n.subs(solved)
        if numerator == 0:
            continue
        if factor.degree() == 1:
            primitive += elementary(numerator/d**power,ctx=ctx)
            continue
        # d=L((x+h)^2+k^2) y n=A d' + B.
        leading = factor.LC()
        h = factor.nth(1)/(2*leading)
        k = sp.sqrt(factor.nth(0)/leading-h**2)
        A = sp.Poly(numerator,X).nth(1)/(2*leading)
        B = sp.expand(numerator-A*sp.diff(d,X))
        term = A*sp.log(d) + B/(leading*k)*sp.atan((X+h)/k)
        step(ctx, 'Completar el cuadrado y separar el término de logaritmo del de arcotangente.',
             rf'{latex(d)}={latex(leading)}\left({latex((X+h)**2)}+{latex(k**2)}\right),\quad {latex(numerator)}={latex(A*sp.diff(d,X))}+{latex(B)}')
        step(ctx, 'Integrar la fracción con denominador cuadrático positivo.',
             rf'\int {latex(numerator/d)}\,dx={latex(term)}+C')
        primitive += term
    return {**primitive_result(original, primitive, domain, ctx), 'descomposicion':str(decomposition),
            'numerador_reconstruido':str(reconstructed)}


def exponent(value, label):
    n = exact(value)
    if not n.is_Integer or not 0 <= n <= 12:
        raise ValueError(f'{label} debe ser un entero entre 0 y 12.')
    return int(n)


def sine_cosine(m, n, ctx):
    s, c = sp.sin(X), sp.cos(X)
    u = sp.Symbol('u', real=True)
    if m % 2:
        inner, adjusted = c, -(1-u**2)**((m-1)//2)*u**n
        formula = r'u=\cos x,\quad du=-\sin x\,dx,\quad \sin^2 x=1-u^2'
        reason = 'El exponente del seno es impar. Reservar un seno para el diferencial.'
    elif n % 2:
        inner, adjusted = s, (1-u**2)**((n-1)//2)*u**m
        formula = r'u=\sin x,\quad du=\cos x\,dx,\quad \cos^2 x=1-u^2'
        reason = 'El exponente del coseno es impar. Reservar un coseno para el diferencial.'
    else:
        step(ctx, 'Los dos exponentes son pares. Reducir de dos en dos usando la identidad pitagórica y partes.',
             r'I_{m,n}=-\frac{\sin^{m-1}(x)\cos^{n+1}(x)}{m+n}+\frac{m-1}{m+n}I_{m-2,n}\quad(m\ge2)')
        value = X
        for j in range(2,n+1,2):
            value = s*c**(j-1)/j + sp.Rational(j-1,j)*value
            step(ctx, 'Reducir la potencia par del coseno.', rf'I_{{0,{j}}}={latex(value)}')
        for i in range(2,m+1,2):
            value = -s**(i-1)*c**(n+1)/(i+n) + sp.Rational(i-1,i+n)*value
            step(ctx, 'Reducir la potencia par del seno.', rf'I_{{{i},{n}}}={latex(value)}')
        return value
    step(ctx, reason, formula)
    step(ctx, 'La identidad deja un polinomio en u.', rf'\int {latex(adjusted)}\,du')
    return elementary(sp.expand(adjusted),u,ctx).subs(u,inner)


def tangent_cotangent(m, fn, ctx):
    z = fn(X)
    tangent = fn == sp.tan
    orientation = 1 if tangent else -1
    axis = sp.cos(X) if tangent else sp.sin(X)
    identity = r'\tan^2x=\sec^2x-1,\quad d(\tan x)=\sec^2x\,dx' if tangent else (
               r'\cot^2x=\csc^2x-1,\quad d(\cot x)=-\csc^2x\,dx')
    step(ctx, 'Reservar el cuadrado de la secante o cosecante para el diferencial.', identity)
    value = -orientation*sp.log(sp.Abs(axis)) if m % 2 else X
    step(ctx, 'La reducción de dos en dos termina en exponente uno si es impar, o cero si es par.',
         rf'I_{{{m%2}}}={latex(value)}')
    for j in range(2+m%2,m+1,2):
        value = orientation*z**(j-1)/(j-1)-value
        step(ctx, 'Integrar la potencia de la variable sustituida y restar la potencia anterior.',
             rf'I_{{{j}}}={latex(value)}')
    return z**m, value, condition_set(axis,X,'no_cero') if m else R


def secant_cosecant(m, fn, ctx):
    z = fn(X)
    secant = fn == sp.sec
    orientation = 1 if secant else -1
    companion = sp.tan(X) if secant else sp.cot(X)
    axis = sp.cos(X) if secant else sp.sin(X)
    differential = r'd(\tan x)=\sec^2x\,dx' if secant else r'd(\cot x)=-\csc^2x\,dx'
    step(ctx, 'Reservar la potencia cuadrada para el diferencial. Reducir por partes y la identidad pitagórica.',
         differential)
    value = sp.log(sp.Abs(z+orientation*companion)) if m % 2 else X
    step(ctx, 'La paridad fija el caso base. En exponente impar se usa el logaritmo del producto auxiliar.',
         rf'I_{{{m%2}}}={latex(value)}')
    for j in range(2+m%2,m+1,2):
        value = orientation*z**(j-2)*companion/(j-1) + sp.Rational(j-2,j-1)*value
        step(ctx, 'Integrar por partes el factor reservado y reducir dos potencias.', rf'I_{{{j}}}={latex(value)}')
    return z**m, value, condition_set(axis,X,'no_cero') if m else R


def trig_powers(data, ctx):
    m = exponent(data['potencia'], 'El primer exponente')
    n = exponent(data.get('potencia_coseno','0'), 'El exponente del coseno')
    family = data['familia']
    if family == 'seno_coseno':
        f = sp.sin(X)**m*sp.cos(X)**n
        return primitive_result(f,sine_cosine(m,n,ctx),R,ctx)
    if family in ('tangente','cotangente'):
        f, value, domain = tangent_cotangent(m,sp.tan if family=='tangente' else sp.cot,ctx)
        return primitive_result(f,value,domain,ctx)
    if family in ('secante','cosecante'):
        f, value, domain = secant_cosecant(m,sp.sec if family=='secante' else sp.csc,ctx)
        return primitive_result(f,value,domain,ctx)
    raise ValueError('Elegí una familia de potencias trigonométricas.')


def trig_substitution(data, ctx):
    a = exact(data['parametro'])
    if a <= 0:
        raise ValueError('El parámetro a debe ser positivo.')
    theta = sp.Symbol('theta', real=True)
    family = data['familia']
    if family == 'diferencia':
        radicand = a**2-X**2
        domain, angles = sp.Interval(-a,a), r'-\pi/2\le\theta\le\pi/2'
        transform = a*sp.sin(theta)
        reduced_root = a*sp.cos(theta)
        in_theta = a**2*(theta+sp.sin(theta)*sp.cos(theta))/2
        inverse = sp.asin(X/a)
        value = (X*sp.sqrt(radicand)+a**2*inverse)/2
        identity = r'1-\sin^2\theta=\cos^2\theta,\quad \cos\theta\ge0'
    else:
        raise ValueError('Elegí una familia de radicales.')
    root = sp.sqrt(radicand)
    dx = sp.diff(transform,theta)
    step(ctx, 'Elegir la sustitución y restringir θ para fijar el signo del radical.',
         rf'x={latex(transform)},\quad {angles},\quad dx={latex(dx)}\,d\theta', dominio=str(domain))
    step(ctx, 'Aplicar la identidad y extraer la raíz con el signo del intervalo.',
         rf'{identity},\quad \sqrt{{{latex(radicand)}}}={latex(reduced_root)}')
    step(ctx, 'Multiplicar por el diferencial e integrar en θ.',
         rf'\int {latex(reduced_root*dx)}\,d\theta={latex(in_theta)}+C')
    step(ctx, 'Regresar a x con la función inversa y el radical original.',
         rf'\theta={latex(inverse)},\quad F(x)={latex(value)}')
    return primitive_result(root,value,domain,ctx)
