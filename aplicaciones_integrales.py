"""Planteamientos de integrales a partir de un modelo geométrico o físico."""
from fractions import Fraction
from math import isfinite

import sympy as sp

from calculo_i import X, exact, function, interval, require_interval
from integracion import elementary, integral_tex, latex, step
from motor_matematico.algorithms.calculo import analizar, evaluar
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
