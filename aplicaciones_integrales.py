"""Planteamientos de integrales a partir de un modelo geométrico o físico."""
from fractions import Fraction
from math import isfinite

import sympy as sp

from calculo_i import X, exact, function, interval, require_interval
from integracion import integral_tex, latex, step
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
