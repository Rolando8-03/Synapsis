"""Exploración de raíces, interpolación y aproximación numérica."""
from decimal import Decimal, localcontext
from fractions import Fraction as F

import sympy as sp

from .algebra import real_display, step
from .geometria import points_from
from motor_matematico.parsing.polynomials import polynomial
from motor_matematico.algorithms.linear.context import freeze, integer
from motor_matematico.algorithms.linear.reduction import solve
from motor_matematico.algorithms.numerical.functions import Function, decimal
from motor_matematico.algorithms.numerical.integration import weighted_mesh
from motor_matematico.domain.models import DomainError, ResourceLimitError
from motor_matematico.parsing.numbers import parse_number

X, Y = sp.symbols("x y", real=True)


def endpoints(data):
    a,b = (parse_number(data[name]) for name in ("inferior","superior"))
    if not a<b or max(abs(a),abs(b))>10**6:
        raise ValueError("Ingresá un intervalo creciente dentro de ±1 000 000.")
    return a,b


def symbolic_samples(expr, left, right, count=150):
    result = []
    for i in range(count+1):
        x = left+(right-left)*i/count
        result.append([real_display(x),real_display(expr.subs(X,x))])
    return result


def candidates(data,ctx):
    f = Function(data["expresion"],ctx)
    a,b = endpoints(data)
    n = integer(data["n"],"Subintervalos",2,120)
    grid = [a+(b-a)*i/n for i in range(n+1)]
    def safe(x):
        try:
            return f.exact(x)
        except (DomainError,ValueError,ArithmeticError):
            return None
    values = [safe(x) for x in grid]
    intervals, blocked, lines = [],[],[]
    for i,(left,right) in enumerate(zip(grid,grid[1:])):
        fl,fr = values[i:i+2]
        entry = [left,right]
        try:
            f.continuous(left,right)
        except (DomainError,ValueError,ArithmeticError):
            blocked.append(entry)
            status = "Dominio no verificable"
        else:
            if fl is not None and fr is not None and fl*fr<0:
                intervals.append(entry)
                status = "Cambio de signo en intervalo continuo"
            else:
                status = "Sin cambio de signo detectado"
            if fl is not None and fr is not None:
                lines.append({"puntos":[[real_display(left),real_display(fl)],[real_display(right),real_display(fr)]],
                              "color":1 if fl*fr<0 else 0})
        step(ctx,"intervalo",status,r"f(a)f(b)<0\quad\text{si hay signos opuestos}",desde=left,hasta=right,fa=fl,fb=fr)
    roots = [x for x,fx in zip(grid,values) if fx is not None and fx==0]
    out = {"intervalos_candidatos":intervals,"intervalos_con_dominio_no_verificado":blocked,
            "ceros_en_muestras":roots,"advertencia":"Una raíz de multiplicidad par puede quedar entre muestras sin producir cambio de signo."}
    if lines:
        out["visual_libro"] = {"tipo":"intervalos","tramos":lines,
                              "lineas":[segment["puntos"] for segment in lines],
                              "leyenda":["Los intervalos con cambio de signo se resaltan","Los huecos señalan dominio sin verificar"],
                              "enlace":["#raices/raices.biseccion","Continuar con Bisección"]}
    return out


def polynomial_bound(coefficients, radius):
    return sum((abs(v)*radius**k for (k,),v in coefficients.terms()),sp.S.Zero)


def certify(g, a, b, ctx):
    if g.polynomial is None:
        return None
    middle, radius = sp.Rational((a+b)/2), sp.Rational((b-a)/2)
    p = sum(sp.Rational(c)*(X+middle)**k for k,c in g.polynomial.items())
    slope = polynomial_bound(sp.Poly(sp.diff(p,X),X),radius)
    excursion = polynomial_bound(sp.Poly(p-middle,X),radius)
    good = slope<1 and excursion<=radius
    step(ctx,"contraccion","Acotar la derivada y toda la imagen mediante coeficientes en el centro.",
         r"\max|g'|\le q<1,\quad g([a,b])\subseteq[a,b]", q=str(slope),
         radio=str(radius), cota_imagen=str(excursion), hipotesis_cumplidas=bool(good))
    return F(slope) if good else None


def fixed_point(data,ctx):
    f = Function(data["expresion"],ctx)
    a,b = endpoints(data)
    x0 = parse_number(data["inicial"])
    tol = parse_number(data["tolerancia"])
    n = integer(data["n"],"Iteraciones",1,60)
    if not a<=x0<=b or not F(1,10**20)<=tol<=1:
        raise ValueError("Ubicá la semilla dentro del intervalo y elegí una tolerancia entre 1e-20 y 1.")
    results, curves = {},[]
    for label, field in (("Despeje 1","g1"),("Despeje 2","g2")):
        g = Function(data[field],ctx)
        q = certify(g,a,b,ctx)
        certified = q is not None
        current = x0
        rows = []
        vertices = [[real_display(current), real_display(current)]]
        reason = "Límite de iteraciones"
        for k in range(1,n+1):
            try:
                following = g.exact(current) if certified else F(g.value(decimal(current)))
                if certified and max(following.numerator.bit_length(),following.denominator.bit_length())>500:
                    certified = False
                    following = F(g.value(decimal(current)))
            except (DomainError,ValueError,ArithmeticError):
                reason = "El despeje no está definido en el último punto"
                break
            if not a<=following<=b:
                reason = "El siguiente valor sale del intervalo"
                break
            try:
                residual = abs(f.exact(following))
            except (DomainError,ValueError,ArithmeticError):
                reason = "La ecuación original no está definida en el siguiente punto"
                break
            diff = abs(following-current)
            bound = freeze(q*diff/(1-q)) if certified else None
            row = {"iteracion":k,"anterior":current,"siguiente":following,"cambio":diff,"residuo_original":residual,
                   "cota_al_punto_fijo":bound}
            rows.append(row)
            vertices.extend([[real_display(current),real_display(following)],[real_display(following)]*2])
            step(ctx,"punto_fijo",f"{label}: evaluar g y comprobar el residuo de f.",
                 r"x_{k+1}=g(x_k),\qquad |f(x_{k+1})|", **row)
            current = following
            if diff<=tol and residual<=tol:
                reason = "Cambio y residuo dentro de la tolerancia"
                break
            if diff<=tol:
                reason = "El cambio es pequeño. El residuo todavía supera la tolerancia"
                break
        step(ctx,"parada",f"{label}: {reason}.")
        results[field] = {"motivo":reason,"iteraciones":rows,"ultimo_x":current,
                          "q_en_la_cota":q,"cota_activa_en_el_ultimo_paso":certified and bool(rows)}
        curves.append(vertices)
    return {"exactitud":"aproximada",**results,
            "visual_libro":{"tipo":"rectas","lineas":[[[real_display(a)]*2,[real_display(b)]*2],*curves],
                             "leyenda":["y=x","Despeje 1","Despeje 2"]}}


def power(data,ctx):
    from .algebra import small,show
    from motor_matematico.algorithms.linear.context import vector
    A = small(data,square=True)
    seed = vector(data["b"],A.rows)
    if not any(seed):
        raise ValueError("Elegí una semilla distinta de cero.")
    count = integer(data["n"],"Iteraciones",1,120)
    tol = parse_number(data["tolerancia"])
    if not F(1,10**20)<=tol<=1:
        raise ValueError("La tolerancia debe estar entre 1e-20 y 1.")
    with localcontext() as arithmetic:
        arithmetic.prec = 35
        decimals = [[Decimal(int(v.p))/Decimal(int(v.q)) for v in row] for row in A.tolist()]
        v = list(map(decimal,seed))
        norm = max(map(abs,v))
        v = [x/norm for x in v]
        rows = []
        step(ctx,"semilla","Normalizar la semilla por la norma infinito. Para hallar el dominante, la semilla debe excitar su componente.",
             vector=v, matriz=show(A))
        for k in range(1,count+1):
            product = [sum(a*x for a,x in zip(row,v)) for row in decimals]
            scale = max(map(abs,product))
            quotient = sum(x*y for x,y in zip(v,product))/sum(x*x for x in v)
            residual = max(abs(y-quotient*x) for x,y in zip(v,product))
            rows.append([k,quotient,residual])
            step(ctx,"potencia","Multiplicar, estimar con el cociente de Rayleigh y medir el residuo.",
                 r"\lambda=\frac{v^TAv}{v^Tv},\quad\|Av-\lambda v\|_\infty", vector=v,
                 producto=product, lambda_aprox=quotient,residuo=residual)
            if residual<=decimal(tol):
                reason = "Residuo dentro de la tolerancia"
                break
            if scale==0:
                reason = "El producto se anuló"
                break
            if k<count:
                v = [x/scale for x in product]
        else:
            reason = "Límite de iteraciones"
    return {"exactitud":"aproximada","valor_propio":quotient,"vector_propio":v,"residuo":residual,
            "advertencia":"Un residuo pequeño identifica un par propio aproximado. La dominancia depende del espectro y de la semilla.",
            "motivo":reason,"tabla":rows,"encabezados":["k","Cociente de Rayleigh","Residuo"]}


def differences(points,ctx):
    x,y = zip(*points)
    columns = [list(y)]
    for order in range(1,len(x)):
        previous = columns[-1]
        column = [(previous[i+1]-previous[i])/(x[i+order]-x[i]) for i in range(len(previous)-1)]
        columns.append(column)
        step(ctx,"diferencias",f"Construir la columna de orden {order} con los cocientes.",
             r"f[x_i,\ldots,x_j]=\frac{f[x_{i+1},\ldots,x_j]-f[x_i,\ldots,x_{j-1}]}{x_j-x_i}",
             diferencias=column, denominadores=[x[i+order]-x[i] for i in range(len(column))])
    p = sum(sp.Rational(col[0])*sp.prod(X-node for node in x[:i]) for i,col in enumerate(columns))
    return p, columns


def interpolation(data,ctx,*,method):
    points = points_from(data)
    p, columns = differences(points,ctx)
    x,y = zip(*points)
    result = {}
    if method=="lagrange":
        bases = [sp.prod((X-other)/(node-other) for j,other in enumerate(x) if i!=j)
                 for i,node in enumerate(x)]
        for i,basis in enumerate(bases):
            step(ctx,"lagrange",f"Construir la base cardinal L{i}.",sp.latex(basis))
        alternative = sum(value*basis for value,basis in zip(y,bases))
        result["coincide_con_newton"] = sp.expand(p-alternative)==0
        p = alternative
    else:
        result["encabezados"] = ["x",*[f"Orden {i}" for i in range(len(columns))]]
        result["tabla"] = [[z,*[col[j] if j<len(col) else None for col in columns]] for j,z in enumerate(x)]
    checks = [p.subs(X,z)==v for z,v in points]
    step(ctx,"nodos","Verificar el interpolante en cada uno de los nodos.",comprobaciones=checks)
    poly = sp.expand(p)
    return {**result,"polinomio":str(poly),"formula_latex":"P(x)="+sp.latex(poly),"verificacion":all(checks),
            "series":{"points":symbolic_samples(poly,min(x),max(x)),"markers":[list(map(real_display,p)) for p in points]}}


def spline(data,ctx):
    points = sorted(points_from(data))
    xs,ys = zip(*points)
    h = [right-left for left,right in zip(xs,xs[1:])]
    n = len(xs)
    A = [[F(0)]*n for _ in xs]
    b = [F(0)]*n
    A[0][0] = A[-1][-1] = F(1)
    for i in range(1,n-1):
        A[i][i-1:i+2] = h[i-1],2*(h[i-1]+h[i]),h[i]
        b[i] = 6*((ys[i+1]-ys[i])/h[i]-(ys[i]-ys[i-1])/h[i-1])
    step(ctx,"tridiagonal","Imponer segunda derivada cero en los extremos y continuidad de la primera en los nodos.",
         r"M_0=M_n=0", sistema=A, independiente=b)
    M = solve(A,b,ctx)["particular"]
    pieces = []
    for i,(a,c,w) in enumerate(zip(xs,xs[1:],h)):
        u,v = (c-X)/w,(X-a)/w
        p = sp.expand(w*w*(M[i]*u**3+M[i+1]*v**3)/6+(ys[i]-M[i]*w*w/6)*u+(ys[i+1]-M[i+1]*w*w/6)*v)
        pieces.append(p)
        step(ctx,"tramo","Construir el tramo a partir de las segundas derivadas.",sp.latex(p), intervalo=[a,c])
    checks = {
        "nodos":all(p.subs(X,xs[i])==ys[i] and p.subs(X,xs[i+1])==ys[i+1] for i,p in enumerate(pieces)),
        "C1_y_C2":all(sp.diff(pieces[i-1]-pieces[i],X,k).subs(X,xs[i])==0 for i in range(1,n-1) for k in (1,2)),
        "natural":sp.diff(pieces[0],X,2).subs(X,xs[0])==0 and sp.diff(pieces[-1],X,2).subs(X,xs[-1])==0,
    }
    step(ctx,"verificacion","Comprobar nodos, continuidad y condiciones naturales.",**checks)
    return {"tramos":[{"desde":a,"hasta":b,"polinomio":str(p)} for a,b,p in zip(xs,xs[1:],pieces)],"verificacion":checks,
            "series":{"points":[pt for a,b,p in zip(xs,xs[1:],pieces) for pt in symbolic_samples(p,a,b,20)],
                      "markers":[list(map(real_display,p)) for p in points]}}


def composite(f, a, b, n, ctx, *, simpson=False):
    h, factors, values, result = weighted_mesh(f, a, b, n, simpson=simpson)
    result = freeze(result)
    name = "Simpson 1/3" if simpson else "Trapecios"
    step(ctx,"cuadratura",f"{name}: multiplicar cada muestra por su peso y sumar.",
         r"Q=\frac{h}{"+("3" if simpson else "2")+r"}\sum_i w_i f(x_i)", h=h, pesos=factors, muestras=values, valor=result)
    return result


def derivative_bound(f, a, b, order):
    from math import prod
    return sum(abs(c)*prod(range(k-order+1,k+1))*max(abs(a),abs(b))**(k-order)
               for k,c in f.polynomial.items() if k>=order)


def quadrature(data,ctx,*,romberg=False):
    f = Function(data["expresion"],ctx)
    a,b = endpoints(data)
    f.continuous(a,b)
    if romberg:
        levels = integer(data["n"],"Niveles de Romberg",1,8)
        rows = []
        for i in range(levels):
            line = [composite(f,a,b,2**i,ctx)]
            for j in range(1,i+1):
                refined = line[-1]+(line[-1]-rows[-1][j-1])/(4**j-1)
                line.append(freeze(refined))
                step(ctx,"romberg","Extrapolar usando las dos mallas consecutivas.",
                     r"R_{i,j}=R_{i,j-1}+\frac{R_{i,j-1}-R_{i-1,j-1}}{4^j-1}", fila=i,columna=j,valor=refined)
            rows.append(line)
        return {"exactitud":"aproximada","valor":rows[-1][-1],
                "estimacion_no_garantizada":abs(rows[-1][-1]-rows[-2][-1]) if levels>1 else None,
                "tabla":[row+[None]*(levels-len(row)) for row in rows],
                "encabezados":[f"Orden {i}" for i in range(levels)]}
    n = integer(data["n"],"Subintervalos",2,128)
    if n%2:
        raise ValueError("Simpson 1/3 requiere un número par de subintervalos.")
    out = {"exactitud":"aproximada","subintervalos":n}
    for name, simpson, order, denominator in (("trapecios",False,2,12),("simpson_13",True,4,180)):
        next_n = 2*n if simpson else n
        coarse = composite(f,a,b,n if simpson else n//2,ctx,simpson=simpson)
        refined = composite(f,a,b,next_n,ctx,simpson=simpson)
        # La cota clásica supone una derivada acotada. Para otros casos se muestra solo la estimación.
        bound = None if f.polynomial is None else (b-a)**(order+1)*derivative_bound(f,a,b,order)/(denominator*next_n**order)
        out[name] = {"valor_en_malla_n":coarse if simpson else refined,
                     "cota_garantizada_en_malla_n":None if bound is None else bound*(next_n//n)**order,
                     "estimacion_por_refinamiento":abs(refined-coarse)/(2**order-1),
                     "subintervalos_de_la_estimacion":next_n}
    step(ctx,"error","Separar la estimación por refinamiento de las cotas demostradas para polinomios.")
    return out


def finite_difference(data,ctx,*,method):
    f = Function(data["expresion"],ctx)
    x,h = parse_number(data["x"]),parse_number(data["h"])
    if not F(1,10**18)<=h<=1000 or abs(x)>10**6:
        raise ValueError("Usá un paso positivo entre 1e-18 y 1000, con |x| ≤ 1 000 000.")
    formulas = {"adelante":r"\frac{f(x+h)-f(x)}h","atras":r"\frac{f(x)-f(x-h)}h","centrada":r"\frac{f(x+h)-f(x-h)}{2h}"}
    k = "centrada" if method=="richardson" else method
    def evaluate(step_size,rounded=False):
        a = x-step_size if k!="adelante" else x
        b = x+step_size if k!="atras" else x
        f.continuous(a,b)
        left,right = f.exact(a),f.exact(b)
        if rounded:
            with localcontext() as arithmetic:
                arithmetic.prec=integer(data["cifras"],"Cifras significativas",3,15)
                return F((decimal(right)-decimal(left))/decimal(b-a))
        value = (right-left)/(b-a)
        step(ctx,"diferencia","Evaluar ambos puntos, restar y dividir por su distancia.",formulas[k],
             izquierda=a,derecha=b,f_izquierda=left,f_derecha=right,valor=value)
        return value
    first, half = evaluate(h), evaluate(h/2)
    rounded, half_rounded = evaluate(h,True), evaluate(h/2,True)
    result, simulated = (half+(half-first)/3, half_rounded+(half_rounded-rounded)/3) if method=="richardson" else (first,rounded)
    if method=="richardson":
        step(ctx,"extrapolacion","Cancelar el término principal de orden dos.",
             r"D_R=D(h/2)+\frac{D(h/2)-D(h)}3", valor=result)
    reference = None
    if f.polynomial is not None:
        reference = sum(k*c*x**(k-1) for k,c in f.polynomial.items() if k)
    step(ctx,"errores","Comparar el cálculo con la referencia exacta si está disponible y contrastar con el redondeo simulado.",
         referencia=reference,cambio=abs(first-half),diferencia_redondeo=abs(result-simulated))
    return {"exactitud":"aproximada","valor":result,"referencia_exacta":reference,
            "error_truncamiento":None if reference is None else abs(result-reference),
            "cambio_al_reducir_h":abs(first-half),"efecto_redondeo_simulado":abs(result-simulated),
            "control_libro":{"campo":"h","etiqueta":"Paso h","valor":str(h)}}


def ode(data,ctx,*,method):
    expression = polynomial(data["expresion"],(X,Y))
    x,y,h = (parse_number(data[k]) for k in ("x","y","h"))
    n = integer(data["n"],"Pasos",1,60)
    if h==0 or max(abs(x),abs(y),abs(h))>10**6:
        raise ValueError("Usá un paso distinto de cero y magnitudes iniciales dentro de ±1 000 000.")
    reference = polynomial(data["referencia"],(X,)) if data.get("referencia") else None
    if reference is not None and (sp.expand(sp.diff(reference,X)-expression.subs(Y,reference))!=0 or reference.subs(X,x)!=y):
        raise ValueError("La solución de referencia debe satisfacer la EDO y la condición inicial.")
    initial = x
    row = [0,x,y, F(0) if reference is not None else None]
    rows = [row]
    coeffs = [(i,j,F(coefficient)) for (i,j),coefficient in sp.Poly(expression,X,Y).terms()]
    with localcontext() as arithmetic:
        arithmetic.prec = 35
        y = decimal(y)
        def slope(at,value):
            if abs(value)>Decimal("1e30"):
                raise ResourceLimitError("La trayectoria excede la escala de cálculo de esta EDO.")
            return sum((decimal(c)*(decimal(at)**i if i else 1)*(value**j if j else 1) for i,j,c in coeffs),Decimal(0))
        for i in range(1,n+1):
            x = initial+(i-1)*h
            H = decimal(h)
            slopes = [slope(x,y)]
            if method=="heun":
                slopes.append(slope(x+h,y+H*slopes[0]))
                change = H*sum(slopes)/2
            elif method=="rk4":
                slopes.append(slope(x+h/2,y+H*slopes[0]/2))
                slopes.append(slope(x+h/2,y+H*slopes[1]/2))
                slopes.append(slope(x+h,y+H*slopes[2]))
                change = H*(slopes[0]+2*slopes[1]+2*slopes[2]+slopes[3])/6
            else:
                change = H*slopes[0]
            y += change
            if abs(y)>Decimal("1e30"):
                raise ResourceLimitError("La trayectoria excede la escala de cálculo de esta EDO.")
            error = abs(F(y)-F(reference.subs(X,x+h))) if reference is not None else None
            rows.append([i,x+h,y,error])
            step(ctx,"edo",f"Paso {i}: evaluar pendientes y actualizar la ordenada.",
                 r"y_{i+1}=y_i+\Delta y", x=x,pendientes=slopes, incremento=change, siguiente=y,error=error)
    plot = [[real_display(xi),real_display(yi)] for _,xi,yi,_ in rows]
    names = ["Solución numérica"]
    if reference is not None:
        for point, (_,xi,_,_) in zip(plot,rows):
            point.append(real_display(reference.subs(X,xi)))
        names.append("Referencia verificada")
    return {"exactitud":"aproximada","valor_final":y,"tabla":rows,
            "encabezados":["k","x","y","Error absoluto"],"series":{"points":plot,"names":names}}
