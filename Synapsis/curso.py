"""Operaciones del temario que complementan el solucionador original."""
import ast
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
from fractions import Fraction
from functools import reduce
from math import factorial, gcd, lcm
import re
import sys

import sympy as sp
from sympy.solvers.solveset import NonlinearError

from nexolineal.algorithms.linear.context import Context, integer, matrix, vector
from nexolineal.algorithms.numerical.functions import Function, decimal
from nexolineal.parsing.numbers import parse_number


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


def from_equations(data, solve):
    variables = symbols(data['variables'])
    A, b = system_data(data['ecuaciones'], variables)
    recipe = [[as_fraction(value) for value in row] for row in A.row_join(b).tolist()]
    result = solve({'matrix': recipe, 'steps': False})
    return {
        'variables': [str(variable) for variable in variables], 'A': rows_text(A),
        'b': rows_text(b), 'matriz_aumentada': rows_text(A.row_join(b)),
        'clasificacion': result['clasificacion'],
        'ecuaciones': [str(lhs) + ' = ' + str(rhs) for lhs, rhs in zip(A*sp.Matrix(variables), b)],
        'rango_A': result['rango_A'], 'rango_aumentada': result['rango_aumentada'],
        'forma_reducida': result['matriz_rref'], 'solucion_particular': result['solucion_particular'],
        'direcciones': result['direcciones'],
    }


def parametric(data):
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
    if det.is_zero:
        result.update(solucion_unica='Ningún valor real del parámetro',
                      criterio='El determinante es idénticamente cero. Para un valor concreto, usá Resolver y clasificar.')
        return result
    exceptional = set(det.real_roots())
    result['valores_singulares_reales'] = [str(root) for root in sorted(exceptional, key=lambda value: value.evalf())]
    formulas = {}
    for i, variable in enumerate(variables):
        replaced = A.copy()
        replaced[:, i] = b
        numerator = replaced.det(method='berkowitz')
        formulas[str(variable)] = str(sp.cancel(numerator / det.as_expr()))
    result['criterio'] = 'Solución única cuando el parámetro es distinto de los valores singulares.'
    result['solucion_por_cramer'] = formulas
    # Los valores algebraicos de grado alto se muestran exactamente como raíces
    # ordenadas sin forzar una reducción simbólica costosa sobre ellos.
    result['casos_singulares'] = {
        str(root): analyze_affine(A.subs(parameter, root), b.subs(parameter, root))
        for root in exceptional if root.is_Rational
    }
    return result


def transformation(data):
    variables = symbols(data['variables'])
    components = [polynomial(line, variables) for line in lines(data['componentes'], 12)]
    zero = {v: 0 for v in variables}
    image_zero = [sp.expand(p).subs(zero) for p in components]
    result = {'T_de_cero': [str(v) for v in image_zero]}
    for i, component in enumerate(components, 1):
        poly = sp.Poly(component, *variables)
        if poly.total_degree() > 1 or poly.TC() != 0:
            result.update(lineal=False, componente=i,
                          motivo='Aparece un término de grado mayor que uno.' if poly.total_degree() > 1 else 'La imagen del cero no es el cero.',
                          formula_latex=rf'T_{{{i}}}=' + sp.latex(component))
            return result
    A = sp.Matrix([[p.coeff(x) for x in variables] for p in components])
    kernel, image = A.nullspace(), A.columnspace()
    result.update(lineal=True, matriz_estandar=rows_text(A),
                  nucleo=[list(map(str,v)) for v in kernel],
                  base_imagen=[list(map(str,v)) for v in image],
                  rango=len(image), nulidad=len(kernel),
                  formula_latex=r'T\left(' + ','.join(map(sp.latex, variables)) + r'\right)=' + sp.latex(sp.Matrix(components)))
    if data.get('v'):
        values = vector(data['v'], len(variables))
        result['T_de_v'] = [str(entry) for entry in A * sp.Matrix(values)]
    return result


def subspace(data):
    variables = symbols(data['variables'])
    A, b = system_data(data['ecuaciones'], variables)
    affine = analyze_affine(A, b)
    basis = A.nullspace()
    homogeneous = not any(b)
    result = dict(affine, es_subespacio=homogeneous, contiene_cero=homogeneous,
                  formula_latex=r'H=\{x\mid Ax=b\}', A=rows_text(A), b=rows_text(b))
    if homogeneous:
        result.update(cerrado_bajo_suma=True, cerrado_bajo_producto_escalar=True,
                      base=[list(map(str, value)) for value in basis], dimension=len(basis),
                      justificacion='Si Au=Av=0, entonces A(αu+βv)=αAu+βAv=0.')
    else:
        result['justificacion'] = 'El vector cero no satisface una o más ecuaciones.' if affine['rango_A'] == affine['rango_aumentada'] else 'El conjunto es vacío.'
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
    from nexolineal.algorithms.linear.spaces import study, membership
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
    from nexolineal.algorithms.linear.context import tex
    context.emit('posicion', f'Ir a la fila {i+1} y columna {j+1}.', {'fila': A[i], 'columna': [r[j] for r in A]})
    return {'orden': f'{m} × {n}', 'entrada': value, 'fila': A[i],
            'columna': [[r[j]] for r in A], 'diagonal': [A[k][k] for k in range(min(m,n))],
            'formula_latex': rf'a_{{{i+1},{j+1}}}={tex(value)}'}


def matrix_compare(data, context):
    from nexolineal.algorithms.linear.context import multiply
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
    from nexolineal.algorithms.linear.matrix import determinant, invert
    A = matrix(data['A'], square=True)
    n = len(A)
    determinant_value = determinant(A, context, 'reduccion')
    # La forma reducida permite explicar todos los criterios equivalentes.
    from nexolineal.algorithms.linear.reduction import reduce as row_reduce
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
    if value:
        out['inversa'], _ = invert(A, context)
    return out


def economy(data):
    M = matrix(data['A'], square=True)
    n = len(M)
    scale = 100 if data['unidades'] == 'porcentaje' else 1
    if any(value < 0 for row in M for value in row):
        raise ValueError('Las participaciones deben ser no negativas.')
    A = [[entry / scale for entry in row] for row in M]
    for i in range(n):
        total = sum(A[j][i] for j in range(n) if i != j)
        if total > 1:
            raise ValueError(f'Las ventas de la columna {i+1} superan el total de su producción.')
        A[i][i] = 1 - total
    C = sp.eye(n) - sp.Matrix(A)
    b = sp.zeros(n, 1)
    if data.get('precio'):
        index = integer(data['sector'], 'Sector de referencia', 1, n) - 1
        fixed = parse_number(data['precio'])
        if fixed <= 0:
            raise ValueError('El precio fijado debe ser positivo.')
        C = C.col_join(sp.eye(n)[index,:])
        b = b.col_join(sp.Matrix([fixed]))
    return {'tabla_intercambio': A, 'modelo': rows_text(C.row_join(b)),
            'equilibrio': analyze_affine(C,b), 'formula_latex': r'(I-M)p=0'}


def balance(data):
    A = matrix(data['A'])
    if any(x.denominator != 1 for row in A for x in row):
        raise ValueError('La matriz de átomos debe contener cantidades enteras con signo.')
    S = sp.Matrix(A)
    basis = S.nullspace()
    out = {'matriz_de_balance': A, 'dimension_del_nucleo': len(basis),
           'generadores': [list(map(str, v)) for v in basis], 'formula_latex': r'Ac=0'}
    if len(basis) == 1:
        row = [int(v*lcm(*(int(w.q) for w in basis[0]))) for v in basis[0]]
        primitive = [v // reduce(gcd, row) for v in row]
        if all(v < 0 for v in primitive):
            primitive = [-v for v in primitive]
        if all(v > 0 for v in primitive):
            out['coeficientes_enteros_minimos'] = primitive
        else:
            out['conclusion'] = 'No se obtuvo un balance que incluya todos los compuestos con coeficientes positivos.'
    elif not basis:
        out['conclusion'] = 'Solo existe la solución trivial.'
    else:
        out['conclusion'] = 'El balance tiene varios parámetros. Elegí una combinación de los generadores con coeficientes enteros positivos.'
    return out


def nonnegative(data):
    A = matrix(data['A'])
    b = vector(data['b'], len(A))
    S, d = sp.Matrix(A), sp.Matrix(b)
    if S.cols > 8:
        raise ValueError('Este análisis admite hasta 8 variables de flujo.')
    out = analyze_affine(S,d)
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
    return {'truncado': display(truncated), 'redondeado': display(rounded),
            'error_de_truncamiento': exact - Fraction(sign*truncated, scale),
            'error_de_redondeo': exact - Fraction(sign*rounded, scale),
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
            'formula_latex': r'\sqrt{a+b}-\sqrt{a-b}=\frac{2b}{\sqrt{a+b}+\sqrt{a-b}}'}


def dominance(data):
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
    if len(choices) == n:
        order = [choices[j] for j in range(n)]
        out['orden_de_filas'] = [i+1 for i in order]
        out['matriz_reordenada'] = [A[i] for i in order]
        if b is not None:
            out['b_reordenado'] = [b[i] for i in order]
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
