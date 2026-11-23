"""Operaciones de Cálculo I con condiciones y trazas sobre expresiones verificadas."""
import ast
from fractions import Fraction
from math import isfinite

import sympy as sp

from curso import polynomial
from motor_matematico.algorithms.calculo import analizar, ejecutar_calculo
from motor_matematico.algorithms.numerical.symbolic import symbolic_expression
from motor_matematico.domain.models import DomainError
from motor_matematico.parsing.numbers import parse_number

X, Y = sp.symbols("x y", real=True)
R = sp.S.Reals


def exact(text):
    return sp.Rational(parse_number(text))


def interval(data):
    a, b = exact(data["inferior"]), exact(data["superior"])
    if not a < b:
        raise ValueError("El extremo inferior debe ser menor que el superior.")
    return a, b, sp.Interval(a, b)


def emit(ctx, message, *parts, **evidence):
    ctx.emit("calculo_i", message, evidence, "".join(parts))


def condition_set(value, variable, relation):
    if value.has(sp.zoo, sp.nan, sp.I):
        return sp.EmptySet
    try:
        if relation == "no_cero":
            allowed = R - sp.solveset(value, variable, domain=R)
        elif relation == "entre_menos_uno_y_uno":
            allowed = condition_set(1-value, variable, "no_negativo") & condition_set(1+value, variable, "no_negativo")
        else:
            predicate = value >= 0 if relation == "no_negativo" else value > 0
            if predicate in (sp.S.true, sp.S.false):
                allowed = R if predicate else sp.EmptySet
            else:
                allowed = sp.solve_univariate_inequality(predicate, variable, relational=False)
    except (NotImplementedError, TypeError) as error:
        raise DomainError("No se pudo determinar exactamente el dominio de esa restricción.") from error
    if allowed.has(sp.ConditionSet):
        raise DomainError("No se pudo determinar exactamente el dominio de esa restricción.")
    return allowed


def function(source, ctx, argument=X):
    tree = analizar(source, variable=True)
    domain = R
    restrictions = []
    def collect(node, expression):
        nonlocal domain
        requirements = []
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            requirements.append((expression.args[1].base, "no_cero"))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            base, exponent = expression.as_base_exp()
            exponent = sp.cancel(exponent)
            if exponent.is_Integer and exponent < 0:
                requirements.append((base, "no_cero"))
            elif exponent.is_Rational and not exponent.is_Integer:
                requirements.append((base, "positivo" if exponent < 0 else "no_negativo"))
            elif not exponent.is_Integer:
                requirements.append((base, "positivo"))
        if isinstance(node, ast.Call):
            name = node.func.id
            arg = symbolic_expression(node.args[0], ctx, argument)
            if name == "sqrt":
                requirements.append((arg, "no_negativo"))
            elif name in ("ln", "log"):
                requirements.append((arg, "positivo"))
            elif name in ("asin", "acos"):
                requirements.append((arg, "entre_menos_uno_y_uno"))
            elif name == "tan":
                requirements.append((sp.cos(arg), "no_cero"))
            elif name == "factorial":
                raise DomainError("El factorial se reserva para cálculos discretos.")
        for value, relation in requirements:
            allowed = condition_set(value, X, relation)
            domain &= allowed
            restrictions.append({"expresion": str(value), "condicion": relation, "conjunto": str(allowed)})

    result = symbolic_expression(tree, ctx, argument, check=collect)
    return result, domain, restrictions


def at(expression, point, domain):
    if domain.contains(point) != sp.S.true:
        raise DomainError("El punto está fuera del dominio de la función.")
    return sp.simplify(expression.subs(X, point))


def require_interval(domain, region):
    if region.is_subset(domain) is not True:
        raise DomainError("El intervalo debe estar contenido en el dominio real de la función.")


def domain(data, ctx):
    _, allowed, restrictions = function(data["expresion"], ctx)
    for restriction in restrictions:
        emit(ctx, "Aplicar la restricción de la expresión original.", **restriction)
    emit(ctx, "Intersecar las restricciones para obtener el dominio real.", sp.latex(allowed))
    return {"dominio": str(allowed), "restricciones": restrictions, "formula_latex": r"D_f=" + sp.latex(allowed)}


def composition(data, ctx):
    inner, inner_domain, _ = function(data["interior"], ctx)
    composed, outer_domain, restrictions = function(data["exterior"], ctx, inner)
    allowed = inner_domain & outer_domain
    emit(ctx, "Sustituir g(x) como argumento en la función exterior.", r"f(g(x))=", sp.latex(composed),
         interior=str(inner), exterior=data["exterior"])
    emit(ctx, "Exigir que x pertenezca al dominio interior y que g(x) pertenezca al dominio exterior.",
         sp.latex(allowed), dominio_interior=str(inner_domain), restricciones_exterior=restrictions)
    result = {"composicion": str(sp.simplify(composed)), "dominio": str(allowed)}
    if data.get("punto"):
        result["valor"] = str(at(composed, exact(data["punto"]), allowed))
    return result


def inverse(data, ctx):
    a, b, region = interval(data)
    source = polynomial(data["expresion"], (X,))
    degree = sp.degree(source, X)
    if degree not in (1, 2):
        raise ValueError("Ingresá una función afín no constante o una cuadrática.")
    if degree == 1:
        slope = source.coeff(X)
        branch = (Y-source.subs(X, 0))/slope
        proof = "La pendiente constante distinta de cero hace inyectiva la función."
        branch_condition = sp.S.true
    else:
        p = source.coeff(X, 2)
        vertex = -source.coeff(X, 1)/(2*p)
        if a < vertex < b:
            raise DomainError("El intervalo cruza el vértice. Elegí una sola rama inyectiva.")
        side = 1 if a >= vertex else -1
        branch = vertex + side*sp.sqrt((Y-source.subs(X, vertex))/p)
        branch_condition = X >= vertex if side == 1 else X <= vertex
        proof = "Se conserva la rama creciente o decreciente que queda de un solo lado del vértice."
    image = sorted([source.subs(X, a), source.subs(X, b)])
    emit(ctx, proof, r"f^{-1}(y)=", sp.latex(branch), intervalo=str(region), rama=str(branch_condition))
    forward = sp.simplify(source.subs(X, branch))
    backward = sp.simplify(branch.subs(Y, source))
    if degree == 2:
        radicand = sp.cancel((source-source.subs(X,vertex))/p)
        if sp.expand(radicand-(X-vertex)**2) != 0:
            raise DomainError("No se pudo comprobar el cuadrado de la rama.")
        # En esta rama |x-vértice| = lado por (x-vértice).
        backward = sp.simplify(vertex + side*(side*(X-vertex)))
    if forward != Y or sp.simplify(backward-X) != 0:
        raise DomainError("No se pudieron comprobar ambas composiciones sobre la rama.")
    emit(ctx, "Sustituir la rama en f y usar la condición del intervalo para la composición inversa.",
         r"f(f^{-1}(y))=", sp.latex(forward), r",\qquad f^{-1}(f(x))=", sp.latex(backward),
         paso_de_rama=r"\sqrt{(x-h)^2}=|x-h|" if degree == 2 else "Despeje lineal.")
    return {"inversa": str(branch), "dominio_inversa": str(sp.Interval(*image)),
            "rango_inversa": str(region), "formula_latex": r"f^{-1}(y)=" + sp.latex(branch)}


def approach(source, point, side, ctx):
    expression, allowed, _ = function(source, ctx)
    # Una aproximación unilateral exige un tramo del dominio adyacente al punto.
    direction = sp.Interval.open(-sp.oo, point) if side == "-" else sp.Interval.open(point, sp.oo)
    side_domain = allowed & direction
    if side_domain == sp.EmptySet:
        return None
    try:
        approaches = side_domain.closure.contains(point) == sp.S.true
    except NotImplementedError:
        # A real line with a finite set removed is still dense near the point.
        approaches = (isinstance(allowed, sp.Complement) and allowed.args[0] == R
                      and allowed.args[1].is_finite_set is True)
    if not approaches:
        return None
    try:
        result = sp.limit(expression, X, point, dir=side)
    except NotImplementedError:
        return None
    return None if result.has(sp.Limit, sp.AccumBounds, sp.nan, sp.zoo, sp.I) else result


def one_sided(data, ctx):
    point = exact(data["punto"])
    left = data["expresion"]
    right = data.get("derecha") or left
    values = {side: approach(source, point, side, ctx)
              for side, source in (("-", left), ("+", right))}
    for side, value in values.items():
        emit(ctx, "Evaluar la aproximación por este lado.",
             rf"\lim_{{x\to {sp.latex(point)}^{{{side}}}}}",
             "=" + sp.latex(value) if value is not None else r"\text{ sin límite lateral verificado}",
             lado=side, limite=str(value) if value is not None else None)
    equal = values["-"] is not None and values["-"] == values["+"]
    chosen = data["lado"]
    if chosen not in ("-", "+", "ambos"):
        raise ValueError("Elegí izquierda, derecha o ambos lados.")
    limit_value = values[chosen] if chosen != "ambos" else values["-"] if equal else None
    emit(ctx, "Comparar las dos aproximaciones para decidir si coinciden.", coincide=equal,
         limite_bilateral=str(values["-"]) if equal else None)
    return {"limite": str(limit_value) if limit_value is not None else None,
            "izquierda": str(values["-"]) if values["-"] is not None else None,
            "derecha": str(values["+"]) if values["+"] is not None else None,
            "limite_bilateral": str(values["-"]) if equal else None}


def continuity(data, ctx):
    result = one_sided({**data, "lado": "ambos"}, ctx)
    point = exact(data["punto"])
    f, allowed, _ = function(data["expresion"], ctx)
    right = data.get("derecha")
    value = None
    if data.get("valor_punto"):
        value = exact(data["valor_punto"])
    elif not right and allowed.contains(point) == sp.S.true:
        value = at(f, point, allowed)
    agreed = value is not None and value.is_finite is True and result["limite_bilateral"] == str(value)
    emit(ctx, "La continuidad exige que el límite bilateral finito coincida con el valor de la función.",
         continua=agreed, valor=str(value) if value is not None else None)
    output = {**result, "continua": agreed, "valor_en_el_punto": str(value) if value is not None else None}
    if abs(point) <= 10**8:
        g, right_domain, _ = function(right, ctx) if right else (f, allowed, [])
        graph = []
        def ordinate(expression, argument):
            evaluated = expression.subs(X, argument).evalf()
            number = float(evaluated) if evaluated.is_real else None
            return number if number is not None and isfinite(number) and abs(number) < 10**90 else None
        for index in range(-60,61):
            sample = point + sp.Rational(index,30)
            expression, supported = (f,allowed) if index < 0 else (g,right_domain)
            y = ordinate(expression, sample) if index and supported.contains(sample) == sp.S.true else None
            graph.append([float(sample),y])
        marker = ordinate(value, point) if value is not None else None
        if any(y is not None for _,y in graph) or marker is not None:
            output["series"] = {"points":graph,"markers":[[float(point),marker]] if marker is not None else [],
                                "caption":"Aproximación gráfica a ambos lados y valor en el punto"}
    return output


def factoring(data, ctx):
    point = exact(data["punto"])
    tree = analizar(data["expresion"], variable=True)
    if not isinstance(tree, ast.BinOp) or not isinstance(tree.op, ast.Div):
        raise ValueError("Ingresá un cociente de polinomios para factorizar.")
    numerator = polynomial(ast.unparse(tree.left), (X,))
    denominator = polynomial(ast.unparse(tree.right), (X,))
    if not denominator or numerator.subs(X, point) != 0 or denominator.subs(X, point) != 0:
        raise ValueError("En el punto indicado se requiere una indeterminación 0/0.")
    cancellation = sp.cancel(numerator / denominator)
    emit(ctx, "Factorizar numerador y denominador.", sp.latex(sp.factor(numerator)),
         r",\quad ", sp.latex(sp.factor(denominator)))
    emit(ctx, "Cancelar los factores comunes exclusivamente donde el denominador original es distinto de cero.",
         sp.latex(cancellation), exclusiones=str(sp.solveset(denominator, X, domain=R)))
    return one_sided({**data, "lado": "ambos"}, ctx)


def rationalizing(data, ctx):
    point = exact(data["punto"])
    tree = analizar(data["expresion"], variable=True)
    if not isinstance(tree, ast.BinOp) or not isinstance(tree.op, ast.Div):
        raise ValueError("Ingresá un cociente con diferencia de radicales en el numerador.")
    numerator = tree.left
    if not (isinstance(numerator, ast.BinOp) and isinstance(numerator.op, ast.Sub)
            and isinstance(numerator.left, ast.Call) and numerator.left.func.id == "sqrt"):
        raise ValueError("Usá un numerador de la forma sqrt(u)-v.")
    u, _d, _ = function(ast.unparse(numerator.left.args[0]), ctx)
    v, _d, _ = function(ast.unparse(numerator.right), ctx)
    d, _d, _ = function(ast.unparse(tree.right), ctx)
    if d == 0 or d.subs(X, point) != 0 or sp.simplify(sp.sqrt(u.subs(X, point))-v.subs(X, point)) != 0:
        raise ValueError("En el punto indicado se requiere una indeterminación 0/0.")
    conjugate = sp.sqrt(u) + v
    if conjugate == 0:
        raise ValueError("El conjugado es idénticamente cero.")
    transformed = sp.cancel((u-v**2)/d)/conjugate
    emit(ctx, "Multiplicar numerador y denominador por el conjugado donde no se anula.",
         sp.latex(conjugate), punto=str(point))
    emit(ctx, "Usar diferencia de cuadrados y conservar el dominio original.",
         sp.latex(transformed), reduccion=str(transformed))
    return one_sided({**data, "lado": "ambos"}, ctx)


def infinite_limit(data, ctx):
    point = exact(data["punto"])
    side = data["lado"]
    f, _, _ = function(data["expresion"], ctx)
    num, den = sp.cancel(f).as_numer_denom()
    if num.is_polynomial(X) and den.is_polynomial(X) and den.subs(X, point) == 0:
        factor = sp.Poly(X-point, X)
        reduced = sp.Poly(den, X)
        order = 0
        while reduced.eval(point) == 0:
            reduced = reduced.exquo(factor)
            order += 1
        coefficient = sp.simplify(num.subs(X,point)/reduced.eval(point))
        emit(ctx, "Extraer del denominador la potencia que se anula y evaluar el factor restante.",
             rf"f(x)\sim\frac{{{sp.latex(coefficient)}}}{{(x-({sp.latex(point)}))^{{{order}}}}}",
             orden_del_polo=order, signo_del_factor=str(sp.sign(coefficient)),
             signo_izquierdo=str(sp.sign(coefficient)*(-1)**order), signo_derecho=str(sp.sign(coefficient)))
    result = one_sided(data, ctx)
    emit(ctx, "Un límite infinito describe el crecimiento sin cota en el lado seleccionado.",
         lado=side, limite=result["limite"])
    return result


def infinity_limit(data, ctx):
    source = data["expresion"]
    f, allowed, _ = function(source, ctx)
    if data["lado"] not in ("+", "-"):
        raise ValueError("Elegí un sentido hacia el infinito.")
    target = sp.oo if data["lado"] == "+" else -sp.oo
    if allowed == sp.EmptySet or target != (allowed.sup if target == sp.oo else allowed.inf):
        raise DomainError("El dominio no se extiende hacia ese infinito.")
    num, den = sp.cancel(f).as_numer_denom()
    if not (num.is_polynomial(X) and den.is_polynomial(X)):
        raise ValueError("Usá un cociente de polinomios para comparar sus términos dominantes.")
    top, bottom = sp.Poly(num, X), sp.Poly(den, X)
    degree = bottom.degree()
    scaled = 0 if top.is_zero else top.LC()/bottom.LC()*X**(top.degree()-degree)
    emit(ctx, "Dividir por la mayor potencia del denominador y comparar los términos dominantes.",
         sp.latex(scaled), grado_denominador=int(degree),
         grado_numerador=None if top.is_zero else int(top.degree()))
    value = sp.limit(f, X, target)
    formula = rf"\lim_{{x\to {sp.latex(target)}}}f(x)={sp.latex(value)}"
    emit(ctx, "Evaluar los términos que permanecen al alejarnos.", formula)
    return {"limite": str(value), "formula_latex": formula}


def by_definition(data, ctx):
    source = polynomial(data["expresion"], (X,))
    h = sp.Symbol("h", real=True)
    difference = sp.expand(source.subs(X, X+h)-source)
    emit(ctx, "Sustituir x+h y restar f(x).", r"f(x+h)-f(x)=", sp.latex(difference))
    quotient = sp.cancel(difference/h)
    emit(ctx, "Cancelar h para incrementos distintos de cero.", sp.latex(quotient), condicion="h ≠ 0")
    value = sp.limit(quotient, h, 0)
    formula = r"f'(x)=\lim_{h\to0}" + sp.latex(quotient) + "=" + sp.latex(value)
    emit(ctx, "Tomar el límite del cociente incremental simplificado.", formula)
    return {"derivada": str(value), "formula_latex": formula}


def derivative_rule(data, ctx, rule):
    f, allowed, _ = function(data["expresion"], ctx)
    tree = analizar(data["expresion"], variable=True)
    if rule in ("producto", "cociente"):
        required = ast.Mult if rule == "producto" else ast.Div
        if not isinstance(tree, ast.BinOp) or not isinstance(tree.op, required):
            raise ValueError(f"Ingresá un {rule} de dos funciones.")
        u = symbolic_expression(tree.left, ctx, X)
        v = symbolic_expression(tree.right, ctx, X)
        du, dv = sp.diff(u, X), sp.diff(v, X)
        rule_tex = r"(uv)'=u'v+uv'" if rule == "producto" else r"(u/v)'=\frac{u'v-uv'}{v^2}"
        emit(ctx, "Separar ambos operandos y derivarlos por separado.",
             rf"u={sp.latex(u)},\;v={sp.latex(v)},\;u'={sp.latex(du)},\;v'={sp.latex(dv)}")
        substitution = (rf"\left({sp.latex(du)}\right)\left({sp.latex(v)}\right)"
                        rf"+\left({sp.latex(u)}\right)\left({sp.latex(dv)}\right)")
        if rule == "cociente":
            substitution = (rf"\frac{{\left({sp.latex(du)}\right)\left({sp.latex(v)}\right)"
                            rf"-\left({sp.latex(u)}\right)\left({sp.latex(dv)}\right)}}"
                            rf"{{\left({sp.latex(v)}\right)^2}}")
        emit(ctx, "Sustituir en la regla conservando el dominio de la entrada.",
             rule_tex + r",\qquad f'(x)=" + substitution, dominio=str(allowed))
    else:
        if isinstance(tree, ast.Call):
            name = tree.func.id
            variant = {"exp": "exponencial", "ln": "logaritmica", "log": "logaritmica",
                       "sin": "trigonometrica", "cos": "trigonometrica", "tan": "trigonometrica",
                       "asin": "trigonometrica", "acos": "trigonometrica", "atan": "trigonometrica"}.get(name)
            inner = symbolic_expression(tree.args[0], ctx, X)
            slot = sp.Symbol("u", real=True)
            arg_node = ast.Call(func=tree.func, args=[ast.Name(id="x")], keywords=[])
            outer = symbolic_expression(arg_node, ctx, slot)
        elif isinstance(tree, ast.BinOp) and isinstance(tree.op, ast.Pow):
            slot = sp.Symbol("u", real=True)
            base = symbolic_expression(tree.left, ctx, X)
            exponent = sp.cancel(symbolic_expression(tree.right, ctx, X))
            if exponent.is_number:
                inner, outer, variant = base, slot**exponent, "cadena"
            elif base.is_number and base.is_positive:
                inner, outer, variant = exponent, base**slot, "exponencial"
            else:
                raise ValueError("Usá una potencia de exponente constante o una exponencial de base positiva constante.")
        else:
            raise ValueError("Ingresá una potencia compuesta o la función elemental indicada.")
        if rule != "cadena" and rule != variant:
            raise ValueError("Elegí una expresión de la familia de la regla indicada.")
        slope = sp.diff(outer, slot)
        inner_slope = sp.diff(inner, X)
        emit(ctx, "Identificar la función interior y la exterior.",
             rf"u={sp.latex(inner)},\quad f=F(u),\quad F(u)={sp.latex(outer)}")
        emit(ctx, "Derivar la función interior y la exterior.",
             rf"u'={sp.latex(inner_slope)},\quad F'(u)={sp.latex(slope)}")
        emit(ctx, "Sustituir la función interior en la derivada exterior y multiplicar.",
             rf"f'(x)=\left({sp.latex(slope.subs(slot,inner))}\right)\left({sp.latex(inner_slope)}\right)",
             dominio=str(allowed))
    result = sp.simplify(sp.diff(f, X))
    formula = "f'(x)=" + sp.latex(result)
    emit(ctx, "Simplificar el resultado de la regla.", formula)
    return {"derivada": str(result), "dominio_funcion": str(allowed), "formula_latex": formula}


def implicit(data, ctx):
    lhs = polynomial(data["izquierda"], (X,Y))
    rhs = polynomial(data["derecha"], (X,Y))
    derivative = sp.Symbol("y'")
    left_diff = sp.diff(lhs,X) + sp.diff(lhs,Y)*derivative
    right_diff = sp.diff(rhs,X) + sp.diff(rhs,Y)*derivative
    coefficient = sp.diff(lhs-rhs,Y)
    emit(ctx, "Derivar ambos miembros tratando y como función de x.",
         sp.latex(left_diff), "=", sp.latex(right_diff))
    if coefficient == 0:
        emit(ctx, "La ecuación no permite despejar y′ mediante una división.")
        return {"derivada": None, "condicion": "El coeficiente de y′ es idénticamente cero."}
    solution = sp.cancel(-sp.diff(lhs-rhs,X)/coefficient)
    formula = rf"y'={sp.latex(solution)},\quad {sp.latex(coefficient)}\ne0"
    emit(ctx, "Aislar y′ donde su coeficiente es distinto de cero.", formula)
    return {"derivada": str(solution), "condicion": str(sp.Ne(coefficient,0)), "formula_latex": formula}


def successive(data, ctx):
    source = polynomial(data["expresion"], (X,Y))
    variables = data["orden"].replace(",", " ").split()
    if not 1 <= len(variables) <= 5 or any(v not in ("x","y") for v in variables):
        raise ValueError("Ingresá de una a cinco variables x o y en el orden en que se deriva.")
    for variable in variables:
        active, constant = (X,Y) if variable == "x" else (Y,X)
        result = sp.diff(source, active)
        emit(ctx, f"Derivar respecto de {active} manteniendo {constant} constante.",
             rf"\frac{{\partial}}{{\partial {active}}}\left({sp.latex(source)}\right)={sp.latex(result)}")
        source = result
    return {"orden_derivacion": variables, "derivada": str(source), "formula_latex": sp.latex(source)}


def finite_roots(expression, domain=R):
    roots = sp.solveset(expression, X, domain=domain)
    if not isinstance(roots, sp.FiniteSet) and roots != sp.EmptySet:
        raise DomainError("Se requiere un conjunto finito de raíces que se pueda verificar exactamente.")
    return roots


def derivative_domain(f, allowed):
    derivative = sp.simplify(sp.diff(f, X))
    derivative_allowed = allowed.interior
    for term in sp.preorder_traversal(derivative):
        if term.func == sp.sign:
            derivative_allowed &= condition_set(term.args[0], X, "no_cero")
        if term.is_Pow and term.exp.is_Rational:
            if term.exp < 0:
                derivative_allowed &= condition_set(term.base, X, "no_cero")
            if term.exp.q != 1:
                derivative_allowed &= condition_set(term.base, X, "positivo" if term.exp < 0 else "no_negativo")
    return derivative, derivative_allowed


def critical_values(f, allowed):
    derivative, regular = derivative_domain(f, allowed)
    stationary = regular if derivative == 0 else sp.solveset(derivative, X, domain=regular)
    if stationary.has(sp.ConditionSet):
        raise DomainError("No se pudieron determinar exactamente los ceros de la derivada.")
    singular = allowed - regular
    candidates = singular & allowed.interior
    if isinstance(candidates, sp.FiniteSet):
        for point in candidates:
            difference = (f - f.subs(X,point))/(X-point)
            try:
                slopes = [sp.limit(difference,X,point,dir=side) for side in ("-","+")]
            except NotImplementedError as error:
                raise DomainError("No se pudo verificar la existencia de la derivada en ese punto.") from error
            if slopes[0].is_finite is True and slopes[0] == slopes[1]:
                singular -= sp.FiniteSet(point)
                if slopes[0] == 0:
                    stationary |= sp.FiniteSet(point)
    return stationary | singular, derivative, singular


def critical(data, ctx):
    f, allowed, _ = function(data["expresion"], ctx)
    values, derivative, singular = critical_values(f, allowed)
    emit(ctx, "Encontrar los ceros de la derivada que pertenecen al dominio.",
         "f'(x)=" + sp.latex(derivative), dominio=str(allowed))
    emit(ctx, "Incluir dónde no existe la derivada bilateral dentro del dominio.",
         sp.latex(values), derivada_inexistente=str(singular))
    return {"numeros_criticos": str(values), "formula_latex": sp.latex(values)}


def midpoint(left, right):
    if left == -sp.oo:
        return right-1 if right != sp.oo else sp.Integer(0)
    return left+1 if right == sp.oo else (left+right)/2


def signs(data, ctx):
    f = polynomial(data["expresion"], (X,))
    derivative = sp.diff(f,X)
    second = sp.diff(derivative,X)
    breaks = set(finite_roots(derivative)) if derivative else set()
    if second:
        breaks.update(finite_roots(second))
    bounds = [-sp.oo, *sorted(breaks), sp.oo]
    rows, inflections, prior = [], [], None
    for left,right in zip(bounds,bounds[1:]):
        sample = midpoint(left,right)
        slope, bend = sp.sign(derivative.subs(X,sample)), sp.sign(second.subs(X,sample))
        if prior is not None and prior * bend < 0:
            inflections.append(str(left))
        region = sp.Interval.open(left,right)
        rows.append([str(region), str(sample), str(slope), str(bend),
                     {1:"Creciente",0:"Constante",-1:"Decreciente"}[slope],
                     {1:"Hacia arriba",0:"Nula",-1:"Hacia abajo"}[bend]])
        emit(ctx, "Evaluar los signos entre ceros consecutivos de las derivadas.",
             sp.latex(region), muestra=str(sample), signo_primera=str(slope), signo_segunda=str(bend))
        prior = bend
    return {"tabla": rows, "encabezados": ["Intervalo","Muestra","Signo f′","Signo f″","Variación","Concavidad"],
            "inflexiones":inflections}


def optimization(data, ctx):
    a,b,region = interval(data)
    f, allowed, _ = function(data["expresion"],ctx)
    require_interval(allowed,region)
    mode = data["entrega"]
    if mode not in ("plantear","resolver"):
        raise ValueError("Elegí plantear o resolver.")
    formula = rf"\min_{{x\in {sp.latex(region)}}} f(x),\quad\max_{{x\in {sp.latex(region)}}} f(x)"
    emit(ctx, "Definir la función objetivo y el intervalo cerrado factible.", formula, objetivo=str(f))
    if mode == "plantear":
        return {"objetivo":str(f),"intervalo":str(region),"formula_latex":formula}
    derivative = sp.diff(f,X)
    if derivative == 0:
        value = str(at(f,a,allowed))
        emit(ctx, "La función es constante. Cada punto del intervalo alcanza ambos extremos.",
             sp.latex(f))
        return {"minimo":value,"maximo":value,"puntos_minimo":str(region),"puntos_maximo":str(region)}
    critical_set,_,_ = critical_values(f, allowed)
    interior = critical_set & sp.Interval.open(a,b)
    if interior != sp.EmptySet and not isinstance(interior, sp.FiniteSet):
        raise DomainError("La comparación requiere un conjunto finito de candidatos interiores.")
    points = sorted({a,b,*interior})
    values = [(p,at(f,p,allowed)) for p in points]
    low,high = min(v for _,v in values), max(v for _,v in values)
    emit(ctx, "Comparar el valor de la función en los números críticos interiores y en los dos extremos.",
         minimo=str(low), maximo=str(high))
    return {"tabla":[[str(p),str(v)] for p,v in values],"encabezados":["Candidato","f(x)"],
            "minimo":str(low),"maximo":str(high),
            "puntos_minimo":[str(p) for p,v in values if v == low],
            "puntos_maximo":[str(p) for p,v in values if v == high]}


def hessian(data, ctx):
    f = polynomial(data["expresion"], (X,Y))
    point = {X:exact(data["x"]),Y:exact(data["y"])}
    gradient = [sp.diff(f,var).subs(point) for var in (X,Y)]
    emit(ctx, "Evaluar ambas derivadas parciales para verificar si el punto es crítico.",
         r"\nabla f=" + sp.latex(tuple(gradient)))
    if any(gradient):
        return {"critico":False,"clasificacion":"El gradiente no se anula en el punto."}
    H = sp.hessian(f,(X,Y)).subs(point)
    determinant = H.det()
    if determinant < 0:
        classification = "Punto silla"
    elif determinant == 0:
        classification = "Prueba inconclusa"
    else:
        classification = "Mínimo local" if H[0,0]>0 else "Máximo local"
    emit(ctx, "Clasificar con el determinante hessiano y, si es positivo, con la segunda parcial en x.",
         r"D=f_{xx}f_{yy}-f_{xy}^2=" + sp.latex(determinant),
         f_xx=str(H[0,0]),clasificacion=classification)
    return {"critico":True,"clasificacion":classification,
            "hessiano":[list(map(str,row)) for row in H.tolist()],"determinante":str(determinant)}


def rate(data, ctx, method):
    f, allowed, _ = function(data["expresion"], ctx)
    unit_in, unit_out = data.get("unidad_x","unidad de x"), data.get("unidad_y","unidad de f")
    if method == "media":
        a,b,region = interval(data)
        require_interval(allowed, region)
        v1,v2 = at(f,a,allowed),at(f,b,allowed)
        number = sp.simplify((v2-v1)/(b-a))
        tex = rf"\frac{{{sp.latex(v2)}-({sp.latex(v1)})}}{{{sp.latex(b)}-({sp.latex(a)})}}"
        output_unit = unit_out + " por " + unit_in
        interpretation = "Cambio promedio de f por cada unidad de x en el intervalo."
    else:
        x = exact(data["punto"])
        value = at(f,x,allowed)
        derivative, regular = derivative_domain(f,allowed)
        slope = at(derivative,x,regular)
        if method == "instantanea":
            number,tex = slope, rf"f'({sp.latex(x)})"
            output_unit = unit_out + " por " + unit_in
            interpretation = "Ritmo de cambio local de f respecto de x en el punto."
        else:
            if x == 0 or value == 0:
                raise DomainError("La elasticidad requiere que x y f(x) sean distintos de cero.")
            number = sp.simplify(x*slope/value)
            tex = rf"\frac{{({sp.latex(x)})({sp.latex(slope)})}}{{{sp.latex(value)}}}"
            output_unit = "Sin unidades"
            interpretation = "Cambio porcentual aproximado de f ante un aumento de 1 % en x. El signo indica el sentido."
    emit(ctx, "Identificar la variable, calcular la razón y expresar sus unidades.",
         tex, "=" + sp.latex(number), unidades=output_unit)
    return {"valor":str(number),"unidades":output_unit,"interpretacion":interpretation}


def related(data, ctx):
    relation = polynomial(data["expresion"], (X,Y))
    point = {X:exact(data["x"]),Y:exact(data["y"])}
    if relation.subs(point) != 0:
        raise DomainError("El punto debe satisfacer la relación igualada a cero.")
    fx,fy = (sp.diff(relation,var).subs(point) for var in (X,Y))
    if fy == 0:
        raise DomainError("No se puede despejar la tasa de y porque F_y se anula en el punto.")
    dx = exact(data["tasa_x"])
    dy = -fx*dx/fy
    emit(ctx, "Derivar F(x(t), y(t))=0 por la regla de la cadena.",
         r"F_x\,\frac{dx}{dt}+F_y\,\frac{dy}{dt}=0", F_x=str(fx),F_y=str(fy))
    emit(ctx, "Sustituir el punto y despejar la tasa de y.",
         r"\frac{dy}{dt}=" + sp.latex(dy), tasa_x=str(dx))
    return {"valor":str(dy), "unidades":data.get("unidad_y","unidad de y")+" por "+data.get("unidad_t","unidad de tiempo"),
            "interpretacion":"Signo positivo indica aumento de y. Signo negativo indica disminución."}


def theorem(data, ctx, method):
    a,b,region = interval(data)
    f,allowed,_ = function(data["expresion"],ctx)
    continuous = region.is_subset(allowed) is True
    derivative,regular = derivative_domain(f,allowed)
    differentiable = sp.Interval.open(a,b).is_subset(regular) is True
    emit(ctx, "Verificar continuidad en el intervalo cerrado a partir del dominio real.",
         intervalo=str(region), dominio=str(allowed), continua=continuous)
    ends = [at(f,p,allowed) if allowed.contains(p) == sp.S.true else None for p in (a,b)]
    fa,fb = ends
    if method == "intermedio":
        target = exact(data["nivel"])
        between = None not in ends and bool(min(ends) <= target <= max(ends))
        satisfied = continuous and between
        expression, search_region = f-target, region
        emit(ctx, "Comprobar que el valor objetivo está entre los valores de los extremos.",
             extremos=list(map(str,ends)), nivel=str(target), entre=between)
    else:
        target = (fb-fa)/(b-a) if None not in ends else None
        satisfied = continuous and differentiable and (method != "rolle" or fa == fb)
        expression = derivative-target if target is not None else None
        search_region = sp.Interval.open(a,b)
        emit(ctx, "Comprobar derivabilidad en el intervalo abierto y comparar los extremos.",
             derivable=differentiable, extremos=list(map(str,ends)), extremos_iguales=fa is not None and fa == fb)
    mode = data["entrega"]
    if mode not in ("plantear", "resolver"):
        raise ValueError("Elegí verificar las hipótesis o resolver.")
    result = {"hipotesis_satisfechas":satisfied}
    if satisfied and mode == "resolver":
        roots = sp.solveset(expression,X,domain=search_region)
        if roots.has(sp.ConditionSet):
            raise DomainError("Las hipótesis se cumplen, pero el motor no pudo despejar el punto exactamente.")
        emit(ctx, "Resolver la ecuación del teorema sobre el intervalo correspondiente.",
             sp.latex(roots),objetivo=str(target))
        result["puntos"] = str(roots)
    return result


def average(data, ctx):
    a,b,region = interval(data)
    f,allowed,_ = function(data["expresion"],ctx)
    require_interval(allowed,region)
    result = ejecutar_calculo({"accion":"calculo","operacion":"definida",**data})
    width = b-a
    formula = rf"f_{{\mathrm{{prom}}}}=\frac{{1}}{{{sp.latex(width)}}}\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}}{sp.latex(f)}\,dx"
    emit(ctx, "Dividir la integral definida por la longitud del intervalo.", formula)
    integral = parse_number(result["valor"])
    value = integral / Fraction(width)
    relation = "=" if result["exactitud"] == "exacta" else r"\approx "
    emit(ctx, "Evaluar la integral y dividir por la longitud.", formula + relation + sp.latex(sp.Rational(value)),
         integral=result["valor"], exactitud=result["exactitud"])
    return {"valor":str(value) if relation == "=" else format(float(value),".12g"),
            "integral":result["valor"],"exactitud":result["exactitud"],"formula_latex":formula}


def substitution(data, ctx):
    f, allowed, _ = function(data["expresion"],ctx)
    inner, _, _ = function(data["sustitucion"],ctx)
    slope=sp.diff(inner,X)
    if slope == 0:
        raise ValueError("La sustitución debe variar con x.")
    u = sp.Symbol("u",real=True)
    adjusted = sp.cancel(f/slope)
    # Reduce módulo u-g(x) para verificar si todo el integrando ajustado depende solo de u.
    quotient = adjusted
    if adjusted.is_polynomial(X) and inner.is_polynomial(X):
        quotient = sp.rem(adjusted, sp.expand(inner)-u, X)
    if quotient.has(X) or not quotient.is_polynomial(u):
        raise DomainError("Elegí una sustitución que deje un polinomio en u después de dividir por du/dx.")
    primitive = sp.integrate(quotient,u).subs(u,inner)
    if sp.simplify(sp.diff(primitive,X)-f) != 0:
        raise DomainError("No se pudo comprobar la sustitución para esta entrada.")
    emit(ctx, "Elegir u, calcular du y ajustar el integrando.", rf"u={sp.latex(inner)},\quad du={sp.latex(slope)}\,dx",
         ajuste=str(quotient),dominio=str(allowed))
    emit(ctx, "Integrar en u, regresar a x y comprobar por derivación.", sp.latex(primitive)+r"+C")
    result = {"primitiva":str(primitive)+" + C","dominio":str(allowed),"formula_latex":sp.latex(primitive)+r"+C"}
    if "inferior" in data or "superior" in data:
        if not data.get("inferior") or not data.get("superior"):
            raise ValueError("Ingresá ambos extremos para evaluar la integral definida.")
        a,b,region = interval(data)
        require_interval(allowed,region)
        value=sp.simplify(primitive.subs(X,b)-primitive.subs(X,a))
        emit(ctx, "Evaluar los extremos después de regresar a x.", sp.latex(value))
        result["valor"]=str(value)
    return result


def area(data, ctx):
    a,b,region=interval(data)
    f=polynomial(data["expresion"],(X,))
    g=polynomial(data.get("segunda") or "0",(X,))
    difference=sp.expand(f-g)
    crossings=sorted(finite_roots(difference,sp.Interval.open(a,b))) if difference else []
    bounds=[a,*crossings,b]
    total=sp.S.Zero
    if data["entrega"] not in ("plantear","resolver"):
        raise ValueError("Elegí plantear o resolver.")
    integral=sp.integrate(difference,X) if data["entrega"] == "resolver" else None
    terms=[]
    for left,right in zip(bounds,bounds[1:]):
        value=difference.subs(X,midpoint(left,right))
        sign=-1 if value<0 else 1
        term=rf"\int_{{{sp.latex(left)}}}^{{{sp.latex(right)}}}\left({sp.latex(sign*difference)}\right)\,dx"
        emit(ctx,"Determinar la función superior en este subintervalo.",term,
             superior="f" if sign==1 else "g", muestra=str(midpoint(left,right)))
        terms.append(term)
        if integral is not None:
            total += sign*(integral.subs(X,right)-integral.subs(X,left))
    formula="A="+"+".join(terms)
    intersections = [a,*crossings,b] if difference else []
    result={"formula_latex":formula,
            "cruces":[str(x) for x in intersections if difference.subs(X,x)==0],
            "curvas_coincidentes":difference == 0}
    if integral is not None:
        result["area"]=str(sp.simplify(total))
        emit(ctx,"Evaluar las integrales y sumar sus áreas.",formula+"="+sp.latex(total))
    return result
