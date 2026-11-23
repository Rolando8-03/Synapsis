"""Motor de Synapsis. Los datos exactos se conservan como fracciones en el JSON."""
from fractions import Fraction
from copy import deepcopy
from math import acos, degrees, hypot, isfinite
from pathlib import Path
import re
import sys

from motor_matematico.application.catalog import CATALOG
from motor_matematico.application.derivative_view import derivative_lines, expression_tex
from motor_matematico.application.service import execute
from motor_matematico.algorithms.linear.context import Context, vector as parse_vector, matrix as bounded_matrix
from motor_matematico.algorithms.numerical.functions import Function, decimal
from motor_matematico.algorithms.calculo import analizar
from motor_matematico.domain.models import DomainError, serializar
from motor_matematico.algorithms.linear.factorization import factor, reuse_factors
from curso import (
    accumulation, accuracy, balance, dominance, economy, entry, from_equations,
    invertible_theorem, machine, matrix_compare, nonnegative, parametric,
    polynomials, precision, propagation, subspace, taylor_exp, transformation, vector_diagram,
)
from motor_matematico.parsing.numbers import parse_number

sys.path.insert(0, str(Path(__file__).resolve().parent / "motor_grupo4"))
from modulos.modulo_sistemas import resolver_desde_interfaz
from modulos.modulo_matrices import ejecutar_programa5
from operaciones_matrices import _serializar
from relaciones_vectoriales import ejecutar_relaciones
from calculo_basico import ejecutar_calculo
from formato_latex import lista_soluciones_latex, operacion_latex
from temario import SESSIONS, CALCULUS_COURSES
import operadores_calculo
from catalogo_calculo_i import catalog_entries
from procedimientos import (calculus_trace, compare_bisection, compare_iterations, error_trace, legacy_trace,
                            original_extra, original_rows, root_visual)

EXACT = "Exacto · fracciones"
NUMERICAL = "Método numérico"
ORIGINAL = "Motor de la calculadora original"

def field(name, label, kind="scalar", default="", required=True, **extra):
    return dict(name=name, label=label, kind=kind, default=default, required=required, **extra)

def spec(title, description, fields):
    return dict(title=title, description=description, fields=fields)

A = field("A", "Matriz A", "matrix", "2 1\n1 -1")
B = field("B", "Matriz B", "matrix", "1 2\n3 4")
V = field("v", "Vector v", "vector", "1 2 3")
U = field("u", "Vector u", "vector", "2 -1 3")
BOUNDS = [field("from", "Desde", default="-6"), field("to", "Hasta", default="6")]
EXTRA = {
    "original.sistema": spec("Resolver y clasificar", "Ingresá la matriz aumentada. La reducción exacta se actualiza al completar las celdas.", [
        field("objetivo", "Resultado solicitado", "select", "completo", choices=["completo", "escalonada"])]),
    "original.inversa_adjunta": spec("Inversa por adjugata", "Desarrollo con cofactores y comprobación del producto.", [A]),
    "original.propiedades_det": spec("Propiedades del determinante", "Comprobá propiedades con las matrices y las operaciones elementales elegidas.", [A, B,
        field("eje", "Operar sobre", "select", "fila", choices=["fila", "columna"]), field("fila_i", "Primer índice", "integer", "1"),
        field("fila_j", "Segundo índice", "integer", "2"), field("k", "Escalar k", default="3")]),
    "original.triangular": spec("Resolver con L y U", "Ingresá los factores triangulares para resolver Ly=b y Ux=y.", [
        field("A", "Factor L", "matrix", "1 0\n1/2 1"),
        field("B", "Factor U", "matrix", "2 1\n0 -3/2"), field("b", "Vector b", "vector", "5 1")]),
    "original.relaciones": spec("Propiedades de Ax y verificaciones", "Verificá linealidad, comparación y propiedades del producto matriz-vector.", [
        A, field("u", "Vector u", "vector", "2 -1"), field("v", "Vector v", "vector", "1 2"), field("c", "Escalar c", default="2")]),
    "original.primitiva": spec("Integral indefinida · método original", "Calculá una primitiva con las reglas de integración de la calculadora original.", [field("expresion", "Función f(x)", "expression", "3*x^2")]),
    "vectores.combinacion": spec("Combinación αu + βv", "Combinación lineal exacta de dos vectores.", [U, V, field("alpha", "α", default="2"), field("beta", "β", default="-1")]),
    "vectores.angulo": spec("Ángulo entre dos vectores", "Usa el producto punto y las normas euclidianas. El ángulo se expresa en grados.", [U,V]),
    "calculo.derivada_parcial": spec("Derivada parcial", "Derivá un polinomio en x e y respecto de una variable.", [
        field("expresion", "Función de x e y", "expression", "x^2*y", editor="parcial"),
        field("variable", "Derivar respecto de", "select", "x", choices=["x", "y"])]),
    "calculo.sumatoria": spec("Sumatoria finita", "Sumá un polinomio en k entre dos índices enteros, incluidos ambos.", [
        field("expresion", "Término en k", "expression", "k^2", editor="sumatoria"),
        field("inferior", "Índice inicial", "integer", "1"),
        field("superior", "Índice final", "integer", "3")]),
    "calculo.limite_lateral": spec("Límite lateral", "Calculá el límite lateral de un polinomio o de un cociente de polinomios.", [
        field("expresion", "Función de x", "expression", "(x^2-1)/(x-1)", editor="limite"),
        field("punto", "Punto de aproximación", default="1"),
        field("lado", "Lado", "select", "+", choices=["-", "+"])]),
    "grafica.explicita": spec("Función explícita", "Explorá y=f(x) en un intervalo. Usá * para multiplicar y ^ para potencias.", [field("expr", "f(x)", "expression", "sin(x)+x/4"), *BOUNDS]),
    "grafica.parametrica": spec("Curva paramétrica", "Dibujá una curva dada por x(t) e y(t). Las funciones trigonométricas usan radianes.", [
        field("expr", "x(t)", "expression", "cos(t)"), field("y", "y(t)", "expression", "sin(t)"),
        field("from", "Desde", default="0"), field("to", "Hasta", default="6.28318530718")]),
    "bases.enteros": spec("Enteros entre bases 2–36", "Convierte enteros de forma exacta, con signo y dígitos A–Z.", [
        field("numero", "Numeral", "text", "11010110"), field("origen", "Base de origen", "integer", "2"), field("destino", "Base de destino", "integer", "16")]),
    "bases.romanos": spec("Números romanos", "Conversión de enteros entre 1 y 3999 y validación de la forma romana estándar.", [
        field("sentido", "Conversión", "select", "decimal a romano", choices=["decimal a romano", "romano a decimal"]),
        field("numero", "Número", "text", "49")]),
}

VARIABLES = field("variables", "Variables en orden", "text", "x y")
EQUATIONS = field("ecuaciones", "Ecuaciones · una por línea", "multiline", "2x+y=5\nx-y=1")
DECIMALS = field("decimales", "Decimales", "integer", "4")
EXTRA.update({
    "sistemas.ecuaciones": spec("Ecuaciones a matriz aumentada", "Escribí tus incógnitas y después las ecuaciones. Podés usar 2x, 2*x o fracciones como 1/3.", [VARIABLES, EQUATIONS]),
    "sistemas.homogeneo": spec("Núcleo de A · sistema homogéneo", "Encontrá la base y la dimensión del conjunto solución de Ax=0.", [A]),
    "sistemas.parametrico": spec("Regla de Cramer con un parámetro", "Hallá para qué valores reales del parámetro la solución es única y calculá sus expresiones exactas.", [
        field("variables", "Incógnitas en orden", "text", "x1 x2"), field("parametro", "Parámetro", "text", "s"),
        field("ecuaciones", "Ecuaciones · una por línea", "multiline", "3*s*x1-2*x2=4\n-6*x1+s*x2=1")]),
    "factorizacion.resolver": spec("Resolver Ax=b mediante LU o PLU", "Factorizá A y resolvé con sustituciones. Para obtener solo los factores, usá las otras opciones del grupo.", [
        A, field("b", "Vector b", "vector", "5 1"), field("metodo", "Método", "select", "lu", choices=["lu","plu"])]),
    "matrices.notacion": spec("Orden, entrada aᵢⱼ y diagonal", "Inspeccioná una entrada, su fila y su columna. Los índices comienzan en 1.", [A,
        field("fila", "Índice de fila", "integer", "1"), field("columna", "Índice de columna", "integer", "2")]),
    "matrices.comparar": spec("Igualdad y conmutatividad", "Compará A con B y calculá AB y BA cuando las dimensiones lo permitan.", [A,B]),
    "matrices.teorema_invertible": spec("Criterios de invertibilidad", "Comprobá las condiciones equivalentes del teorema mediante rango y determinante.", [A]),
    "espacios.subespacio": spec("Subespacio por ecuaciones", "Dado un conjunto definido por igualdades lineales, establecé si es subespacio y hallá base y dimensión cuando corresponda.", [
        field("variables", "Variables en orden", "text", "x y z"),
        field("ecuaciones", "Restricciones · una por línea", "multiline", "x=2y")]),
    "espacios.polinomios": spec("Independencia y generación en Pₙ", "Escribí polinomios en x y analizá sus vectores de coeficientes, dimensión y generación.", [
        field("grado", "Grado máximo del espacio Pₙ", "integer", "2"),
        field("familia", "Polinomios · uno por línea", "multiline", "x-2x^2\nx^2-4x\n-7x+8x^2"),
        field("objetivo", "Polinomio objetivo · opcional", "text", "", False)]),
    "transformaciones.formula": spec("¿Es lineal? · desde su fórmula", "Ingresá una componente polinómica por línea. Si es lineal, hallá su matriz, núcleo, imagen, rango y nulidad.", [
        VARIABLES, field("componentes", "Componentes de T · una por línea", "multiline", "x+y\nx-y\n3y"),
        field("v", "Vector para evaluar T · opcional", "vector", "", False)]),
    "modelos.economia": spec("Intercambio y equilibrio económico", "Cada columna representa un sector de origen. Ingresá las ventas a los otros sectores. La calculadora completa la parte de producción retenida y plantea el equilibrio.", [
        field("A", "Transferencias entre sectores", "matrix", "0 20 20\n5 0 30\n30 70 0"),
        field("unidades", "Unidades de las transferencias", "select", "porcentaje", choices=["porcentaje","proporcion"]),
        field("sector", "Número del sector de referencia", "integer", "3", False),
        field("precio", "Precio del sector de referencia · opcional", default="100", required=False)]),
    "modelos.balance": spec("Balance por conservación", "Ingresá una fila por elemento. Usá columnas positivas para reactivos y negativas para productos. Con un grado de libertad, el motor busca el balance entero mínimo.", [
        field("A", "Conteos por elemento y compuesto", "matrix", "3 0 -1 0\n8 0 0 -2\n0 2 -2 -1")]),
    "modelos.flujos": spec("Flujos y mezclas no negativos", "Planteá Ax=b. Calculá la familia de soluciones y el mínimo y máximo posible de cada variable con x ≥ 0.", [
        field("A", "Matriz A de balances", "matrix", "1 1 0 0 0\n0 1 -1 1 0\n0 0 0 1 1\n1 0 0 0 1\n0 0 1 0 0"),
        field("b", "Balance b", "vector", "800 300 500 600 400")]),
    "errores.redondeo": spec("Redondeo, truncamiento y cifras", "Compará ambos métodos y calculá la tolerancia porcentual asociada al número de cifras significativas.", [
        field("numero", "Valor exacto", default="3.1415926536"), DECIMALS,
        field("cifras", "Cifras significativas", "integer", "3")]),
    "errores.propagacion": spec("Propagación de error con derivadas", "Compará el diferencial con la variación de la función para una perturbación dada.", [
        field("expresion", "Función f(x)", "expression", "x^2"), field("x", "Punto x", default="2"),
        field("delta", "Perturbación Δx", default="0.01")]),
    "errores.acumulacion": spec("Acumulación al iterar", "Simulá interés compuesto y compará el efecto de redondear o truncar en cada período.", [
        field("capital", "Capital inicial", default="12345.67"), field("tasa", "Tasa por período · %", default="0.75"),
        field("periodos", "Períodos", "integer", "12"), field("decimales", "Decimales", "integer", "2")]),
    "errores.maquina": spec("Épsilon, límites y cancelación", "Explorá los límites de punto flotante de Python y el efecto de racionalizar una resta de raíces cercanas.", [
        field("a", "Valor a", default="1e16"), field("b", "Valor b", default="1")]),
    "vectores.paralelogramo": spec("Vectores en el plano · paralelogramo", "Visualizá los dos vectores escalados y su suma para cualquier α y β.", [
        field("u", "Vector u", "vector", "2 2"), field("v", "Vector v", "vector", "-6 1"),
        field("alpha", "α", default="1"), field("beta", "β", default="1")]),
    "errores.taylor": spec("Truncamiento de la serie de eˣ", "Compará la serie truncada exacta, el resultado con redondeo por término y la incertidumbre propagada.", [
        field("x", "Punto x", default="0.5"), field("delta", "Incertidumbre de x", default="0.01"),
        field("terminos", "Número de términos", "integer", "4"), DECIMALS]),
    "errores.exactitud": spec("Exactitud y precisión de mediciones", "Cuantificá la distancia del promedio a la referencia y la dispersión de las mediciones.", [
        field("mediciones", "Mediciones", "vector", "3.1 3.2 3.0"), field("referencia", "Referencia", default="3.1415926536")]),
    "iterativos.comparar": spec("Comparar Jacobi y Gauss-Seidel", "Ejecutá ambos con el mismo vector inicial y criterio. Compará las iteraciones, el error y el residual.", [
        *deepcopy(CATALOG["iterativos.gauss_seidel"].fields),
        field("reordenar", "Reordenar filas si existe una diagonal estrictamente dominante", "boolean", False, False)]),
    "iterativos.dominancia": spec("Dominancia y orden de las filas", "Verificá el criterio por fila y obtené un orden estrictamente dominante cuando exista.", [
        field("A", "Matriz A", "matrix", "2 -6 -1\n-3 -1 7\n-8 1 -2"),
        field("b", "Vector b · opcional", "vector", "", False)]),
})

CALCULUS_I, CALCULUS_HANDLERS, CALCULUS_GROUPS = catalog_entries(field, spec)
EXTRA.update(CALCULUS_I)

MODULES = {
    "sistemas": [("Resolución", ["original.sistema", "sistemas.resolver", "sistemas.homogeneo", "sistemas.cramer", "sistemas.parametrico", "sistemas.inversa"]),
        ("Factorización", ["factorizacion.lu", "factorizacion.plu", "factorizacion.resolver", "original.triangular"]),
        ("Notación y modelos", ["sistemas.ecuaciones","modelos.economia","modelos.balance","modelos.flujos"])],
    "matrices": [("Operaciones", ["matrices.notacion", "matrices.comparar", "matrices.suma", "matrices.resta", "matrices.producto", "matrices.escalar", "matrices.transpuesta", "matrices.traza", "matrices.potencia"]),
        ("Reducción y propiedades", ["matrices.analizar", "matrices.ref", "matrices.rref", "matrices.elemental", "matrices.propiedades"]),
        ("Determinantes e inversa", ["determinantes.calcular", "determinantes.cofactores", "matrices.inversa", "original.inversa_adjunta", "original.propiedades_det", "matrices.teorema_invertible"]),
        ("Bloques", ["matrices.particionar", "matrices.suma_bloques", "matrices.producto_bloques"])],
    "vectores": [("Operaciones", ["vectores.suma", "vectores.resta", "vectores.escalar", "vectores.producto_punto", "vectores.producto_cruz", "vectores.norma", "vectores.angulo", "vectores.combinacion", "vectores.paralelogramo", "vectores.proyeccion"]),
        ("Bases y subespacios", ["vectores.analizar", "vectores.generado", "espacios.polinomios", "espacios.subespacio", "espacios.fundamentales", "espacios.base", "espacios.suma", "espacios.interseccion", "espacios.coordenadas", "espacios.cambio_base"]),
        ("Transformaciones", ["transformaciones.formula", "transformaciones.analizar", "transformaciones.desde_imagenes", "transformaciones.componer", "transformaciones.representar", "original.relaciones"])],
    "grafica": [
        ("Gráficas", ["grafica.explicita", "grafica.parametrica", "funciones.evaluar"]),
        ("Derivada e integral básica", ["calculo.derivar", "calculo.derivada_parcial", "calculo.primitiva",
            "original.primitiva", "calculo.definida", "calculo.numerica", "calculo.sumatoria"]),
        *CALCULUS_GROUPS,
    ],
    "raices": [("Métodos de intervalo", ["raices.biseccion", "raices.falsa_posicion"]), ("Métodos abiertos", ["raices.newton", "raices.secante"])],
    "iterativos": [("Métodos de aproximación", ["iterativos.jacobi", "iterativos.gauss_seidel", "iterativos.sor", "iterativos.dominancia","iterativos.comparar"])],
    "errores": [("Análisis numérico", ["errores.calcular", "errores.redondeo", "errores.propagacion", "errores.acumulacion", "errores.taylor", "errores.exactitud", "errores.maquina", "calculadora.evaluar"])],
    "bases": [("Conversiones", ["bases.enteros", "conversiones.bases", "bases.romanos"]), ("Conjuntos", ["conjuntos.operar"])],
}
ALL_OPERATIONS = {key for groups in MODULES.values() for _, ids in groups for key in ids}

def catalog():
    definitions = {key: deepcopy(value.to_dict()) for key, value in CATALOG.items() if key in ALL_OPERATIONS}
    definitions.update(EXTRA)
    for key, name in (("factorizacion.lu", "Solo factorizar A = LU"), ("factorizacion.plu", "Solo factorizar PA = LU")):
        item = definitions[key]
        item.update(title=name, description="Ingresá únicamente la matriz A. Vas a obtener los factores, el procedimiento y la comprobación del producto.")
        item["fields"] = [f for f in item["fields"] if f["name"] == "A"]
    return {"modules": MODULES, "operations": definitions, "sessions": SESSIONS, "calculus_courses": CALCULUS_COURSES}

def solve_original(data):
    rows = data.get("matrix")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 12:
        raise ValueError("Ingresá de 1 a 12 ecuaciones.")
    columns = len(rows[0]) if isinstance(rows[0], list) else 0
    if not 2 <= columns <= 13 or any(not isinstance(r, list) or len(r) != columns for r in rows):
        raise ValueError("Cada ecuación requiere sus coeficientes y el término independiente.")
    def check_cell(value):
        value = str(value).strip().replace("−", "-")
        if not re.fullmatch(r"[+-]?(?:(?:\d{1,24}(?:[.,]\d{0,24})?|[.,]\d{1,24})(?:[eE][+-]?\d{1,2})?|\d{1,24}\s*/\s*[+-]?\d{1,24})", value):
            raise ValueError("Cada celda debe ser un entero, decimal o fracción de tamaño moderado.")
        if "/" in value:
            numerator, denominator = value.split("/")
            return str(Fraction(int(numerator), int(denominator)))
        return value
    checked = [[check_cell(x) for x in row] for row in rows]
    objetivo = data.get("objetivo", "completo")
    if objetivo not in ("completo", "escalonada"):
        raise ValueError("Elegí el análisis completo o la forma escalonada.")
    result = resolver_desde_interfaz(
        {"textos_A": [r[:-1] for r in checked], "textos_b": [r[-1] for r in checked]},
        solo_escalonada=objetivo == "escalonada",
    )
    expressions = result.get("expresiones_rref")
    if expressions:
        result["latex_solucion"] = lista_soluciones_latex(
            [{"constante": Fraction(item["constante"]),
              "terminos": {int(j): Fraction(value) for j,value in item["terminos"].items()}}
             for item in expressions], result["variables_libres"]
        )
    for name in ("pasos_gauss", "pasos_jordan") if data.get("steps", True) else ():
        for step in result.get(name, []):
            operation = step["operacion"]
            decoded = {"tipo":operation["tipo"]}
            for key, value in operation.items():
                if key == "tipo":
                    continue
                if key == "aumentada":
                    decoded[key] = value == "True"
                elif key in ("fila", "columna", "fila_a", "fila_b", "destino", "origen", "multiplo"):
                    decoded[key] = int(value)
                else:
                    decoded[key] = Fraction(value)
            step["formula_latex"] = operacion_latex(decoded)
    if not data.get("steps", True):
        for key in ("pasos_gauss", "pasos_jordan", "pasos_sustitucion"):
            result.pop(key, None)
    return result

ROMAN = ((1000,"M"), (900,"CM"), (500,"D"), (400,"CD"), (100,"C"), (90,"XC"),
         (50,"L"), (40,"XL"), (10,"X"), (9,"IX"), (5,"V"), (4,"IV"), (1,"I"))
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def roman(n):
    if not 1 <= n <= 3999:
        raise ValueError("El número debe estar entre 1 y 3999.")
    result = []
    for value, label in ROMAN:
        count, n = divmod(n, value)
        result.append(label * count)
    return "".join(result)

def roman_conversion(data):
    text = str(data["numero"]).strip().upper()
    if data["sentido"] == "decimal a romano":
        if not re.fullmatch(r"[0-9]{1,4}", text):
            raise ValueError("Ingresá un entero entre 1 y 3999.")
        return {"representacion": roman(int(text))}
    if not re.fullmatch(r"[MDCLXVI]{1,15}", text):
        raise ValueError("Ingresá números romanos, por ejemplo XLIX.")
    remainder, n = text, 0
    for value, label in ROMAN:
        while remainder.startswith(label):
            remainder = remainder[len(label):]
            n += value
    if remainder or not 1 <= n <= 3999 or roman(n) != text:
        raise ValueError("Usá la escritura romana estándar, por ejemplo XLIX.")
    return {"valor": n, "romano": text}

def base_conversion(data):
    source, target = int(data["origen"]), int(data["destino"])
    if not 2 <= source <= 36 or not 2 <= target <= 36:
        raise ValueError("Las bases deben estar entre 2 y 36.")
    text = str(data["numero"]).strip().upper()
    if not re.fullmatch(r"[+-]?[0-9A-Z]{1,128}", text):
        raise ValueError("Ingresá un entero con hasta 128 dígitos.")
    try:
        number = int(text, source)
    except ValueError:
        raise ValueError("El numeral contiene dígitos que no existen en la base de origen.") from None
    remaining, digits = abs(number), []
    unsigned = text.lstrip("+-")
    positional = [f"{DIGITS.index(char)}·{source}^{i}" for i,char in reversed(list(enumerate(reversed(unsigned))))]
    steps = [{"description":"Desarrollar cada dígito en potencias de su base de origen.",
              "data":{"aportes":positional,"valor_decimal":str(number)}}]
    while remaining:
        quotient, digit = divmod(remaining, target)
        steps.append({"description": f"{remaining} ÷ {target} = {quotient}, residuo {DIGITS[digit]}"})
        digits.append(DIGITS[digit])
        remaining = quotient
    numeral = ("-" if number < 0 else "") + ("".join(reversed(digits)) or "0")
    return {"representacion": numeral, "valor_decimal": str(number)}, steps

def graph(data, parametric):
    start, stop = decimal(data["from"]), decimal(data["to"])
    if not start < stop or abs(start) > 1e7 or abs(stop) > 1e7:
        raise ValueError("Ingresá un intervalo creciente dentro de ±10 000 000.")
    context = Context()
    def expression(value):
        return Function(re.sub(r"\bt\b", "x", value) if parametric else value, context)
    x_fn = expression(data["expr"]) if parametric else None
    y_fn = expression(data["y"] if parametric else data["expr"])
    points = []
    for i in range(801):
        t = start + (stop - start) * i / 800
        try:
            x, y = float(x_fn.value(t) if x_fn else t), float(y_fn.value(t))
            points.append([x,y] if isfinite(x) and isfinite(y) else [None,None])
        except DomainError:
            points.append([None,None])
    if all(x is None for x,_ in points):
        raise ValueError("La función no tiene puntos reales representables en el intervalo.")
    return {"parametric": parametric, "points": points,
            "muestras": [[str(start + (stop-start)*i/800), *points[i]] for i in range(0, 801, 100)]}

def original_program(operation, data):
    for key in ("A", "B"):
        if key in data:
            bounded_matrix(data[key])
    if operation == "original.inversa_adjunta":
        # La expansión de cofactores original es recursiva.
        if len(str(data["A"]).splitlines()) > 6:
            raise ValueError("La adjugata original admite hasta orden 6. Para matrices grandes usá Gauss-Jordan.")
        return ejecutar_programa5({**data, "opcion": "8"})
    if operation == "original.propiedades_det":
        return ejecutar_programa5({**data, "opcion": "13"})
    if operation == "original.triangular":
        return ejecutar_programa5({**data, "opcion": "14"})
    if operation == "original.relaciones":
        matrix = bounded_matrix(data["A"])
        return ejecutar_relaciones({**data, "A": matrix, "u": parse_vector(data["u"]),
                                    "v": parse_vector(data["v"]), "filas": len(matrix),
                                    "columnas": len(matrix[0]), "accion": "propiedades_matriz_vector"})
    return ejecutar_calculo({**data, "accion": "calculo", "operacion": "integrar"})

def vector_pair(data):
    def parse(key):
        return parse_vector(data[key])
    u,v = parse("u"),parse("v")
    if not u or len(u) != len(v) or len(u)>100:
        raise ValueError("Los vectores deben tener la misma dimensión (de 1 a 100).")
    return u,v

COURSE_HANDLERS = {
    **CALCULUS_HANDLERS,
    "calculo.derivada_parcial": operadores_calculo.partial,
    "calculo.sumatoria": operadores_calculo.summation,
    "matrices.notacion": entry, "matrices.comparar": matrix_compare,
    "matrices.teorema_invertible": invertible_theorem, "espacios.polinomios": polynomials,
    "sistemas.parametrico": parametric, "espacios.subespacio": subspace,
    "transformaciones.formula": transformation, "modelos.economia": economy,
    "modelos.balance": balance, "modelos.flujos": nonnegative, "errores.redondeo": precision,
    "errores.propagacion": propagation, "errores.acumulacion": accumulation,
    "errores.maquina": machine, "iterativos.dominancia": dominance, "vectores.paralelogramo": vector_diagram,
    "errores.taylor": taylor_exp, "errores.exactitud": accuracy,
}
WITH_CONTEXT = {*CALCULUS_HANDLERS,"calculo.sumatoria", "calculo.limite_lateral", "calculo.derivada_parcial","matrices.notacion", "matrices.comparar", "matrices.teorema_invertible", "espacios.polinomios",
                "sistemas.parametrico","transformaciones.formula","espacios.subespacio","modelos.economia",
                "modelos.balance","modelos.flujos","iterativos.dominancia"}


def calculate(operation, data, steps=True):
    if not isinstance(operation, str) or operation not in ALL_OPERATIONS or not isinstance(data, dict):
        raise ValueError("Operación o datos no válidos.")
    fields = EXTRA[operation]["fields"] if operation in EXTRA else CATALOG[operation].fields
    for f in fields:
        value = data.get(f["name"])
        if f.get("required") and f["name"] not in data and operation in CALCULUS_HANDLERS:
            raise ValueError(f'Completá «{f["label"]}».')
        if f["kind"] == "expression" and isinstance(value, str) and len(value) > 500:
            raise ValueError("La expresión admite hasta 500 caracteres.")
        if f["name"] in data and f["kind"] in {"matrix","vector","vectors"} and len(str(value)) > 15000:
            raise ValueError("La entrada matricial es demasiado larga.")
    if operation not in EXTRA:
        if operation in {"factorizacion.lu", "factorizacion.plu"}:
            data = {k:v for k,v in data.items() if k != "b"}
        response = execute({"schema_version":"1.0", "operation_id":operation, "input":data,
                            "options":{"include_steps":steps}})
        if operation == "calculo.derivar" and response.get("result"):
            response["metadata"]["formulas_derivada"] = derivative_lines(data, response["result"])
        if operation == "raices.newton" and (response.get("result") or {}).get("derivada"):
            derivative = response["result"]["derivada"]
            response["metadata"]["derivada_latex"] = expression_tex(analizar(derivative, variable=True))
        if operation.startswith("raices.") and (response.get("result") or {}).get("aproximacion") is not None:
            try:
                response["result"]["grafico_raiz"] = root_visual(data,response["result"])
            except (DomainError,ValueError,ArithmeticError):
                response["result"]["grafico_raiz"] = None
        if operation=="raices.biseccion" and response.get("status")=="ok":
            out=response["result"]
            try:
                comparison=compare_bisection(data,out)
            except (ValueError,ArithmeticError,RuntimeError):
                comparison=None
            if comparison:
                response["verification"]["contraste_independiente"]=serializar(comparison)
        if response.get("result") and steps:
            context = Context()
            if operation in {"calculadora.evaluar","calculo.derivar","calculo.definida","calculo.primitiva"}:
                calculus_trace(operation,data,response["result"],context)
            elif operation == "matrices.propiedades":
                legacy_trace(operation,response["result"],context)
            response["steps"].extend(step.to_dict() for step in context.steps)
        return response
    output, trace = None, []
    metadata = {"exact": True}
    verification = {}
    context = Context(collect_steps=steps)
    if operation == "original.sistema":
        output = solve_original({**data, "steps": steps})
        if "solucion_particular" in output:
            images = [
                [sum(Fraction(a) * Fraction(v) for a, v in zip(row, direction)) for row in output["A"]]
                for direction in output["direcciones"]
            ]
            verification = {"passed": all(row["cumple"] for row in output["comprobaciones"])
                            and all(not any(image) for image in images), "Av": images}
            output["comprobaciones_direcciones"] = images
        metadata["source"] = ORIGINAL
    elif operation == "sistemas.homogeneo":
        A = bounded_matrix(data["A"])
        output = solve_original({"matrix":[[str(x) for x in row] + ["0"] for row in A], "steps":steps})
        if steps:
            context.emit("homogeneo","Añadir un término igual a cero por ecuación.",{"A":A},r"Ax=0")
            original_rows(context,output["pasos_jordan"])
            context.emit("base","Tomar cada variable libre como parámetro independiente.",{"direcciones":output["direcciones"]},output["latex_solucion"])
        output = {"clasificacion":output["clasificacion"], "base_del_espacio_solucion":output["direcciones"],
                  "dimension":len(output["direcciones"]), "rango_A":output["rango_A"],
                  "matriz_aumentada":output["matriz_inicial"], "forma_reducida":output["matriz_rref"],
                  "formula_latex":output["latex_solucion"]}
        verification = {"passed":True}
    elif operation == "sistemas.ecuaciones":
        output = from_equations(data, solve_original, context)
    elif operation == "factorizacion.resolver":
        A = bounded_matrix(data.get("A"))
        method = data.get("metodo", "lu")
        if method not in ("lu", "plu"):
            raise ValueError("Elegí LU o PLU para resolver el sistema.")
        rhs = data.get("b")
        if rhs is None or rhs == [] or isinstance(rhs, str) and not rhs.strip():
            raise ValueError("Para resolver Ax=b, ingresá el vector b. Para obtener solo los factores, alcanza con A.")
        b = parse_vector(rhs, len(A))
        if "factores" in data:
            output, verification = reuse_factors(A, b, data["factores"], method == "plu", context)
        else:
            output, verification = factor(A, context, method == "plu", b)
    elif operation=="iterativos.comparar":
        output=compare_iterations(data,context)
        metadata["exact"]=False
    elif operation in COURSE_HANDLERS:
        handler = COURSE_HANDLERS[operation]
        output = handler(data, context) if operation in WITH_CONTEXT else handler(data)
        metadata["exact"] = operation not in {"errores.propagacion", "errores.maquina", "errores.acumulacion", "errores.taylor", "errores.exactitud"}
    elif operation.startswith("original."):
        output = _serializar(original_program(operation, data))
        metadata = {"source": ORIGINAL}
    elif operation == "bases.enteros":
        output, trace = base_conversion(data)
    elif operation == "bases.romanos":
        output = roman_conversion(data)
    elif operation.startswith("grafica."):
        output = graph(data, operation.endswith("parametrica"))
        metadata["exact"] = False
    else:
        u,v = vector_pair(data)
        if operation.endswith("combinacion"):
            alpha,beta = parse_number(data["alpha"]),parse_number(data["beta"])
            output = {"vector":[str(alpha*a+beta*b) for a,b in zip(u,v)]}
        else:
            denominator = hypot(*u)*hypot(*v)
            if denominator == 0:
                raise ValueError("El ángulo con un vector nulo no está definido.")
            product = sum(a*b for a,b in zip(u,v))
            cosine = max(-1,min(1,float(product)/denominator))
            output = {"angulo_grados":degrees(acos(cosine)), "producto_punto":str(product), "coseno":cosine}
            metadata["exact"] = False
    if steps:
        if operation=="original.primitiva":
            calculus_trace(operation,data,output,context)
        elif operation.startswith("original."):
            legacy_trace(operation,output,context)
        elif operation.startswith("errores."):
            error_trace(operation,data,output,context)
        else:
            original_extra(operation,data,output,context)
    return {"status":"ok", "result":serializar(output), "metadata":metadata,
            "verification":serializar(verification), "steps":(trace or [step.to_dict() for step in context.steps]) if steps else []}
