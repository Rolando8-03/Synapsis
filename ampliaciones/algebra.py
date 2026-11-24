"""Ortogonalidad, espectro y aproximaciones matriciales."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import isfinite

import sympy as sp

from motor_matematico.algorithms.linear.context import integer, matrix, vector
from motor_matematico.algorithms.linear.reduction import kernel, solve
from motor_matematico.parsing.numbers import parse_number


def show(value):
    if isinstance(value, sp.MatrixBase):
        return [[str(entry) for entry in row] for row in value.tolist()]
    return str(value)


def real_display(value):
    number = float(value)
    if not isfinite(number) or abs(number) > 1e100:
        raise ValueError("La magnitud supera la escala de visualización.")
    return number


def small(data, key="A", *, square=False, limit=6):
    rows = matrix(data[key], square=square)
    if max(len(rows), len(rows[0])) > limit:
        raise ValueError(f"Esta operación admite hasta {limit} filas y columnas.")
    return sp.Matrix(rows)


def rational_rows(A):
    return [[F(int(v.p), int(v.q)) for v in row] for row in A.tolist()]


def step(ctx, kind, message, formula="", **data):
    ctx.emit(kind, message, data, formula)


def orthogonalize(A, ctx):
    """Gram-Schmidt exacto: los vectores ortogonales permanecen racionales."""
    orthogonal = []
    for j in range(A.cols):
        column = A[:, j]
        residual = column.copy()
        for i, basis in enumerate(orthogonal):
            weight = basis.dot(column) / basis.dot(basis)
            residual -= weight * basis
            step(ctx, "proyeccion", f"En la columna {j+1}, restar la proyección sobre u{i+1}.",
                 rf"c_{{{i+1},{j+1}}}=\frac{{u_{{{i+1}}}^Ta_{{{j+1}}}}}{{u_{{{i+1}}}^Tu_{{{i+1}}}}}={sp.latex(weight)}",
                 proyeccion=show(weight*basis), resto=show(residual))
        if residual.is_zero_matrix:
            step(ctx, "dependencia", f"La columna {j+1} deja resto cero. No se puede normalizar.", columna=j+1)
            continue
        norm = sp.sqrt(residual.dot(residual))
        orthogonal.append(residual)
        step(ctx, "normalizacion", "Dividir el resto por su norma.",
             rf"q_{{{len(orthogonal)}}}=\frac{{u_{{{len(orthogonal)}}}}}{{{sp.latex(norm)}}}",
             ortogonal=show(residual), unitario=show(residual/norm))
    return orthogonal


def qr(A, ctx):
    orthogonal = orthogonalize(A, ctx)
    Q = sp.Matrix.hstack(*(u/sp.sqrt(u.dot(u)) for u in orthogonal)) if orthogonal else sp.zeros(A.rows, 0)
    R = sp.simplify(Q.T*A)
    return orthogonal, Q, R


def gram_schmidt(data, ctx):
    A = small(data)
    basis, Q, R = qr(A, ctx)
    return {"base_ortogonal": [show(u) for u in basis], "Q": show(Q), "rango": Q.cols,
            "columnas_dependientes": Q.cols < A.cols, "ortogonalidad": Q.T*Q == sp.eye(Q.cols)}


def rounded_qr(A, digits, modified, ctx):
    def rounded(value):
        return +value
    with localcontext() as arithmetic:
        arithmetic.prec = digits
        columns = [[Decimal(int(value.p))/Decimal(int(value.q)) for value in A[:, j]] for j in range(A.cols)]
        unit = []
        for j, source in enumerate(columns, 1):
            current = source[:]
            for q in unit:
                target = current if modified else source
                factor = sum((a*b for a,b in zip(q,target)), Decimal(0))
                current = [rounded(u-factor*v) for u,v in zip(current,q)]
            norm = sum((u*u for u in current), Decimal(0)).sqrt()
            step(ctx, "qr_redondeo", f"Columna {j}: resto y norma con precisión simulada.",
                 modo="modificado" if modified else "clasico", resto=current, norma=norm)
            if norm == 0:
                return {"columnas_normalizadas": len(unit), "error_ortogonalidad": None,
                        "diagnostico": "El redondeo produjo un resto nulo."}
            unit.append([u/norm for u in current])
    with localcontext() as arithmetic:
        arithmetic.prec = max(30, 2*digits)
        error = max(abs(sum((u*v for u,v in zip(q,r)), Decimal(0))-(i==j))
                    for i,q in enumerate(unit) for j,r in enumerate(unit))
    return {"columnas_normalizadas": len(unit), "error_ortogonalidad": error}


def qr_operation(data, ctx):
    A = small(data)
    _, Q, R = qr(A, ctx)
    reconstructs = sp.simplify(Q*R-A).is_zero_matrix
    ortho = sp.simplify(Q.T*Q-sp.eye(Q.cols)).is_zero_matrix
    step(ctx, "verificacion", "Comprobar ortonormalidad y reconstrucción.",
         r"Q^TQ=I,\qquad QR=A", ortonormal=ortho, reconstruccion=reconstructs)
    out = {"Q":show(Q), "R":show(R), "rango":Q.cols, "ortonormal":ortho, "reconstruccion":reconstructs}
    if data.get("comparar"):
        digits = integer(data["cifras"], "Cifras significativas", 3, 14)
        out["comparacion_simulada"] = {name: rounded_qr(A, digits, modified, ctx)
                                      for name,modified in (("clasico",False),("modificado",True))}
    return out


def project(data, ctx):
    A = small(data)
    b = sp.Matrix(vector(data["b"], A.rows))
    basis = orthogonalize(A, ctx)
    projection = sp.zeros(A.rows, 1)
    for u in basis:
        coefficient = u.dot(b)/u.dot(u)
        projection += coefficient*u
        step(ctx, "componente", "Sumar la proyección sobre el siguiente vector de la base.",
             rf"\frac{{u^Tb}}{{u^Tu}}={sp.latex(coefficient)}", acumulado=show(projection))
    residual = b-projection
    products = [u.dot(residual) for u in basis]
    step(ctx, "residuo", "Restar la proyección y comprobar cada producto con la base.",
         r"r=b-p,\quad u_i^Tr=0", residuo=show(residual), productos=list(map(str,products)))
    return {"proyeccion":show(projection), "residuo":show(residual), "productos_con_la_base":list(map(str,products)),
            "ortogonal":all(value==0 for value in products)}


def least_squares(A, b, ctx):
    _, Q, R = qr(A, ctx)
    if Q.cols == A.cols:
        right = sp.simplify(Q.T*b)
        coeffs = sp.zeros(A.cols,1)
        for i in reversed(range(A.cols)):
            coeffs[i] = sp.simplify((right[i]-sum(R[i,j]*coeffs[j] for j in range(i+1,A.cols)))/R[i,i])
            step(ctx, "sustitucion", "Resolver el sistema triangular de QR desde la última fila.",
                 rf"x_{{{i+1}}}={sp.latex(coeffs[i])}")
        method, directions = "QR reducida", []
    else:
        normal, right = A.T*A, A.T*b
        step(ctx, "normales", "Con columnas dependientes, resolver las ecuaciones normales exactas.",
             r"(A^TA)x=A^Tb", matriz=show(normal), independiente=show(right))
        family = solve(rational_rows(normal), [F(int(v.p),int(v.q)) for v in right], ctx)
        coeffs = sp.Matrix(family["particular"])
        directions = [list(map(str,u)) for u in family["direcciones"]]
        method = "Ecuaciones normales"
    residual = b-A*coeffs
    products = A.T*residual
    step(ctx, "verificacion", "Comprobar la ortogonalidad del residuo a cada columna.",
         r"A^Tr=0", productos=show(products))
    return coeffs, residual, directions, method


def fit(data, ctx):
    A = small(data)
    b = sp.Matrix(vector(data["b"], A.rows))
    c, r, directions, method = least_squares(A,b,ctx)
    return {"coeficientes":show(c), "residuo":show(r), "normal":show(A.T*r),
            "unica":not directions, "direcciones":directions, "metodo":method}


def spectrum(A, ctx):
    characteristic = A.charpoly()
    symbol = characteristic.gen
    poly = characteristic.as_expr()
    step(ctx, "caracteristico", "Construir y expandir el determinante de λI−A.",
         r"\det\left("+sp.latex(symbol*sp.eye(A.rows)-A)+r"\right)="+sp.latex(poly))
    _, factors = sp.factor_list(poly)
    step(ctx, "factores", "Factorizar y leer la multiplicidad de cada factor.",
         sp.latex(sp.factor(poly)), factores=[[str(p),m] for p,m in factors])
    return sp.roots(poly, symbol), poly


def field_selection(data):
    choice = data.get("cuerpo", "real")
    if choice not in ("real","complejo"):
        raise ValueError("Elegí el cuerpo real o complejo.")
    return choice


def eigenvalues(data, ctx):
    A = small(data, square=True, limit=3)
    choice = field_selection(data)
    values, poly = spectrum(A, ctx)
    selected = [dict(valor=str(value), multiplicidad=mult)
                for value,mult in values.items() if choice=="complejo" or value.is_real]
    step(ctx,"espectro","Resolver el polinomio y conservar los valores del cuerpo elegido.",
         cuerpo=choice, valores=selected)
    return {"cuerpo":choice, "polinomio_caracteristico":str(poly), "valores_propios":selected}


def eigenspace(data, ctx):
    A = small(data, square=True, limit=3)
    from motor_matematico.algorithms.calculo_docente.calculo_i import X, function
    def component(key):
        raw = data.get(key) or "0"
        expr, domain = function(raw,ctx)[:2]
        if expr.has(X) or expr.is_real is not True or expr.is_algebraic is not True or domain.is_empty:
            raise ValueError("Ingresá una constante algebraica real en cada componente de λ.")
        return sp.simplify(expr)
    value = component("lambda")+sp.I*component("imag")
    N = A-value*sp.eye(A.rows)
    step(ctx,"traslado","Restar λ en la diagonal y reducir el sistema homogéneo.",
         r"(A-\lambda I)v=0", matriz=show(N))
    if value.is_Rational:
        basis = [sp.Matrix(u) for u in kernel(rational_rows(N),ctx)]
    else:
        reduced, pivots = N.rref()
        basis = N.nullspace()
        step(ctx,"reduccion","Reducir con las entradas algebraicas exactas e identificar las variables libres.",
             sp.latex(reduced), pivotes=[i+1 for i in pivots])
    evidence = [bool(sp.simplify(A*u-value*u).is_zero_matrix) for u in basis]
    step(ctx,"verificacion","Comprobar Av=λv para cada vector encontrado.",
         r"Av_i=\lambda v_i", comprobaciones=evidence)
    return {"lambda":str(value),"base":[show(u) for u in basis],"dimension":len(basis),
            "es_valor_propio":bool(basis), "verificacion":all(evidence)}


def diagonalize(data, ctx):
    A = small(data, square=True, limit=3)
    choice = field_selection(data)
    values, _ = spectrum(A,ctx)
    vectors, diagonal, dimensions = [], [], []
    for value, mult in values.items():
        if choice=="real" and not value.is_real:
            continue
        basis = (A-value*sp.eye(A.rows)).nullspace()
        vectors.extend(basis)
        diagonal.extend([value]*len(basis))
        dimensions.append({"valor":str(value),"algebraica":mult,"geometrica":len(basis)})
        step(ctx,"espacio_propio","Resolver el núcleo y comparar las dos multiplicidades.",
             r"\ker(A-\lambda I)", **dimensions[-1], base=[show(v) for v in basis])
    if len(vectors)!=A.cols:
        step(ctx,"decision","Los espacios propios del cuerpo elegido no aportan suficientes vectores.")
        return {"cuerpo":choice,"diagonalizable":False,"multiplicidades":dimensions}
    P, D = sp.Matrix.hstack(*vectors), sp.diag(*diagonal)
    check = sp.simplify(A*P-P*D).is_zero_matrix
    step(ctx,"identidad","Comprobar el cambio de base.",r"AP=PD", comprobado=check)
    return {"cuerpo":choice,"diagonalizable":True,"P":show(P),"D":show(D),"verificacion":check}


def spectral(data,ctx):
    A = small(data,square=True,limit=3)
    if A!=A.T:
        raise ValueError("El teorema espectral real exige una matriz simétrica.")
    values,_ = spectrum(A,ctx)
    axes, diagonal = [], []
    for value in values:
        E = sp.Matrix.hstack(*(A-value*sp.eye(A.rows)).nullspace())
        for u in orthogonalize(E,ctx):
            axes.append(sp.simplify(u/sp.sqrt(u.dot(u))))
            diagonal.append(value)
    Q,D = sp.Matrix.hstack(*axes),sp.diag(*diagonal)
    ortho = sp.simplify(Q.T*Q-sp.eye(A.rows)).is_zero_matrix
    rebuild = sp.simplify(Q*D*Q.T-A).is_zero_matrix
    step(ctx,"identidad","Verificar los ejes unitarios y reconstruir la matriz.",
         r"Q^TQ=I,\qquad A=QDQ^T", ortogonal=ortho, reconstruccion=rebuild)
    result = {"Q":show(Q),"D":show(D),"ortonormal":ortho,"reconstruccion":rebuild}
    if A.rows==2:
        result["diagrama_vectores"] = [(f"Eje {i+1}, λ={diagonal[i]}", [0,0], list(map(real_display,q))) for i,q in enumerate(axes)]
    return result


def singular_values(data,ctx):
    A = small(data,limit=6)
    if data.get("imagen") and any(v<0 or v>255 for v in A):
        raise ValueError("Cada intensidad de píxel debe estar entre 0 y 255.")
    gram = A.T*A
    step(ctx,"gram","Construir la matriz de Gram. Sus autovalores son los cuadrados de los valores singulares.",
         r"A^TA v_i=\sigma_i^2v_i", matriz=show(gram))
    # La SVD directa evita elevar al cuadrado el condicionamiento al formar la matriz de Gram.
    import mpmath as mp
    rank = A.rank()
    k = integer(data.get("rango") if data.get("rango") is not None else rank,"Rango de truncamiento",0,rank)
    # Un contexto independiente evita compartir la precisión entre solicitudes.
    arithmetic = mp.mp.clone()
    arithmetic.dps = 50
    B = arithmetic.matrix([[arithmetic.mpf(int(v.p))/int(v.q) for v in row] for row in A.tolist()])
    left, sigmas, right = arithmetic.svd(B)
    U = arithmetic.matrix(A.rows, rank)
    W = arithmetic.matrix(A.cols,rank)
    values = []
    full = arithmetic.zeros(A.rows,A.cols)
    truncated = arithmetic.zeros(A.rows,A.cols)
    for i in range(rank):
        q = right[i,:].T
        sigma = sigmas[i]
        if not sigma:
            raise ValueError("La precisión disponible no resuelve este valor singular.")
        u = left[:,i]
        values.append(sigma)
        U[:,i], W[:,i] = u,q
        full += sigma*u*q.T
        if i<k:
            truncated += sigma*u*q.T
        step(ctx,"singular",f"Construir el par singular {i+1} a partir de su vector derecho.",
             r"u_i=Av_i/\sigma_i", lambda_gram=arithmetic.nstr(sigma*sigma,18), sigma=arithmetic.nstr(sigma,18))
    fmt = lambda M: [[arithmetic.nstr(M[i,j],18) for j in range(M.cols)] for i in range(M.rows)]
    frobenius = lambda M: arithmetic.sqrt(sum(x*x for x in M))
    error = frobenius(B-full)
    tail = frobenius(B-truncated)
    expected = arithmetic.sqrt(sum(s*s for s in values[k:]))
    matrix_norm = frobenius(B)
    relative = error / matrix_norm if matrix_norm else arithmetic.mpf(0)
    orth_error = max(frobenius(U.T*U-arithmetic.eye(rank)),frobenius(W.T*W-arithmetic.eye(rank))) if rank else arithmetic.mpf(0)
    tail_error = abs(tail-expected) / matrix_norm if matrix_norm else arithmetic.mpf(0)
    step(ctx,"reconstruccion","Medir reconstrucción y comparar el error de truncamiento con la cola singular.",
         r"\|A-A_k\|_F^2=\sum_{i>k}\sigma_i^2", error=arithmetic.nstr(tail,18), cola=arithmetic.nstr(expected,18))
    out = {"exactitud":"aproximada","rango_exacto":rank,"rango_truncado":k,"U_reducida":fmt(U),"V_reducida":fmt(W),
           "valores_singulares":[arithmetic.nstr(v,18) for v in values], "reconstruccion":fmt(full),"truncada":fmt(truncated),
           "error_reconstruccion_relativo":arithmetic.nstr(relative,18),"error_truncamiento":arithmetic.nstr(tail,18),
           "error_ortogonalidad":arithmetic.nstr(orth_error,18),
           "verificacion":max(relative,orth_error,tail_error) < arithmetic.mpf("1e-30")}
    if data.get("imagen"):
        out["visual_libro"] = {"tipo":"imagen","rango":k,"maximo":rank,"original":[list(map(real_display,row)) for row in A.tolist()],
                                "truncada":[[float(v) for v in row] for row in fmt(truncated)]}
    elif values:
        out["series"] = {"points":[[i,float(v)] for i,v in enumerate(values,1)],"names":["Valores singulares"]}
    return out


def norm_value(values, choice):
    if choice == "uno":
        return sum(map(abs, values))
    if choice == "infinito":
        return max(map(abs, values))
    raise ValueError("Elegí norma 1 o infinito.")


def sensitivity(data, ctx):
    A = small(data,square=True)
    b, delta = (sp.Matrix(vector(data[key],A.rows)) for key in ("b","delta"))
    choice = data["norma"]
    measure = lambda v: norm_value(v,choice)
    by_axis = (lambda M: M.T.tolist()) if choice=="uno" else (lambda M: M.tolist())
    induced = lambda M: max(sum(map(abs,v)) for v in by_axis(M))
    if measure(b)==0:
        raise ValueError("Con b nulo el cambio relativo de la entrada queda indefinido.")
    R = rational_rows(A)
    def rational_column(v):
        return [F(int(t.p),int(t.q)) for t in v]
    first = solve(R,rational_column(b),ctx)
    if first["clasificacion"]!="unica":
        step(ctx,"condicion","Una matriz singular carece de inversa. No hay una solución única para medir el cambio relativo.",
             r"\kappa(A)\text{ no es finito}", rango=first["rango_A"])
        return {"norma":choice,"condicion":None,"clasificacion":first["clasificacion"],
                "diagnostico":"La sensibilidad de una solución única queda indefinida."}
    second = solve(R,rational_column(b+delta),ctx)
    x, changed = sp.Matrix(first["particular"]),sp.Matrix(second["particular"])
    relative_b, relative_x = measure(delta)/measure(b), measure(changed-x)/measure(x)
    condition = induced(A)*induced(A.inv())
    bound = condition*relative_b
    step(ctx,"condicion","Comparar perturbaciones de los datos y la solución exacta.",
         r"\frac{\|\Delta x\|}{\|x\|}\le\kappa(A)\frac{\|\Delta b\|}{\|b\|}",
         delta_b=str(relative_b),delta_x=str(relative_x),cota=str(bound))
    return {"norma":choice,"x":show(x),"x_perturbada":show(changed),"condicion":str(condition),
            "cambio_relativo_b":str(relative_b),"cambio_relativo_x":str(relative_x),"cota":str(bound),
            "verificacion":bool(relative_x<=bound),"referencia":"Ambos sistemas se resolvieron con aritmética racional."}


def pivoting(data,ctx):
    A = small(data,square=True)
    b = sp.Matrix(vector(data["b"],A.rows))
    digits = integer(data["cifras"],"Cifras significativas",3,14)
    exact = solve(rational_rows(A),[F(int(v.p),int(v.q)) for v in b],ctx)
    if exact["clasificacion"]!="unica":
        raise ValueError("Elegí una matriz invertible para comparar con una referencia única.")
    exact = exact["particular"]
    def simulate(pivot):
        mode = "con pivoteo parcial" if pivot else "sin pivoteo"
        def to_decimal(value):
            f = F(value)
            return Decimal(f.numerator)/Decimal(f.denominator)
        with localcontext() as arithmetic:
            arithmetic.prec = digits
            n = A.rows
            grid = [[to_decimal(v) for v in row] for row in A.row_join(b).tolist()]
            max_factor = Decimal(0)
            for i in range(n):
                if pivot:
                    row = max(range(i,n),key=lambda k: abs(grid[k][i]))
                    if row!=i:
                        grid[i],grid[row] = grid[row],grid[i]
                        step(ctx,"intercambio",f"{mode}: intercambiar las filas {i+1} y {row+1}.")
                lead = grid[i][i]
                if not lead:
                    step(ctx,"detencion",f"{mode}: pivote nulo tras el redondeo.",fila=i+1)
                    return {"estado":"pivote_nulo","fila":i+1,"factor_maximo":max_factor}
                for j in range(i+1,n):
                    factor = grid[j][i]/lead
                    max_factor = max(max_factor,abs(factor))
                    before = grid[j][:]
                    grid[j] = [Decimal(0)]*(i+1)+[grid[j][k]-factor*grid[i][k] for k in range(i+1,n+1)]
                    step(ctx,"eliminacion",f"{mode}: reducir la fila {j+1} usando el pivote de la fila {i+1}.",
                         rf"F_{{{j+1}}}\gets F_{{{j+1}}}-mF_{{{i+1}}}",factor=factor,antes=before,despues=grid[j])
            x = [Decimal(0)]*n
            for i in reversed(range(n)):
                x[i] = (grid[i][-1]-sum(grid[i][j]*x[j] for j in range(i+1,n)))/grid[i][i]
        error = max(abs(F(x[i])-exact[i]) for i in range(len(x)))
        return {"estado":"completo","x":x,"factor_maximo":max_factor,"error_infinito":error}
    return {"exactitud":"aproximada","referencia_racional":list(map(str,exact)),
            "sin_pivoteo":simulate(False),"con_pivoteo":simulate(True)}
