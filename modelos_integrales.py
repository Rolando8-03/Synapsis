"""Modelos de densidad, momentos y trabajo para Cálculo II."""
import sympy as sp

from aplicaciones_integrales import exact_integral, partition, wants_value
from calculo_i import X, exact, interval, midpoint
from curso import polynomial
from integracion import elementary, integral_tex, latex, step
from motor_matematico.domain.models import DomainError


def rod(data, ctx, *, center=False):
    a, b, _ = interval(data)
    left, right = (exact(data[key]) for key in ('densidad_izquierda','densidad_derecha'))
    if min(left,right)<0:
        raise DomainError('Las densidades en los dos extremos deben ser no negativas.')
    density = left+(right-left)*(X-a)/(b-a)
    step(ctx,'Interpolar la densidad lineal desde los dos extremos de la barra.',
         r'\rho(x)=\rho(a)+[\rho(b)-\rho(a)]\frac{x-a}{b-a}='+latex(density),
         densidad_izquierda=str(left),densidad_derecha=str(right))
    mass = exact_integral(density,a,b)
    formula = 'm=' + integral_tex(density,a,b)
    step(ctx,'Una rebanada de longitud dx tiene masa dm = ρ(x) dx.',
         r'dm=\rho(x)\,dx,\quad '+formula+'='+latex(mass))
    result = {'formula_latex':formula,'masa':str(mass),'densidad_lineal':str(density)}
    if not center:
        return result
    origin = exact(data.get('origen') or '0')
    lever = X-origin
    moment = exact_integral(lever*density,a,b)
    step(ctx,'Multiplicar dm por el brazo de palanca con signo, medido desde el origen elegido.',
         rf'x_0={latex(origin)},\quad M_{{x_0}}='+integral_tex(lever*density,a,b)+'='+latex(moment))
    result.update(momento=str(moment),origen=str(origin),centro_de_masa=None)
    if mass == 0:
        step(ctx,'La masa es cero. El centro de masa queda indefinido.')
        return result
    center_position = origin+moment/mass
    step(ctx,'Dividir el momento por la masa y sumar el origen para ubicar el centro en la coordenada x.',
         rf'\bar x=x_0+\frac{{M_{{x_0}}}}{{m}}={latex(center_position)}')
    result['centro_de_masa'] = str(center_position)
    return result


def centroid(data, ctx):
    a, b, _ = interval(data)
    f, g = (polynomial(data[key],(X,)) for key in ('expresion','segunda'))
    if f == g:
        raise DomainError('El centroide requiere una región de área positiva.')
    area, mx, my = sp.S.Zero, sp.S.Zero, sp.S.Zero
    for l,r in partition(a,b,f-g):
        upper, lower = (f,g) if (f-g).subs(X,midpoint(l,r))>0 else (g,f)
        height = upper-lower
        area += exact_integral(height,l,r)
        my += exact_integral(X*height,l,r)
        mx += exact_integral((upper**2-lower**2)/2,l,r)
        step(ctx,'Ordenar las fronteras y formar el área y los momentos respecto a sus ejes.',
             rf'A_{{tramo}}={integral_tex(height,l,r)},\quad M_{{y,tramo}}={integral_tex(X*height,l,r)},'
             rf'\quad M_{{x,tramo}}={integral_tex((upper**2-lower**2)/2,l,r)}')
    if area <= 0:
        raise DomainError('El centroide requiere una región de área positiva.')
    center = [sp.simplify(my/area),sp.simplify(mx/area)]
    formula = rf'(\bar x,\bar y)=\left(\frac{{M_y}}{{A}},\frac{{M_x}}{{A}}\right)=\left({latex(center[0])},{latex(center[1])}\right)'
    step(ctx,'Sumar área y momentos de los tramos y dividir usando la convención de ejes.', formula,
         area=str(area),momento_x=str(mx),momento_y=str(my))
    middle = (a+b)/2
    mirrored = {sp.expand(curve.subs(X,2*middle-X)) for curve in (f,g)}
    if mirrored == {sp.expand(f),sp.expand(g)}:
        if sp.simplify(center[0]-middle) != 0:
            raise DomainError('La abscisa del centroide debe estar sobre el eje de simetría.')
        step(ctx,'Reflejar las fronteras en el eje vertical de simetría y comprobar la abscisa del centroide.',
             rf'\bar x=(a+b)/2={latex(middle)}')
    return {'formula_latex':formula,'area':str(area),'momento_x':str(mx),'momento_y':str(my),
            'centroide':[str(point) for point in center]}


def spring(data, ctx):
    k, a, b = (exact(data[key]) for key in ('constante','inferior','superior'))
    if k <= 0:
        raise DomainError('La constante elástica debe ser positiva.')
    force = k*X
    formula = 'W=' + integral_tex(force,a,b)
    step(ctx,'Medir la elongación desde la longitud natural x = 0. La fuerza aplicada en equilibrio es F(x) = kx.',
         rf'F(x)={latex(force)}')
    step(ctx,'Integrar la fuerza aplicada entre las elongaciones inicial y final, en ese orden.',formula)
    result = {'formula_latex':formula,'unidades':'fuerza por longitud'}
    if wants_value(data):
        work = exact_integral(force,a,b)
        result['trabajo'] = str(work)
        step(ctx,'Evaluar la integral de la fuerza aplicada.',formula+'='+latex(work))
    return result


def pumping(data, ctx):
    H, R = (exact(data[key]) for key in ('altura','radio'))
    h = exact(data['relleno']) if str(data.get('relleno','')).strip() else H
    outlet = exact(data['salida']) if str(data.get('salida','')).strip() else H
    weight = exact(data['peso_especifico']) if str(data.get('peso_especifico','')).strip() else sp.Symbol('gamma',positive=True)
    if H <= 0 or R <= 0 or not 0 <= h <= H or outlet < h or weight <= 0:
        raise DomainError('Usá altura, radio y peso específico positivos. La altura del líquido debe estar dentro del tanque y la salida a esa altura o por encima.')
    y = sp.Symbol('y', real=True)
    radius = R*y/H
    section = sp.pi*radius**2
    lift = outlet-y
    density = weight*section*lift
    formula = 'W=' + integral_tex(density,sp.S.Zero,h,y)
    step(ctx,'Medir y desde el vértice inferior. Obtener el radio por semejanza de triángulos.',
         rf'r(y)=\frac{{R}}{{H}}y={latex(radius)}')
    step(ctx,'Multiplicar el área de la rebanada por su espesor y por el peso específico.',
         rf'dV={latex(section)}\,dy,\quad dP={latex(weight*section)}\,dy')
    step(ctx,'Elevar la rebanada desde y hasta el nivel de salida y sumar el trabajo.',
         rf'd(y)={latex(lift)},\quad {formula}', relleno=str(h),salida=str(outlet))
    result = {'formula_latex':formula,'unidades':'fuerza por longitud','peso_especifico':str(weight)}
    if wants_value(data):
        primitive = elementary(sp.expand(density),y)
        value = sp.simplify(primitive.subs(y,h)-primitive.subs(y,0))
        result['trabajo'] = str(value)
        step(ctx,'Evaluar el trabajo en la altura ocupada por el líquido.',formula+'='+latex(value))
    return result
