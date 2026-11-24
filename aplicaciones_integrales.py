"""Planteamientos de integrales a partir de un modelo geométrico o físico."""
from fractions import Fraction
from math import isfinite

import sympy as sp

from calculo_i import X, exact, finite_roots, function, interval, midpoint, require_interval
from curso import polynomial
from integracion import elementary, integral_tex, latex, step
from motor_matematico.algorithms.calculo import analizar, evaluar, integral_numerica
from motor_matematico.algorithms.numerical.symbolic import FunctionNotation
from motor_matematico.domain.models import DomainError


def plot_number(value):
    number = float(value)
    if not isfinite(number) or abs(number) > 1e90:
        raise DomainError('La magnitud es demasiado grande para graficarla.')
    return number


def riemann(data, ctx):
    a, b, region = interval(data)
    n = exact(data['n'])
    if not n.is_Integer or not 1 <= n <= 32:
        raise ValueError('Elegí entre 1 y 32 rectángulos.')
    method = data['muestra']
    offsets = {'izquierda':sp.S.Zero, 'medio':sp.S.Half, 'derecha':sp.S.One}
    if method not in offsets:
        raise ValueError('Elegí izquierda, punto medio o derecha.')
    f, domain, _ = function(data['expresion'],ctx)
    require_interval(domain,region)
    poly = sp.Poly(f,X) if f.is_polynomial(X) else None
    is_exact = poly is not None and all(coef.is_Rational for coef in poly.all_coeffs())
    tree = analizar(data['expresion'],variable=True)
    cache = {}

    def sample(x):
        if x not in cache:
            cache[x] = poly.eval(x) if is_exact else plot_number(evaluar(tree,x=Fraction(x)))
        return cache[x]

    frames = []
    offset = offsets[method]
    for count in range(1,33):
        width = (b-a)/count
        knots = [a+i*width for i in range(count+1)]
        xs = [x+offset*width for x in knots[:-1]]
        heights = [sample(x) for x in xs]
        total = width*sum(heights) if is_exact else plot_number(width)*sum(heights)
        frames.append({'n':count, 'ancho':str(width), 'suma':str(total) if is_exact else format(total,'.10g'),
                       'puntos':[[plot_number(x),plot_number(y)] for x,y in zip(xs,heights)],
                       'particion':[plot_number(x) for x in knots], 'primera_muestra':str(xs[0])})
    curve = [[plot_number(x),plot_number(sample(x))] for x in (a+(b-a)*i/80 for i in range(81))]
    first = frames[int(n)-1]
    sample_formula = {'izquierda':r'x^*_i=x_{i-1}', 'medio':r'x^*_i=(x_{i-1}+x_i)/2', 'derecha':r'x^*_i=x_i'}[method]
    step(ctx,'Partir el intervalo en n subintervalos del mismo ancho.',
         r'\Delta x=(b-a)/n,\quad x_i=a+i\Delta x', ancho=first['ancho'])
    step(ctx,'Elegir un punto de muestra en cada subintervalo.',sample_formula,
         primera_muestra=first['primera_muestra'])
    summation = r'S_n=\sum_{i=1}^n f(x_i^*)\,\Delta x'
    step(ctx,'Sumar las áreas con signo según la altura de los rectángulos.',summation,suma=first['suma'])
    return {'formula_latex':summation,'exactitud':'exacta' if is_exact else 'aproximada',
            'visual_integral':{'tipo':'riemann','curva':curve,'cuadros':frames,'inicial':int(n)-1,
                              'exacta':is_exact}}


def evaluate_primitive(primitive, a, b, variable=X):
    value = sp.simplify(primitive.subs(variable,b)-primitive.subs(variable,a))
    if value.has(sp.nan, sp.zoo, sp.oo, -sp.oo, sp.I, sp.Integral):
        raise DomainError('La evaluación no produce un valor real finito.')
    return value


def exact_integral(f, a, b):
    return evaluate_primitive(elementary(sp.expand(f,power_base=False)),a,b)


def wants_value(data):
    mode = data.get('entrega','plantear')
    if mode not in ('plantear','resolver'):
        raise ValueError('Elegí plantear o resolver.')
    return mode == 'resolver'


def net_change(data, ctx):
    a, b, region = interval(data)
    f, domain, _ = function(data['expresion'],ctx)
    require_interval(domain,region)
    quantity, time = (str(data.get(key,'')).strip() for key in ('unidad_cantidad','unidad_tiempo'))
    if len(quantity)>24 or len(time)>24:
        raise ValueError('Escribí unidades de hasta 24 caracteres.')
    mode = data.get('entrega','cambio')
    if mode not in ('cambio','final'):
        raise ValueError('Elegí obtener el cambio o el valor final.')
    initial = None
    if mode == 'final':
        if not str(data.get('inicial','')).strip():
            raise ValueError('Ingresá el valor inicial para calcular el valor final.')
        initial = exact(data['inicial'])
    formula = r'\Delta Q=' + integral_tex(f,a,b)
    step(ctx,'Integrar la tasa sobre el intervalo y multiplicar sus unidades por la unidad de la variable.',
         formula, unidad_tasa='/'.join(piece for piece in (quantity,time) if piece), unidad_cambio=quantity)
    primitive = elementary(sp.expand(f,power_base=False),ctx=ctx)
    change = evaluate_primitive(primitive,a,b)
    step(ctx,'Evaluar la primitiva de la tasa para hallar el cambio neto.',formula+'='+latex(change))
    result = {'cambio_neto':str(change), 'unidad':quantity, 'formula_latex':formula+'='+latex(change)}
    if initial is not None:
        final = initial+change
        step(ctx,'Sumar el cambio neto al valor inicial.',
             rf'Q(b)=Q(a)+\Delta Q={latex(initial)}+\left({latex(change)}\right)={latex(final)}')
        result.update(valor_final=str(final),valor_inicial=str(initial))
    return result


def partition(a, b, *expressions):
    interior = set()
    for expression in expressions:
        if expression != 0:
            interior.update(finite_roots(expression,sp.Interval.open(a,b)))
    cuts = [a,*sorted(interior),b]
    return list(zip(cuts,cuts[1:]))



def area_model(f, g, spans, terms):
    """Conserva cada tramo exacto y su contorno para explorar el planteamiento."""
    if len(spans) > 12:
        return None
    curve, frames = [], []
    for (left,right), term in zip(spans,terms):
        points = []
        for i in range(33):
            x = left + (right-left)*sp.Rational(i,32)
            points.append([plot_number(value) for value in (x,f.subs(X,x),g.subs(X,x))])
        curve.extend(points)
        upper = 'f(x)' if f.subs(X,midpoint(left,right)) >= g.subs(X,midpoint(left,right)) else 'g(x)'
        frames.append({'izquierda':str(left), 'derecha':str(right), 'superior':upper,
                       'formula_latex':term, 'banda':points})
    return {'tipo':'area', 'curva':curve, 'cuadros':frames, 'inicial':0, 'etiquetas':['f(x)','g(x)']}


def area(data, ctx):
    second = str(data.get('segunda') or '').strip()
    g = polynomial(second,(X,)) if second else sp.S.Zero
    f, domain, _ = function(data['expresion'],ctx)
    difference = sp.expand(f-g) if f.is_polynomial(X) else sp.simplify(f-g)
    left, right = (str(data.get(key,'')).strip() for key in ('inferior','superior'))
    if left and right:
        a, b, region = interval(data)
    elif left or right:
        raise ValueError('Indicá los dos extremos para seleccionar la región.')
    else:
        if not second or difference==0 or not difference.is_polynomial(X):
            raise DomainError('Indicá el intervalo de la región. La detección automática requiere dos curvas polinómicas distintas.')
        crossings = sorted(finite_roots(difference))
        if len(crossings) < 2:
            raise DomainError('Se requieren dos cruces para encerrar una región. Indicá los límites.')
        regions = list(zip(crossings,crossings[1:]))
        if len(regions)>1 and not str(data.get('region','')).strip():
            options = '; '.join(f'{i}: [{p}, {q}]' for i,(p,q) in enumerate(regions,1))
            raise DomainError(f'Elegí el número de región o escribí ambos límites. Regiones de izquierda a derecha: {options}.')
        selected = exact(data.get('region') or '1')
        if not selected.is_Integer or not 1 <= selected <= len(regions):
            raise ValueError(f'Escribí un número de región entre 1 y {len(regions)}.')
        a, b = regions[int(selected)-1]
        region = sp.Interval(a,b)
    require_interval(domain,region)
    spans = partition(a,b,difference)
    crossings = [str(x) for x in [a,*(r for _,r in spans)] if difference!=0 and difference.subs(X,x).equals(0)]
    if crossings:
        step(ctx, 'Igualar las curvas para identificar los cruces en la región.',
             latex(f)+'='+latex(g), cruces=crossings)
    sign_integral = integral_tex(difference,a,b)
    if not second:
        step(ctx, 'La integral con signo resta los aportes por debajo del eje. Para el área, esas alturas se hacen positivas.',
             sign_integral)
    terms = []
    total = sp.S.Zero
    evaluate = wants_value(data)
    for l,r in spans:
        mid = midpoint(l,r)
        sign = -1 if difference.subs(X,mid)<0 else 1
        height = sign*difference
        term = integral_tex(height,l,r)
        step(ctx, 'Comparar las alturas en este tramo para restar la curva inferior de la superior.',term,
             superior='f' if sign==1 else ('g' if second else 'eje x'), muestra=str(mid))
        terms.append(term)
        if evaluate:
            total += exact_integral(height,l,r)
    formula = 'A=' + '+'.join(terms)
    result = {'formula_latex':formula, 'cruces':crossings, 'curvas_coincidentes':difference==0}
    try:
        visual = area_model(f,g,spans,terms)
    except (DomainError, ArithmeticError, ValueError, TypeError):
        visual = None
    if visual:
        result['visual_integral'] = visual
    if evaluate:
        result['area'] = str(sp.simplify(total))
        if not second:
            result['integral_con_signo'] = str(exact_integral(difference,a,b))
        step(ctx, 'Evaluar las integrales y sumar sus áreas geométricas.',formula+'='+latex(sp.simplify(total)))
    return result


def radial_slice(first, second):
    far = max(abs(first),abs(second))
    near = sp.S.Zero if first*second <= 0 else min(abs(first),abs(second))
    return far, near


def volume(data, ctx, *, washers=False):
    a, b, _ = interval(data)
    axis = exact(data.get('eje') or '0')
    f = polynomial(data['expresion'],(X,))
    g = polynomial(data['segunda'],(X,)) if washers else axis
    d, e = f-axis, g-axis
    evaluate = wants_value(data)
    step(ctx, 'Medir los radios como distancias verticales al eje horizontal.',
         rf'y={latex(axis)},\quad d_f=\left|{latex(d)}\right|,\quad d_g=\left|{latex(e)}\right|')
    if washers:
        step(ctx,'Usar la frontera más alejada para R. Si la sección toca o cruza el eje, el hueco es cero.',
             r'A(x)=\pi(R^2-r^2),\quad R=\max(d_f,d_g),\quad r=0\ \text{si el eje atraviesa la región}')
    else:
        step(ctx, 'La región llega hasta el eje. Cada sección transversal es un disco.',r'A(x)=\pi R^2')
    pieces = []
    total = sp.S.Zero
    for l,r in partition(a,b,d,e,d-e,d+e) if washers else [(a,b)]:
        mid = midpoint(l,r)
        p, q = d.subs(X,mid), e.subs(X,mid)
        outer, inner = (d,e) if abs(p)>=abs(q) else (e,d)
        if p*q <= 0:
            inner = sp.S.Zero
        area_at_x = sp.pi*sp.expand(outer**2-inner**2)
        term = integral_tex(area_at_x,l,r)
        formula = rf'R=\left|{latex(outer)}\right|,\quad r=\left|{latex(inner)}\right|,\quad {term}'
        step(ctx, 'Identificar las fronteras de la sección en este tramo.',formula, muestra=str(mid))
        pieces.append(term)
        if evaluate:
            total += exact_integral(area_at_x,l,r)
    formula = 'V=' + '+'.join(pieces)
    result = {'formula_latex':formula}
    if evaluate:
        result['volumen'] = str(sp.simplify(total))
        step(ctx, 'Integrar las áreas de las secciones en el intervalo.', formula+'='+latex(sp.simplify(total)))
    frames, curve = [], []
    for i in range(65):
        x = a+(b-a)*i/64
        y, z = f.subs(X,x), g.subs(X,x)
        outer, inner = radial_slice(y-axis,z-axis)
        curve.append([plot_number(value) for value in (x,y,z,axis)] if washers else
                     [plot_number(value) for value in (x,y,axis)])
        frames.append({'x':str(x), 'exterior':str(outer),'interior':str(inner),
                       'area':str(sp.pi*(outer**2-inner**2)),
                       'formula_latex':rf'A={latex(sp.pi*(outer**2-inner**2))}',
                       'radios':[plot_number(outer),plot_number(inner)],
                       'segmento':[plot_number(value) for value in (x,y,z)]})
    result['visual_integral'] = {'tipo':'seccion', 'curva':curve, 'cuadros':frames, 'inicial':32,
                                  'etiquetas':['f(x)','g(x)','Eje de giro'] if washers else ['f(x)','Eje de giro']}
    return result


def quadratic_arc_primitive(weight, slope):
    factor = sp.diff(slope,X)
    if factor == 0:
        return elementary(sp.expand(weight))*sp.sqrt(1+slope**2)
    u = sp.Symbol('u',real=True)
    root = sp.sqrt(1+u**2)
    bases = [(u*root+sp.asinh(u))/2, root**3/3,
             (u*root*(2*u**2+1)-sp.asinh(u))/8]
    polynomial_in_u = sp.Poly(weight.subs(X,(u-slope.subs(X,0))/factor),u)
    primitive = sum(c*bases[k] for (k,),c in polynomial_in_u.terms())/factor
    return primitive.subs(u,slope)


def arc_or_surface(data, ctx, *, surface=False):
    a, b, _ = interval(data)
    f = polynomial(data['expresion'],(X,))
    slope = sp.diff(f,X)
    arc = sp.sqrt(1+slope**2)
    step(ctx,'Derivar la curva para construir el elemento de arco.',
         rf"f'(x)={latex(slope)},\quad ds=\sqrt{{1+\left(f'(x)\right)^2}}\,dx={latex(arc)}\,dx")
    integrand, quantity = arc, 'L'
    if surface:
        axis = exact(data.get('eje') or '0')
        radius = sp.Abs(f-axis)
        integrand, quantity = 2*sp.pi*radius*arc, 'S'
        step(ctx,'Multiplicar la circunferencia de radio igual a la distancia al eje por el elemento de arco.',
             rf'y={latex(axis)},\quad R={latex(radius)},\quad 2\pi R={latex(2*sp.pi*radius)},\quad dS=2\pi R\,ds')
    formula = quantity + '=' + integral_tex(integrand,a,b)
    step(ctx,'Integrar sobre el intervalo de la curva.',formula)
    straight = not slope.has(X)
    if straight and not surface:
        delta = f.subs(X,b)-f.subs(X,a)
        distance = sp.sqrt((b-a)**2+delta**2)
        if sp.simplify(distance-(b-a)*arc) != 0:
            raise DomainError('La longitud y la distancia entre extremos deben coincidir para una recta.')
        step(ctx,'Para un segmento recto el integrando es constante y la longitud coincide con la distancia entre extremos.',
             r'(b-a)\sqrt{1+m^2}=\sqrt{(b-a)^2+(f(b)-f(a))^2}')
    result = {'formula_latex':formula,'unidades':'longitud al cuadrado' if surface else 'longitud'}
    if not wants_value(data):
        return result
    intervals = partition(a,b,f-axis) if surface else [(a,b)]
    exact_result = sp.degree(f,X) <= 2
    value = sp.S.Zero if exact_result else 0.0
    for l,r in intervals:
        weight = sp.S.One
        if surface:
            displacement = f-axis
            if displacement.subs(X,midpoint(l,r))<0:
                displacement = -displacement
            weight = 2*sp.pi*displacement
        if exact_result:
            value += evaluate_primitive(quadratic_arc_primitive(weight,slope),l,r)
        else:
            expression = FunctionNotation().doprint(weight*arc)
            value += integral_numerica(analizar(expression,variable=True),plot_number(l),plot_number(r))
    value = sp.simplify(value) if exact_result else float(value)
    relation = '=' if exact_result else r'\approx '
    rendered = latex(value) if exact_result else format(value,'.10g')
    result.update(valor=str(value), exactitud='exacta' if exact_result else 'aproximada')
    if straight and not surface:
        result['distancia_extremos'] = str(distance)
    step(ctx,'Evaluar la integral ' + ('exactamente.' if exact_result else 'con Simpson adaptativo.'),
         formula+relation+rendered)
    return result
