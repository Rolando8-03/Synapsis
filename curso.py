"""Operaciones del temario que complementan el solucionador original."""
import ast
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
from fractions import Fraction
from functools import reduce
from itertools import combinations
from math import factorial, gcd, lcm
import re
import sys

import sympy as sp
from sympy.solvers.solveset import NonlinearError

from motor_matematico.algorithms.linear.context import Context, integer, matrix, vector
from motor_matematico.algorithms.numerical.functions import Function, decimal
from motor_matematico.parsing.numbers import parse_number


def polynomial(source, variables):
    """Construir polinomios desde nodos permitidos sin ejecutar texto del usuario."""
    text = str(source).strip().replace('−', '-').replace('·', '*').replace('^', '**')
    if not text or len(text) > 500:
        raise ValueError('Escribí un polinomio de hasta 500 caracteres.')
    names = {str(symbol): symbol for symbol in variables}
    text = re.sub(r'(?<=[0-9)])(?=(?:[a-df-zA-DF-Z(]|[eE](?![+-]?\d)))', '*', text)
    text = re.sub(r'(?<=[A-Za-z])(?=\()', '*', text)
    try:
        tree = ast.parse(text, mode='eval')
    except SyntaxError as error:
        raise ValueError('Revisá la expresión. Usá * para multiplicar y ^ para elevar.') from error
    if sum(1 for _ in ast.walk(tree)) > 110:
        raise ValueError('La expresión supera el tamaño permitido.')

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = parse_number(ast.get_source_segment(text, node))
            return sp.Rational(value.numerator, value.denominator)
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = visit(node.operand)
            return -operand if isinstance(node.op, ast.USub) else operand
        if not isinstance(node, ast.BinOp):
            raise ValueError('Usá números, variables declaradas y operaciones de polinomios.')
        a, b = visit(node.left), visit(node.right)
        if isinstance(node.op, ast.Add):
            value = a + b
        elif isinstance(node.op, ast.Sub):
            value = a - b
        elif isinstance(node.op, ast.Mult):
            value = a * b
        elif isinstance(node.op, ast.Div) and b.is_Rational and b != 0:
            value = a / b
        elif isinstance(node.op, ast.Pow) and b.is_Integer and 0 <= b <= 8:
            value = a ** int(b)
        else:
            raise ValueError('Usá exponentes enteros entre 0 y 8 y divisores constantes no nulos.')
        if value.is_Rational:
            if max(int(value.p).bit_length(), int(value.q).bit_length()) > 384:
                raise ValueError('Los coeficientes individuales son demasiado grandes.')
            return value
        if isinstance(node.op, (ast.Mult, ast.Pow)):
            a_poly = sp.Poly(a, *variables)
            increment = int(b)*a_poly.total_degree() if isinstance(node.op, ast.Pow) else a_poly.total_degree()+sp.Poly(b,*variables).total_degree()
            if increment > 8 or (len(a_poly.terms()) > 12 and not b.is_Rational):
                raise ValueError('El polinomio intermedio es demasiado grande.')
        poly = sp.Poly(value, *variables)
        if len(poly.terms()) > 70 or poly.total_degree() > 8:
            raise ValueError('Se admiten hasta 70 términos y grado total 8.')
        if any(max(int(coef.p).bit_length(), int(coef.q).bit_length()) > 384 for coef in poly.coeffs()):
            raise ValueError('Los coeficientes individuales son demasiado grandes.')
        return poly.as_expr()

    return visit(tree.body)


def symbols(text):
    names = str(text).replace(',', ' ').split()
    if not 1 <= len(names) <= 8 or len(set(names)) != len(names) or any(
        not re.fullmatch(r'[a-z][a-z0-9]{0,6}', name) for name in names
    ):
        raise ValueError('Ingresá hasta 8 variables distintas, por ejemplo x y z o x1 x2 x3.')
    return tuple(sp.Symbol(name, real=True) for name in names)


def lines(text, limit):
    if not isinstance(text, str) or len(text) > 4000:
        raise ValueError('La entrada admite hasta 4000 caracteres.')
    parts = [line.strip() for line in re.split(r'[\n;]+', text) if line.strip()]
    if not 1 <= len(parts) <= limit:
        raise ValueError(f'Ingresá de 1 a {limit} expresiones separadas por líneas.')
    return parts


def system_data(expressions, variables, parameter=None):
    scope = variables + ((parameter,) if parameter is not None else ())
    equations = []
    for line in lines(expressions, 12):
        sides = line.split('=')
        if len(sides) > 2:
            raise ValueError('Cada ecuación debe contener como máximo un signo igual.')
        equations.append(polynomial(sides[0], scope) - polynomial(sides[1], scope) if len(sides) == 2 else polynomial(sides[0], scope))
    try:
        return sp.linear_eq_to_matrix(equations, variables)
    except NonlinearError as error:
        raise ValueError('Las ecuaciones deben ser lineales en las incógnitas declaradas.') from error


def rows_text(A):
    return [[str(value) for value in row] for row in A.tolist()]


def as_fraction(value):
    return Fraction(int(value.p), int(value.q))


def analyze_affine(A, b):
    augmented = A.row_join(b)
    a_rank, ab_rank = A.rank(), augmented.rank()
    solution = next(iter(sp.linsolve((A, b))), None)
    result = {
        'rango_A': a_rank, 'rango_aumentada': ab_rank, 'incognitas': A.cols,
        'clasificacion': 'Sin solución' if solution is None else 'Solución única' if a_rank == A.cols else 'Infinitas soluciones',
    }
    if solution is not None:
        result['solucion'] = [sp.sstr(item) for item in solution]
    return result


def from_equations(data, solve, ctx):
    variables = symbols(data['variables'])
    A, b = system_data(data['ecuaciones'], variables)
    recipe = [[as_fraction(value) for value in row] for row in A.row_join(b).tolist()]
    for i,(row,rhs) in enumerate(zip(A.tolist(),b),1):
        ctx.emit("ecuacion",f"Leer los coeficientes de la ecuación {i} en el orden de las incógnitas.",
                 {"coeficientes":[str(x) for x in row],"termino_independiente":str(rhs)})
    result = solve({'matrix': recipe, 'steps': ctx.collect_steps})
    if ctx.collect_steps:
        from procedimientos import original_rows
        original_rows(ctx,result["pasos_jordan"])
        ctx.emit("clasificar","Comparar los rangos y leer la solución.",{"clasificacion":result["clasificacion"]},
                 result.get("latex_solucion",""))
    return {
        'variables': [str(variable) for variable in variables], 'A': rows_text(A),
        'b': rows_text(b), 'matriz_aumentada': rows_text(A.row_join(b)),
        'clasificacion': result['clasificacion'],
        'ecuaciones': [str(lhs) + ' = ' + str(rhs) for lhs, rhs in zip(A*sp.Matrix(variables), b)],
        'rango_A': result['rango_A'], 'rango_aumentada': result['rango_aumentada'],
        'forma_reducida': result['matriz_rref'], 'solucion_particular': result['solucion_particular'],
        'direcciones': result['direcciones'],
    }


def rank_polynomials(matrix, parameter):
    """El mcd de los menores de cada orden se anula justo cuando cae el rango."""
    profile = {}
    for order in range(1, min(matrix.shape) + 1):
        divisor = sp.Poly(0, parameter, domain=sp.QQ)
        for rows in combinations(range(matrix.rows), order):
            for cols in combinations(range(matrix.cols), order):
                minor = matrix.extract(rows, cols).det(method="berkowitz")
                divisor = divisor.gcd(sp.Poly(minor, parameter, domain=sp.QQ))
                if divisor.degree() == 0:
                    break
            if divisor.degree() == 0:
                break
        if divisor.is_zero:
            break
        profile[order] = divisor
    return profile


def classify_ranks(rank_a, rank_ab, variables):
    if rank_a != rank_ab:
        classification = "Sin solución"
    elif rank_a == variables:
        classification = "Solución única"
    else:
        classification = "Infinitas soluciones"
    return {"rango_A": rank_a, "rango_aumentada": rank_ab, "incognitas": variables,
            "clasificacion": classification}


def parametric(data, ctx):
    variables = symbols(data['variables'])
    params = symbols(data['parametro'])
    if len(params) != 1 or params[0] in variables or len(variables) > 4:
        raise ValueError('Usá un parámetro distinto de las 1 a 4 incógnitas.')
    parameter = params[0]
    A, b = system_data(data['ecuaciones'], variables, parameter)
    if A.rows != A.cols:
        raise ValueError('Para Cramer paramétrico ingresá un sistema cuadrado de hasta 4 ecuaciones.')
    det = sp.Poly(A.det(method='berkowitz'), parameter)
    if det.degree() > 8:
        raise ValueError('El determinante paramétrico excede grado 8.')
    result = {'parametro': str(parameter), 'A': rows_text(A), 'b': rows_text(b),
              'determinante': str(det.as_expr()), 'formula_latex': r'\det(A)=' + sp.latex(det.as_expr())}
    ctx.emit("determinante","Calcular y simplificar el determinante de la matriz de coeficientes.",
             {"A":rows_text(A),"determinante":str(det.as_expr()),"factorizado":str(sp.factor(det.as_expr()))},result["formula_latex"])
    coefficient_ranks = rank_polynomials(A, parameter)
    augmented_ranks = rank_polynomials(A.row_join(b), parameter)

    def rank_at(profile, factor):
        return max((order for order, divisor in profile.items() if not divisor.rem(factor).is_zero), default=0)

    # Con determinante idénticamente nulo también pueden cambiar ambos rangos.
    critical = sp.Poly(1, parameter, domain=sp.QQ)
    for profile in (coefficient_ranks, augmented_ranks):
        if profile:
            critical = critical.lcm(profile[max(profile)])
    cases = {}
    for factor, _ in critical.factor_list()[1]:
        for root in factor.real_roots():
            case = classify_ranks(rank_at(coefficient_ranks, factor), rank_at(augmented_ranks, factor), A.cols)
            if root.is_Rational:
                case = analyze_affine(A.subs(parameter, root), b.subs(parameter, root))
            else:
                case["polinomio_minimo"] = str(factor.monic().as_expr())
            cases[root] = case
    ordered = sorted(cases, key=lambda root: root.evalf())
    singular = det.real_roots(multiple=False) if not det.is_zero else []
    result.update(valores_singulares_reales=[str(root) for root, _ in singular],
                  casos_singulares={str(root): cases[root] for root in ordered})
    ctx.emit("ceros", "Separar los puntos reales donde puede cambiar el rango.",
             {"valores": [str(root) for root in ordered]}, sp.latex(critical.as_expr()) + "=0")
    for root in ordered:
        ctx.emit("caso_singular", "Clasificar con rangos exactos en el valor excepcional.",
                 {"parametro": str(root), **cases[root]}, sp.latex(parameter) + "=" + sp.latex(root))
    if det.is_zero:
        generic = classify_ranks(max(coefficient_ranks, default=0), max(augmented_ranks, default=0), A.cols)
        result.update(solucion_unica="Ningún valor real del parámetro",
                      fuera_de_los_valores_excepcionales=generic,
                      criterio="El determinante es idénticamente cero. La compatibilidad se decide por los rangos.")
        ctx.emit("compatibilidad_generica", "Comparar los rangos fuera de los valores excepcionales.", generic)
        return result
    formulas = {}
    for i, variable in enumerate(variables):
        replaced = A.copy()
        replaced[:, i] = b
        numerator = replaced.det(method='berkowitz')
        quotient = sp.cancel(numerator/det.as_expr())
        formulas[str(variable)] = str(quotient)
        ctx.emit("cramer",f"Reemplazar la columna {i+1} por b y aplicar Cramer.",
                 {"matriz":rows_text(replaced),"determinante":str(numerator)},
                 sp.latex(variable)+r"=\frac{"+sp.latex(numerator)+"}{"+sp.latex(det.as_expr())+"}="+sp.latex(quotient))
    result['criterio'] = 'Solución única cuando el parámetro es distinto de los valores singulares.'
    result['solucion_por_cramer'] = formulas
    return result


def transformation(data, ctx):
    variables = symbols(data['variables'])
    components = [polynomial(line, variables) for line in lines(data['componentes'], 12)]
    zero = {v: 0 for v in variables}
    image_zero = [sp.expand(p).subs(zero) for p in components]
    result = {'T_de_cero': [str(v) for v in image_zero]}
    ctx.emit("origen","Evaluar la imagen del vector cero.",result)
    for i, component in enumerate(components, 1):
        poly = sp.Poly(component, *variables)
        ctx.emit("componente",f"Ordenar y analizar la componente {i}.",{"grado":int(poly.total_degree()),"constante":str(poly.TC())},
                 rf"T_{{{i}}}="+sp.latex(component))
        if poly.total_degree() > 1 or poly.TC() != 0:
            scale = sp.Dummy("lambda", real=True)
            changed = component.xreplace({v:scale*v for v in variables})
            failure = sp.expand(changed-scale*component)
            ctx.emit("demostrar_no_lineal","Restar los lados de la condición de homogeneidad.",
                     {"diferencia":str(failure)},
                     rf"T_{{{i}}}(\lambda x)-\lambda T_{{{i}}}(x)={sp.latex(failure)}\not\equiv0")
            values = {}
            remaining = failure
            for symbol in (scale, *variables):
                degree = int(sp.degree(remaining, symbol))
                choice = next(k for k in range(2, degree + 3) if remaining.subs(symbol, k) != 0)
                values[symbol] = choice
                remaining = remaining.subs(symbol, choice)
            point = {v: values[v] for v in variables}
            image_scaled = component.subs({v: values[scale] * values[v] for v in variables})
            scaled_image = values[scale] * component.subs(point)
            witness = {"vector": list(point.values()), "escalar": values[scale],
                       "T_del_vector_escalado": str(image_scaled), "escalar_por_T": str(scaled_image)}
            ctx.emit("contraejemplo", "Sustituir valores concretos que rompen la homogeneidad.",
                     witness, sp.latex(image_scaled) + r"\ne " + sp.latex(scaled_image))
            result.update(lineal=False, componente=i, contraejemplo=witness,
                          motivo='Aparece un término de grado mayor que uno.' if poly.total_degree() > 1 else 'La imagen del cero no es el cero.',
                          formula_latex=rf'T_{{{i}}}=' + sp.latex(component))
            return result
    A = sp.Matrix([[p.coeff(x) for x in variables] for p in components])
    ctx.emit("matriz","Usar los coeficientes ordenados como filas de la matriz estándar.",{"A":rows_text(A)})
    ctx.emit("aditividad","Distribuir la matriz sobre la suma de dos vectores arbitrarios.",{},r"T(u+v)=A(u+v)=Au+Av=T(u)+T(v)")
    ctx.emit("homogeneidad","Extraer el escalar del producto matriz-vector.",{},r"T(\alpha u)=A(\alpha u)=\alpha Au=\alpha T(u)")
    from motor_matematico.algorithms.linear.spaces import fundamental
    from procedimientos import matvec_steps
    spaces, proof = fundamental(matrix(rows_text(A)),ctx)
    kernel, image = spaces["base_nucleo"], spaces["base_columna"]
    result.update(lineal=True, matriz_estandar=rows_text(A),
                  nucleo=[list(map(str,v)) for v in kernel],
                  base_imagen=[list(map(str,v)) for v in image],
                  rango=len(image), nulidad=len(kernel),
                  formula_latex=r'T\left(' + ','.join(map(sp.latex, variables)) + r'\right)=' + sp.latex(sp.Matrix(components)))
    ctx.emit("rango_nulidad","Extraer la imagen de las columnas pivote originales y el núcleo de las variables libres.",
             {"columnas_pivote":[i+1 for i in spaces["pivotes"]],"base_imagen":image,"base_nucleo":kernel},
             rf"{A.cols}={len(image)}+{len(kernel)}")
    if data.get('v'):
        values = vector(data['v'], len(variables))
        result['T_de_v'] = [str(entry) for entry in A * sp.Matrix(values)]
        if ctx.collect_steps:
            matvec_steps(ctx,rows_text(A),values,result["T_de_v"],"T(v)")
    return result


def subspace(data, ctx):
    variables = symbols(data['variables'])
    A, b = system_data(data['ecuaciones'], variables)
    affine = analyze_affine(A, b)
    from motor_matematico.algorithms.linear.reduction import solve
    reduced = solve(matrix(rows_text(A)), vector(list(map(str,b))), ctx)
    basis = reduced["direcciones"]
    homogeneous = not any(b)
    ctx.emit("cero","Sustituir el vector cero en las restricciones.",{"terminos_independientes":rows_text(b),"contiene_cero":homogeneous},
             r"A0=0")
    if homogeneous:
        ctx.emit("cerradura_suma","Para dos soluciones homogéneas, distribuir A sobre su suma.",{},r"A(u+v)=Au+Av=0")
        ctx.emit("cerradura_escalar","Extraer un escalar arbitrario del producto.",{},r"A(\alpha u)=\alpha Au=0")
        ctx.emit("base","Cada dirección tiene un 1 en su variable libre y ceros en las demás; eso prueba independencia.",
                 {"base":basis,"variables_libres":[i+1 for i in reduced["variables_libres"]]},r"\dim H=n-\operatorname{rang}A")
    result = dict(affine, es_subespacio=homogeneous, contiene_cero=homogeneous,
                  formula_latex=r'H=\{x\mid Ax=b\}', A=rows_text(A), b=rows_text(b))
    if homogeneous:
        result.update(cerrado_bajo_suma=True, cerrado_bajo_producto_escalar=True,
                      base=[list(map(str, value)) for value in basis], dimension=len(basis),
                      justificacion='Si Au=Av=0, entonces A(αu+βv)=αAu+βAv=0.')
    else:
        result['justificacion'] = 'El vector cero no satisface una o más ecuaciones.' if affine['rango_A'] == affine['rango_aumentada'] else 'El conjunto es vacío.'
        failed, rhs = next((i, value) for i, value in enumerate(b, 1) if value)
        ctx.emit("testigo_subespacio", "El origen incumple una de las restricciones.",
                 {"vector_cero": [0] * len(variables), "ecuacion": failed, "obtenido": 0, "requerido": str(rhs)},
                 r"0\ne " + sp.latex(rhs))
    return result


def polynomials(data, context):
    x = sp.Symbol('x', real=True)
    degree = integer(data['grado'], 'Grado máximo', 0, 8)
    def coefficients(text):
        poly = sp.Poly(polynomial(text,(x,)),x)
        if poly.degree() > degree:
            raise ValueError('Un polinomio supera el grado del espacio elegido.')
        return [as_fraction(poly.nth(i)) for i in range(degree+1)]
    family = [coefficients(x) for x in lines(data['familia'], 15)]
    from motor_matematico.algorithms.linear.spaces import study, membership
    context.emit("coordenadas","Leer coeficientes en la base canónica, empezando por el término constante.",
                 {"vectores_de_coeficientes":family},r"\mathcal B=(1,x,\ldots,x^n)")
    out, _ = study(family, degree+1, context)
    if data.get('objetivo'):
        out['pertenencia'], _ = membership(family, coefficients(data['objetivo']), degree+1, context)
    out['base_canonica'] = ['1', *['x' if i == 1 else f'x^{i}' for i in range(1,degree+1)]]
    out['formula_latex'] = rf'a_0+a_1x+\cdots+a_{{{degree}}}x^{{{degree}}}' if degree else 'a_0'
    return out


def entry(data, context):
    A = matrix(data['A'])
    m, n = len(A), len(A[0])
    i = integer(data['fila'], 'Fila', 1, m) - 1
    j = integer(data['columna'], 'Columna', 1, n) - 1
    value = A[i][j]
    from motor_matematico.algorithms.linear.context import tex
    context.emit('posicion', f'Ir a la fila {i+1} y columna {j+1}.', {'fila': A[i], 'columna': [r[j] for r in A]})
    return {'orden': f'{m} × {n}', 'entrada': value, 'fila': A[i],
            'columna': [[r[j]] for r in A], 'diagonal': [A[k][k] for k in range(min(m,n))],
            'formula_latex': rf'a_{{{i+1},{j+1}}}={tex(value)}'}


def matrix_compare(data, context):
    from motor_matematico.algorithms.linear.context import multiply
    A, B = matrix(data['A']), matrix(data['B'])
    out = {'mismo_orden': (len(A),len(A[0])) == (len(B),len(B[0])), 'iguales': A == B}
    products = {}
    for name, left, right in (('AB', A, B), ('BA', B, A)):
        if len(left[0]) == len(right):
            products[name] = multiply(left, right, context)
    out.update(products)
    if len(products) == 2:
        out['conmutan'] = products['AB'] == products['BA']
    else:
        out['motivo'] = 'Al menos uno de los productos tiene dimensiones incompatibles.'
    return out


def invertible_theorem(data, context):
    from motor_matematico.algorithms.linear.matrix import determinant, invert
    A = matrix(data['A'], square=True)
    n = len(A)
    determinant_value = determinant(A, context, 'reduccion')
    # La forma reducida permite explicar todos los criterios equivalentes.
    from motor_matematico.algorithms.linear.reduction import reduce as row_reduce
    rref = row_reduce(A, context)
    rank = len(rref['pivots'])
    value = rank == n
    out = {'invertible': value, 'determinante': determinant_value, 'pivotes': rank,
           'orden': n, 'rref': rref['matrix'],
           'criterios': dict.fromkeys([
                'equivalente_a_la_identidad','columnas_independientes','columnas_generan_Rn',
                'nucleo_trivial', 'inyectiva', 'sobreyectiva', 'inversa_a_izquierda',
                'inversa_a_derecha', 'transpuesta_invertible'], value),
           'formula_latex': r'\det(A)\ne0\iff\operatorname{rang}(A)=n\iff A\text{ es invertible}'}
    context.emit("teorema", "Aplicar el teorema de la matriz invertible.", {"teorema": {
        "enunciado": r"\det(A)\ne0\iff\operatorname{rang}(A)=n\iff A\text{ es invertible}",
        "hipotesis": f"A es una matriz cuadrada de orden {n}.",
        "evidencia": {"determinante": determinant_value, "rango_A": rank, "rref": rref["matrix"]},
        "conclusion": "A es invertible." if value else "A es singular.",
    }})
    if value:
        out['inversa'], _ = invert(A, context)
    return out


def economy(data, ctx):
    M = matrix(data['A'], square=True)
    n = len(M)
    scale = 100 if data['unidades'] == 'porcentaje' else 1
    if any(value < 0 for row in M for value in row):
        raise ValueError('Las participaciones deben ser no negativas.')
    A = [[entry / scale for entry in row] for row in M]
    ctx.emit("unidades_economia", "Leer las columnas como sectores productores y las filas como sectores receptores.",
             {"unidades_de_entrada": data["unidades"], "divisor": scale, "proporciones": A},
             r"m_{ij}=	ext{parte de la producción de }j	ext{ que recibe }i")
    for i in range(n):
        total = sum(A[j][i] for j in range(n) if i != j)
        if total > 1:
            raise ValueError(f'Las ventas de la columna {i+1} superan el total de su producción.')
        A[i][i] = 1 - total
        ctx.emit("retencion",f"Completar la proporción que conserva el sector {i+1}.",
                 {"suma_distribuida":total,"proporcion_retenida":A[i][i]},
                 rf"m_{{{i+1},{i+1}}}=1-({total})={A[i][i]}")
    C = sp.eye(n) - sp.Matrix(A)
    b = sp.zeros(n, 1)
    if data.get('precio'):
        index = integer(data['sector'], 'Sector de referencia', 1, n) - 1
        fixed = parse_number(data['precio'])
        if fixed <= 0:
            raise ValueError('El precio fijado debe ser positivo.')
        C = C.col_join(sp.eye(n)[index,:])
        b = b.col_join(sp.Matrix([fixed]))
    from motor_matematico.algorithms.linear.reduction import solve
    ctx.emit("modelo","Trasladar la producción distribuida y añadir el precio de referencia cuando esté indicado.",
             {"tabla_intercambio":A,"matriz":rows_text(C.row_join(b)),"separador":C.cols},r"(I-M)p=0")
    from procedimientos import model_rows
    model_rows(ctx, rows_text(C), list(map(str, b)), "p", "equilibrio", "precio en la unidad monetaria de referencia")
    solve(matrix(rows_text(C)),vector(list(map(str,b))),ctx)
    return {'tabla_intercambio': A, 'modelo': rows_text(C.row_join(b)),
            'equilibrio': analyze_affine(C,b), 'formula_latex': r'(I-M)p=0'}


def balance(data, ctx):
    A = matrix(data['A'])
    if any(x.denominator != 1 for row in A for x in row):
        raise ValueError('La matriz de átomos debe contener cantidades enteras con signo.')
    S = sp.Matrix(A)
    from motor_matematico.algorithms.linear.reduction import solve
    from procedimientos import model_rows
    model_rows(ctx, A, [Fraction(0)] * len(A), "c", "conservación",
               "átomos por compuesto; positivo en reactivos, negativo en productos")
    solved = solve(A,[Fraction(0)]*len(A),ctx)
    basis = [sp.Matrix(v) for v in solved["direcciones"]]
    out = {'matriz_de_balance': A, 'dimension_del_nucleo': len(basis),
           'generadores': [list(map(str, v)) for v in basis], 'formula_latex': r'Ac=0'}
    if len(basis) == 1:
        multiplier=lcm(*(int(w.q) for w in basis[0]))
        row = [int(v*multiplier) for v in basis[0]]
        ctx.emit("denominadores","Multiplicar el vector de proporciones por el mínimo común múltiplo.",
                 {"mcm":multiplier,"vector_entero":row})
        primitive = [v // reduce(gcd, row) for v in row]
        if all(v < 0 for v in primitive):
            primitive = [-v for v in primitive]
        if all(v > 0 for v in primitive):
            out['coeficientes_enteros_minimos'] = primitive
            ctx.emit("comprobar","Reducir por el máximo común divisor y comprobar todos los balances.",
                     {"coeficientes":primitive,"resultado":[str(v) for v in S*sp.Matrix(primitive)]},r"Ac=0")
        else:
            out['conclusion'] = 'No se obtuvo un balance que incluya todos los compuestos con coeficientes positivos.'
    elif not basis:
        out['conclusion'] = 'Solo existe la solución trivial.'
    else:
        out['conclusion'] = 'El balance tiene varios parámetros. Elegí una combinación de los generadores con coeficientes enteros positivos.'
    return out


def nonnegative(data, ctx):
    A = matrix(data['A'])
    b = vector(data['b'], len(A))
    S, d = sp.Matrix(A), sp.Matrix(b)
    if S.cols > 8:
        raise ValueError('Este análisis admite hasta 8 variables de flujo.')
    out = analyze_affine(S,d)
    from motor_matematico.algorithms.linear.reduction import solve
    from procedimientos import model_rows
    model_rows(ctx, A, b, "x", "balance de flujos",
               "cada flujo y término independiente se expresa en la misma unidad por período")
    solve(A,b,ctx)
    ctx.emit("restricciones","Restringir la familia a flujos no negativos.",{},r"x_i\ge0")
    from sympy.solvers.simplex import InfeasibleLPError, UnboundedLPError, linprog
    if out['rango_A'] != out['rango_aumentada']:
        out['factible_no_negativo'] = False
        return out
    extrema = []
    for i in range(S.cols):
        objective = [int(j == i) for j in range(S.cols)]
        try:
            low, _ = linprog(objective, A_eq=S, b_eq=d, A=sp.zeros(1,S.cols), b=[0])
        except InfeasibleLPError:
            out['factible_no_negativo'] = False
            return out
        try:
            high, _ = linprog([-x for x in objective], A_eq=S, b_eq=d, A=sp.zeros(1,S.cols), b=[0])
            high = str(-high)
        except UnboundedLPError:
            high = 'Sin máximo finito'
        extrema.append([f'x{i+1}', str(low), high])
        ctx.emit("extremos",f"Minimizar y maximizar la variable {i+1} sobre la misma región factible.",
                 {"minimo":str(low),"maximo":high,"restriccion":"Ax=b; x≥0"})
    out.update(factible_no_negativo=True, tabla=extrema, encabezados=['Variable','Mínimo','Máximo'],
               formula_latex=r'Ax=b,\quad x_i\ge0')
    return out


def precision(data):
    exact = parse_number(data['numero'])
    places = integer(data['decimales'], 'Decimales', 0, 18)
    digits = integer(data['cifras'], 'Cifras significativas', 1, 18)
    scale = 10**places
    sign = -1 if exact < 0 else 1
    scaled = abs(exact)*scale
    truncated = int(scaled)
    rounded = truncated + int(scaled - truncated >= Fraction(1,2))
    def display(n):
        digits = str(n).zfill(places+1)
        return ('-' if sign < 0 and n else '') + (digits[:-places]+'.'+digits[-places:] if places else digits)
    truncation_error = exact - Fraction(sign * truncated, scale)
    rounding_error = exact - Fraction(sign * rounded, scale)
    return {'referencia': exact, 'truncado': display(truncated), 'redondeado': display(rounded),
            'fraccion_descartada_en_la_ultima_posicion': scaled - truncated,
            'error_de_truncamiento': truncation_error,
            'error_de_redondeo': rounding_error,
            'error_relativo_truncamiento': abs(truncation_error / exact) if exact else None,
            'error_relativo_redondeo': abs(rounding_error / exact) if exact else None,
            'motivo_relativo_indefinido': 'La referencia es cero.' if not exact else None,
            'tolerancia_porcentual': str(Decimal(5).scaleb(1-digits)),
            'formula_latex': r'\varepsilon_s=0.5\times10^{2-n}\,\%'}


def propagation(data):
    f = Function(data['expresion'], Context())
    x, shift = parse_number(data['x']), parse_number(data['delta'])
    with localcontext() as arithmetic:
        arithmetic.prec = 40
        if shift:
            f.continuous(min(x, x+shift), max(x, x+shift))
        try:
            derived, method = f.derivative()
            derivative = derived.exact(x)
        except ValueError:
            h = max(abs(x), 1) / 10**8
            f.continuous(x-h, x+h)
            derivative = (f.exact(x+h) - f.exact(x-h)) / (2*h)
            method = 'diferencia central con paso ' + str(h)
        actual = f.exact(x+shift) - f.exact(x)
        linear = derivative * shift
        return {'derivada': str(decimal(derivative)),
                'metodo': method, 'diferencial': str(decimal(linear)),
                'variacion': str(decimal(actual)),
                'error_absoluto': str(decimal(abs(actual-linear))),
                'error_relativo': str(decimal(abs((actual-linear)/actual))) if actual else None,
                'motivo_relativo_indefinido': 'La variación de referencia es cero.' if not actual else None,
                'formula_latex': r'\Delta y\approx f^{\prime}(x)\Delta x'}


def accumulation(data):
    principal = parse_number(data['capital'])
    rate = parse_number(data['tasa'])/100
    length = integer(data['periodos'], 'Periodos', 1, 120)
    places = integer(data['decimales'], 'Decimales', 0, 12)
    if not 0 <= principal <= 10**12 or not -1 <= rate <= 1:
        raise ValueError('Usá capital entre 0 y 10¹² y tasa de −100 % a 100 % por período.')
    quantum = Decimal(1).scaleb(-places)
    table, points = [], []
    with localcontext() as ctx:
        ctx.prec = 42
        real, truncated, rounded = [decimal(principal)]*3
        factor = 1 + decimal(rate)
        for i in range(1, length+1):
            real *= factor
            truncated = (truncated * factor).quantize(quantum, rounding=ROUND_DOWN)
            rounded = (rounded * factor).quantize(quantum, rounding=ROUND_HALF_UP)
            error_truncated, error_rounded = real-truncated, real-rounded
            table.append([i, str(real.quantize(quantum)), str(truncated), str(rounded),
                          format(error_truncated,'.10g'), format(error_rounded,'.10g')])
            points.append([i, float(error_truncated), float(error_rounded)])
    return {'referencia_final': str(real), 'truncamiento_final': str(truncated),
            'redondeo_final': str(rounded),
            'encabezados': ['Período','Referencia a los decimales elegidos','Truncado','Redondeado','Error de truncamiento','Error de redondeo'],
            'tabla': table, 'series': {'points': points, 'names': ['Error de truncamiento','Error de redondeo']},
            'formula_latex': r'C_{k+1}=C_k(1+r)'}


def machine(data):
    v = sys.float_info
    a, b = float(parse_number(data['a'])), float(parse_number(data['b']))
    if not 0 <= b < a <= 1e150:
        raise ValueError('Para comparar la resta de raíces elegí 0 ≤ b < a ≤ 10¹⁵⁰.')
    from math import sqrt, ulp
    direct = sqrt(a+b) - sqrt(a-b)
    rationalized = (2*b)/(sqrt(a+b) + sqrt(a-b))
    return {'epsilon': v.epsilon, 'maximo_finito': v.max, 'minimo_normal': v.min,
            'minimo_subnormal': ulp(0.0), 'resta_directa': direct, 'forma_racionalizada': rationalized,
            'demostraciones': {
                'suma_binaria':repr(.1+.2), 'igual_a_0_3':.1+.2 == .3,
                'overflow':str(v.max*2), 'underflow':str(ulp(0.0)/2),
                'primer_numero_mayor_a_uno':repr(1+v.epsilon),
            },
            'formula_latex': r'\sqrt{a+b}-\sqrt{a-b}=\frac{2b}{\sqrt{a+b}+\sqrt{a-b}}'}


def dominance(data, ctx):
    A = matrix(data['A'], square=True)
    n = len(A)
    b = vector(data['b'], n) if data.get('b') else None
    def rows_for(M):
        return [[i + 1, abs(row[i]), sum(abs(x) for j, x in enumerate(row) if j != i),
                 abs(row[i]) > sum(abs(x) for j,x in enumerate(row) if j != i)]
                for i, row in enumerate(M)]
    # Una fila estrictamente dominante solo puede servir en una columna.
    choices = {}
    for i,row in enumerate(A):
        max_j = max(range(n), key=lambda j: abs(row[j]))
        if 2 * abs(row[max_j]) > sum(map(abs,row)):
            choices[max_j] = i
    out = {'dominancia_actual': all(row[-1] for row in rows_for(A)),
           'existe_una_permutacion_dominante': len(choices) == n,
           'encabezados': ['Fila','|aᵢᵢ|','Suma fuera de la diagonal','Domina'], 'tabla': rows_for(A),
           'formula_latex': r'|a_{ii}|>\sum_{j\ne i}|a_{ij}|'}
    for i, diagonal, rest, dominates in out["tabla"]:
        ctx.emit("dominancia",f"Comparar ambas magnitudes en la fila {i}.",{"domina":dominates},
                 f"{diagonal}"+(">" if dominates else r"\le")+str(rest))
    if len(choices) == n:
        order = [choices[j] for j in range(n)]
        out['orden_de_filas'] = [i+1 for i in order]
        out['matriz_reordenada'] = [A[i] for i in order]
        if b is not None:
            out['b_reordenado'] = [b[i] for i in order]
        ctx.emit("permutacion","Colocar cada fila en la posición de su entrada dominante.",
                 {"orden":out["orden_de_filas"],"matriz":out["matriz_reordenada"]})
    return out


def taylor_exp(data):
    x = parse_number(data['x'])
    uncertainty = abs(parse_number(data['delta']))
    count = integer(data['terminos'], 'Términos', 1, 35)
    decimals = integer(data['decimales'], 'Decimales', 0, 18)
    if abs(x) > 30 or uncertainty > 30:
        raise ValueError('Usá x y una incertidumbre dentro de ±30.')
    quantum = Decimal(1).scaleb(-decimals)
    table = []
    with localcontext() as ctx:
        ctx.prec = 65
        point = decimal(x)
        actual = point.exp()
        rounded = Decimal(0)
        for k in range(count):
            term = x**k/factorial(k)
            stored = decimal(term).quantize(quantum, rounding=ROUND_HALF_UP)
            rounded += stored
            table.append([k, str(term), str(stored)])
        truncation = sum(Fraction(row[1]) for row in table)
        lost_terms = actual - decimal(truncation)
        rounding = decimal(truncation) - rounded
        return {'referencia': format(actual,'.32g'), 'serie_truncada_exacta': truncation,
                'serie_redondeada': str(rounded), 'error_truncamiento': format(lost_terms,'.14g'),
                'error_redondeo': format(rounding,'.14g'), 'error_total': format(actual-rounded,'.14g'),
                'incertidumbre_propagada': format(actual*decimal(uncertainty),'.14g'),
                'tabla': table, 'encabezados': ['k','Término exacto','Término guardado'],
                'formula_latex': r'e^x=\sum_{k=0}^{\infty}\frac{x^k}{k!}'}


def accuracy(data):
    values = vector(data['mediciones'])
    if len(values) < 2:
        raise ValueError('Ingresá al menos dos mediciones.')
    reference = parse_number(data['referencia'])
    mean = sum(values)/len(values)
    variance = sum((value-mean)**2 for value in values)/(len(values)-1)
    return {'promedio':mean, 'sesgo':mean-reference, 'sesgo_absoluto':abs(mean-reference),
            'varianza_muestral':variance, 'desviacion_estandar_muestral':str(decimal(variance).sqrt()),
            'formula_latex': r'\bar{x}=\frac{1}{n}\sum_i x_i,\quad s^2=\frac{1}{n-1}\sum_i(x_i-\bar{x})^2'}


def vector_diagram(data):
    u, v = vector(data['u'], 2), vector(data['v'], 2)
    alpha, beta = parse_number(data['alpha']), parse_number(data['beta'])
    scaled_u, scaled_v = [alpha*x for x in u], [beta*x for x in v]
    w = [a+b for a,b in zip(scaled_u,scaled_v)]
    origin = [0,0]
    if any(abs(x) > 10**12 for x in [*scaled_u,*scaled_v,*w]):
        raise ValueError('El gráfico admite coordenadas dentro de ±10¹².')
    diagram = [
        ['αu', origin, list(map(float,scaled_u))],
        ['βv', origin, list(map(float,scaled_v))],
        ['αu + βv', origin, list(map(float,w))],
        ['', list(map(float,scaled_u)), list(map(float,w))],
        ['', list(map(float,scaled_v)), list(map(float,w))],
    ]
    return {'vector_u_escalado':scaled_u, 'vector_v_escalado':scaled_v,
            'vector_resultante':w, 'diagrama_vectores':diagram, 'formula_latex':r'w=\alpha u+\beta v'}
