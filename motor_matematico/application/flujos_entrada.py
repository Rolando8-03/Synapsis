"""Entrada compartida para los flujos de sistemas y cálculo."""
from fractions import Fraction

import sympy as sp

from motor_matematico.algorithms.calculo_docente.calculo_i import X, function
from motor_matematico.application.curso import classify_ranks, symbols, system_data
from motor_matematico.algorithms.calculo_docente.integracion import elementary
from motor_matematico.algorithms.linear.context import Context, matrix
from motor_matematico.algorithms.linear.reduction import reduce, solve
from motor_matematico.domain.models import DomainError, serializar


SYSTEM_METHODS = {
    "gauss": "Gauss", "gauss_jordan": "Gauss-Jordan", "sustitucion": "Sustitución",
    "igualacion": "Igualación", "reduccion": "Reducción", "cramer": "Cramer",
    "inversa": "Matriz inversa", "lu": "LU", "plu": "PLU", "jacobi": "Jacobi",
    "gauss_seidel": "Gauss-Seidel", "sor": "SOR",
}
ITERATIVE = ("jacobi", "gauss_seidel", "sor")
SCHOOL = ("sustitucion", "igualacion", "reduccion")
CALCULUS_METHODS = {
    "integral": {"elemental": "Reglas elementales", "sustitucion": "Sustitución",
                 "por_partes": "Por partes", "fracciones_parciales": "Fracciones parciales",
                 "numerica": "Integración numérica"},
    "derivada": {"definicion": "Definición", "cadena": "Cadena", "producto": "Producto",
                  "cociente": "Cociente", "exponencial": "Exponencial",
                  "logaritmica": "Logarítmica", "trigonometrica": "Trigonométrica"},
    "limite": {"lateral": "Límites laterales", "factorizacion": "Factorización",
                "racionalizacion": "Racionalización", "infinito": "Límite infinito en un punto",
                "al_infinito": "Términos dominantes al infinito"},
}


def school_system(A, b, names, method, steps):
    """Desarrolla el método solicitado para dos ecuaciones con dos incógnitas."""
    if len(A) != 2 or len(A[0]) != 2:
        raise ValueError("Este desarrollo escolar admite dos ecuaciones con dos incógnitas. Para otro tamaño, elegí Gauss.")
    ctx = Context(collect_steps=steps)
    x, y = [sp.Symbol(str(name)) for name in names]
    equations = [sp.Eq(a*x+c*y, d, evaluate=False) for (a, c), d in zip(A, b)]
    ctx.emit("ecuaciones", "Escribir las ecuaciones con los coeficientes ingresados.", {},
             r"\quad;\quad".join(map(sp.latex, equations)))
    candidates = (j for j in range(2) if (all if method == "igualacion" else any)(row[j] for row in A))
    j = next(candidates, None)
    if j is None:
        return school_boundary(A, b, method, ctx)
    k = 1-j
    p, q = (0, 1) if A[0][j] else (1, 0)
    xp, xk = (x, y)[j], (x, y)[k]
    p1, p2 = A[p][j], A[q][j]
    c1, c2 = A[p][k], A[q][k]
    intercept, slope = b[p]/p1, -c1/p1
    isolated = slope*xk+intercept
    if method == "reduccion":
        coefficient, rhs = p1*c2-p2*c1, p1*b[q]-p2*b[p]
        combined = sp.Eq(coefficient*xk, rhs, evaluate=False)
        ctx.emit("reduccion", "Multiplicar las ecuaciones y restarlas para cancelar una incógnita.",
                 {"multiplicador_primera":-p2, "multiplicador_segunda":p1, "filas":[p+1,q+1]},
                 rf"({sp.latex(sp.Rational(p1))})E_{{{q+1}}}-({sp.latex(sp.Rational(p2))})E_{{{p+1}}}\implies {sp.latex(combined)}")
    else:
        ctx.emit("despeje", f"Despejar una incógnita de la ecuación {p+1}.", {},
                 sp.latex(sp.Eq(xp, isolated, evaluate=False)))
        if method == "igualacion":
            other = (b[q]-c2*xk)/p2
            ctx.emit("despeje", f"Despejar la misma incógnita de la ecuación {q+1}.", {},
                     sp.latex(sp.Eq(xp, other, evaluate=False)))
            coefficient, rhs = slope+c2/p2, b[q]/p2-intercept
            left, right = isolated, other
        else:
            coefficient, rhs = p2*slope+c2, b[q]-p2*intercept
            left, right = p2*isolated+c2*xk, b[q]
        ctx.emit(method, "Obtener la ecuación en la incógnita restante.", {},
                 sp.latex(sp.Eq(left, right, evaluate=False)) + r"\implies " +
                 sp.latex(sp.Eq(coefficient*xk, rhs, evaluate=False)))
    if coefficient == 0:
        return school_boundary(A, b, method, ctx)
    values = [Fraction(0), Fraction(0)]
    values[k] = rhs/coefficient
    values[j] = slope*values[k]+intercept
    ctx.emit("resolver", "Dividir por el coeficiente y sustituir el valor en la ecuación despejada.", {},
             sp.latex(sp.Eq(xk, values[k], evaluate=False)) + r",\quad " +
             sp.latex(sp.Eq(xp, values[j], evaluate=False)))
    products = [sum(a*v for a, v in zip(row, values)) for row in A]
    ctx.emit("comprobar", "Comprobar la solución en las dos ecuaciones originales.",
             {"Ax":products, "b":b}, sp.latex(sp.Matrix(products))+"="+sp.latex(sp.Matrix(b)))
    return {"status":"ok", "result":serializar({"particular":values}),
            "verification":{"passed":products == b}, "steps":serializar([s.to_dict() for s in ctx.steps])}


def school_boundary(A, b, method, ctx):
    if method == "igualacion" and all(any(row) for row in A) and not any(A[0][j] and A[1][j] for j in range(2)):
        values = [next(rhs/row[j] for row, rhs in zip(A,b) if row[j]) for j in range(2)]
        ctx.emit("despeje", "Cada ecuación ya contiene una incógnita distinta.", {},
                 sp.latex(sp.Matrix(values)))
        return {"status":"ok", "result":serializar({"particular":values}),
                "verification":{"passed":True}, "steps":serializar([s.to_dict() for s in ctx.steps])}
    ctx.emit("rangos", "Clasificar el sistema cuando falta un pivote o la incógnita se cancela.", {})
    out = solve(A, b, ctx)
    verification = out.pop("verification")
    result = "inconsistent" if out["clasificacion"] == "incompatible" else "infinite"
    return {"status":result, "result":serializar(out), "verification":serializar(verification),
            "steps":serializar([s.to_dict() for s in ctx.steps])}


def systems(data, steps, calculate):
    goal = data.get("objetivo", "resolver")
    form = data.get("formato", "matriz")
    method = data.get("metodo", "gauss")
    if goal not in {"clasificar", "resolver", "comparar"} or form not in {"matriz", "ecuaciones"}:
        raise ValueError("Elegí un objetivo y un formato de entrada válidos.")
    if form == "ecuaciones":
        names = symbols(data.get("variables", "x y"))
        A, b = system_data(data.get("ecuaciones"), names)
        augmented = matrix([list(map(str, row)) for row in A.row_join(b).tolist()])
    else:
        augmented = matrix(data.get("matrix"))
        names = [f"x{i+1}" for i in range(len(augmented[0])-1)]
    if len(augmented[0]) < 2:
        raise ValueError("La matriz aumentada requiere al menos una incógnita y la columna b.")
    A, b = [row[:-1] for row in augmented], [row[-1] for row in augmented]
    base = {"A": [list(map(str, row)) for row in A], "b": list(map(str, b))}
    if goal == "clasificar":
        ctx = Context(collect_steps=steps)
        size = len(A[0])
        reduction = reduce(augmented, ctx, reduced=False, pivot_limit=size)
        rank = len(reduction["pivots"])
        contradiction = any(not any(row[:-1]) and row[-1] for row in reduction["matrix"])
        out = classify_ranks(rank, rank + contradiction, size)
        ctx.emit("teorema", "Aplicar Rouché–Frobenius para clasificar el sistema.", {"teorema": {
            "enunciado": r"Ax=b\text{ compatible}\iff\operatorname{rang}(A)=\operatorname{rang}([A\mid b])",
            "hipotesis": "A y b tienen la misma cantidad de ecuaciones y coeficientes reales.",
            "evidencia": out,
            "conclusion": out["clasificacion"],
        }},
                 rf"\operatorname{{rang}}(A)={rank},\quad "
                 rf"\operatorname{{rang}}([A\mid b])={rank + contradiction},\quad n={size}")
        answer = {"status":"ok","result":out,"steps":serializar([step.to_dict() for step in ctx.steps])}
        label = "Clasificación por rangos"
    elif goal == "comparar":
        answer = calculate("iterativos.comparar", {**data, **base}, steps)
        label = "Comparación de Jacobi y Gauss-Seidel"
    elif method in SCHOOL:
        answer = school_system(A, b, names, method, steps)
        label = SYSTEM_METHODS[method]
    else:
        if method not in SYSTEM_METHODS:
            raise ValueError("Elegí un método disponible para resolver el sistema.")
        if method in ITERATIVE:
            operation = "iterativos."+method
        elif method in {"lu", "plu"}:
            operation = "factorizacion.resolver"
        elif method in {"cramer", "inversa"}:
            operation = "sistemas."+method
        else:
            operation = "sistemas.resolver"
        answer = calculate(operation, {**data, **base}, steps)
        label = SYSTEM_METHODS[method]
    if answer.get("result"):
        answer["result"]["variables"] = list(map(str, names))
        answer["result"]["metodo_elegido"] = label
        if steps and form == "ecuaciones":
            answer["steps"].insert(0, {"kind":"ecuaciones","description":"Construir la matriz aumentada con las incógnitas en el orden indicado.",
                                      "data":{"variables":list(map(str,names)), "matriz":serializar(augmented)},
                                      "formula":r"[A\mid b]=" + sp.latex(sp.Matrix(augmented))})
    return answer


def automatic_integral(data, steps, calculate):
    ctx = Context(collect_steps=False)
    f, _, _ = function(data["expresion"], ctx)
    try:
        elementary(f)
    except DomainError:
        nodes = (node.args[0] if node.is_Pow or node.func in (sp.sin, sp.cos, sp.exp)
                 else node for node in sp.preorder_traversal(f))
        candidates = tuple(dict.fromkeys(node for node in nodes if node != X and node != f and node.has(X)))[:12]
        for inner in candidates:
            try:
                answer = calculate("calculo.sustitucion", {**data, "sustitucion":str(inner)}, steps)
            except (DomainError, ValueError, sp.PolynomialError):
                continue
            return answer, "Sustitución"
        if not data.get("inferior"):
            for key in ("por_partes", "fracciones_parciales"):
                try:
                    answer = calculate("calculo."+key, data, steps)
                except DomainError:
                    continue
                return answer, CALCULUS_METHODS["integral"][key]
            raise DomainError("No se reconoció una técnica aplicable. Elegí una técnica o ingresá una sustitución u(x).")
    operation = "definida" if data.get("inferior") else "primitiva"
    answer = calculate("calculo."+operation, data, steps)
    result = answer.get("result") or {}
    label = "Integración numérica" if operation == "definida" and not result.get("expresion") else "Reglas elementales"
    return answer, label


def calculus(data, steps, calculate):
    kind = data.get("operacion", "integral")
    if kind not in CALCULUS_METHODS:
        raise ValueError("Elegí una integral, una derivada o un límite.")
    if data.get("variable", "x") != "x":
        raise ValueError("Este editor admite x como variable. Usá x o elegí una operación con otras variables.")
    method = data.get("tecnica_"+kind, "auto")
    methods = CALCULUS_METHODS[kind]
    if method != "auto" and method not in methods:
        raise ValueError("Elegí una técnica disponible para esta operación.")
    if not data.get("expresion"):
        raise ValueError("Escribí la función en el editor.")
    if kind == "integral":
        if bool(data.get("inferior")) != bool(data.get("superior")):
            raise ValueError("Ingresá los dos extremos o dejá ambos vacíos para una primitiva.")
        if method == "auto":
            answer, label = automatic_integral(data, steps, calculate)
        else:
            if method == "sustitucion" and not data.get("sustitucion"):
                raise ValueError("Ingresá u(x) o elegí Automática para detectar una sustitución.")
            if method in {"por_partes", "fracciones_parciales"} and data.get("inferior"):
                raise ValueError("Para esta técnica, obtené primero la primitiva y después evaluá sus extremos.")
            if method == "numerica" and not data.get("inferior"):
                raise ValueError("Ingresá los dos extremos para integrar numéricamente.")
            operation = ("definida" if data.get("inferior") else "primitiva") if method == "elemental" else method
            answer = calculate("calculo."+operation, data, steps)
            if method == "elemental" and operation == "definida" and not (answer.get("result") or {}).get("expresion"):
                raise DomainError("No se obtuvo una primitiva elemental. Elegí otra técnica.")
            label = methods[method]
    elif kind == "derivada":
        operation = "derivar" if method == "auto" else "derivada_"+method
        answer = calculate("calculo."+operation, data, steps)
        label = "Derivación simbólica" if method == "auto" else methods[method]
    else:
        operation = "limite_lateral" if method == "auto" else "limite_"+method
        if method != "al_infinito" and not data.get("punto"):
            raise ValueError("Indicá el punto al que se aproxima x.")
        answer = calculate("calculo."+operation, data, steps)
        label = methods["lateral" if method == "auto" else method]
    if answer.get("result"):
        answer["result"]["tecnica_elegida"] = label
    return answer
