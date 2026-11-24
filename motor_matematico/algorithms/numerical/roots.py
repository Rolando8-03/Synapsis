"""Raíces con tablas de la misma ejecución y terminaciones diferenciadas."""

from decimal import Decimal as D
from fractions import Fraction as F
from .functions import Function, decimal
from .polynomials import DIFFERENCES, difference, horner, step_size
from ..linear.context import integer, tex
from ...parsing.numbers import parse_number
from ...domain.models import InputError, DomainError


def settings(data):
    tx = parse_number(data.get("tolerancia_x", "1e-8"))
    tf = parse_number(data.get("tolerancia_f", "1e-8"))
    if not F(1, 10**24) <= tx <= 1 or not F(1, 10**24) <= tf <= 1:
        raise InputError("Las tolerancias deben estar entre 1e-24 y 1.")
    return (
        tx,
        tf,
        integer(data.get("max_iteraciones", 100), "Máximo de iteraciones", 1, 200),
    )


def roots(method, data, ctx):
    f = Function(data["expresion"], ctx)
    tx, tf, limit = settings(data)
    if f.binary_functions and min(tx, tf) < F(1, 10**12):
        raise InputError(
            "Las funciones trascendentales binarias requieren tolerancia ≥1e-12."
        )
    table = []
    warnings = []
    if f.binary_functions:
        warnings.append(
            "Trigonometría y constantes pi/e usan unas 15 cifras; el residual es aproximado."
        )
    result = {
        "expresion": f.expression,
        "metodo": method,
        "tolerancia_x": tx,
        "tolerancia_f": tf,
        "max_iteraciones": limit,
        "tabla": table,
        "cota_garantizada": None,
        "error_verdadero": None,
        "convergencia": False,
    }

    def finish(status, reason, x=None, fx=None):
        if x is not None:
            result["ultimo_punto"] = x
            ctx.emit("parada_raiz", "Leer el último punto, el residuo y el motivo de parada.",
                     {"estado": status, "motivo": reason, "ultimo_punto": x, "residuo": abs(fx)},
                     r"r=|f(x)|")
        result.update(
            motivo_parada=reason, iteraciones=len(table), convergencia=status == "ok"
        )
        if x is not None:
            text = format(decimal(x), ".14g")
            rounding = abs(F(x) - F(text))
            bound = result.get("cota_garantizada")
            result.update(
                aproximacion=x,
                aproximacion_decimal=text,
                cifras_decimal_presentacion=14,
                error_redondeo_decimal=rounding,
                cota_decimal=bound + rounding if bound is not None else None,
                residual=abs(fx),
                valor_funcion=fx,
            )
        return result, status, warnings

    def emit(row):
        row["x_decimal"] = format(decimal(row["x"]), ".14g")
        table.append(row)
        ctx.emit(
            "iteracion_raiz",
            "Iteración " + str(len(table)) + " de " + method + ".",
            row,
            row.get("desarrollo", ""),
        )
        ctx.progress(len(table) * 99 // limit)

    if method in ("biseccion", "falsa_posicion"):
        if f.polynomial is None:
            warnings.append(
                "La cota de intervalo es teórica: la evaluación aproximada de signos no certifica una cota de error verdadero."
            )
        a, b = parse_number(data["inferior"]), parse_number(data["superior"])
        result["intervalo_inicial"] = [a,b]
        if a >= b:
            raise InputError("El extremo inferior debe ser menor que el superior.")
        f.continuous(a, b)
        fa, fb = f.exact(a), f.exact(b)
        ctx.emit("continuidad","Comprobar continuidad en el intervalo y evaluar ambos extremos.",
                 {"intervalo":[a,b],"f_a":fa,"f_b":fb}, r"f(a)f(b)<0\quad\text{si ninguno es raíz}")
        for x, fx in ((a, fa), (b, fb)):
            if fx == 0:
                result["cota_garantizada"] = F(0) if f.polynomial is not None else None
                return finish(
                    "ok",
                    (
                        "raiz_en_extremo"
                        if f.polynomial is not None
                        else "residual_cero_aproximado_en_extremo"
                    ),
                    x,
                    fx,
                )
        if (fa > 0) == (fb > 0):
            raise InputError("Se requiere cambio de signo en un intervalo continuo.")
        ctx.emit("teorema","Aplicar el teorema de Bolzano.", {"teorema":{
            "enunciado":r"f\in C([a,b]),\ f(a)f(b)<0\implies\exists c\in(a,b):f(c)=0",
            "hipotesis":"Se verificó continuidad en el intervalo. Las evaluaciones tienen signos opuestos.",
            "evidencia":{"a":a,"b":b,"f_a":fa,"f_b":fb},
            "conclusion":"El cambio de signo garantiza al menos una raíz para evaluaciones de signo fiables.",
        }})
        criterion = data.get(
            "criterio", "cota" if method == "biseccion" else "residual_y_paso"
        )
        result["criterio"] = criterion
        if method == "biseccion":
            particular = (b - a) / 2
            required = 1
            while particular > tx:
                required += 1
                particular /= 2
            result["iteraciones_para_la_cota"] = required
            ctx.emit("cota_biseccion", "Comparar la cota teórica con la tolerancia y el máximo de iteraciones.",
                     {"ancho_inicial": b-a, "tolerancia": tx, "iteraciones_necesarias": required,
                      "maximo_configurado": limit, "criterio_activo": criterion},
                     r"c_k=\frac{b_0-a_0}{2^k}")
        previous = None
        for k in range(1, limit + 1):
            ctx.tick()
            denominator = decimal(fb) - decimal(fa) if method == "falsa_posicion" else F(2)
            if not denominator:
                ctx.emit("denominador_nulo", "Los valores de ambos extremos coinciden a la precisión de trabajo.",
                         {"a": a, "b": b, "fa": fa, "fb": fb, "denominador": 0})
                last = previous if previous is not None else a
                return finish("breakdown", "denominador_falsa_posicion_nulo", last, f.exact(last))
            # La bisección conserva extremos y puntos medios racionales exactos.
            # Falsa posición redondea su nuevo punto a 40 cifras para acotar crecimiento.
            x = (
                (a + b) / 2
                if method == "biseccion"
                else F(
                    decimal(a)
                    - (
                        decimal(fa)
                        * (decimal(b) - decimal(a))
                        / denominator
                    )
                )
            )
            if not a < x < b:
                return finish(
                    "stagnated",
                    "redondeo_sin_punto_interior",
                    previous if previous is not None else a,
                    f.exact(previous if previous is not None else a),
                )
            fx = f.exact(x)
            delta = abs(x - previous) if previous is not None else None
            relative = delta / abs(x) if delta is not None and x else None
            bound = (b - a) / 2 if method == "biseccion" else max(x - a, b - x)
            certified = bound if f.polynomial is not None else None
            result["cota_garantizada"] = certified
            emit(
                {
                    "iteracion": k,
                    "a": a,
                    "b": b,
                    "fa": fa,
                    "fb": fb,
                    "x": x,
                    "fx": fx,
                    "residual": abs(fx),
                    "error_aproximado_absoluto": delta,
                    "error_aproximado_relativo": relative,
                    "cota_intervalo": bound,
                    "signo_fa_por_fx": "-" if fa*fx < 0 else "+" if fa*fx > 0 else "0",
                    "intervalo_siguiente": [a, x] if fa * fx < 0 else [x, b] if fx else [x, x],
                    "decision_intervalo": "Reemplazar extremo superior" if fa * fx < 0 else
                                          "Reemplazar extremo inferior" if fx else "Valor cero",
                    "denominador": denominator,
                    "error_porcentual": 100 * relative if relative is not None else None,
                    "desarrollo": (r"x_m=\frac{(" + tex(a) + ")+(" + tex(b) + ")}{2}=" + tex(x))
                       if method=="biseccion" else
                       rf"x_r=({tex(a)})-({tex(fa)})\frac{{({tex(b)})-({tex(a)})}}{{{tex(denominator)}}}"
                       rf"\approx{format(decimal(x),'.14g')}",
                    "cota_garantizada": certified,
                }
            )
            passed = (
                bound <= tx
                if criterion == "cota"
                else (
                    abs(fx) <= tf
                    if criterion == "residual"
                    else abs(fx) <= tf
                    and (
                        bound <= tx
                        if criterion == "ambos"
                        else delta is not None and delta <= tx
                    )
                )
            )
            if criterion == "relativo":
                passed = relative is not None and relative <= tx
            if fx == 0 or passed:
                if fx == 0 and f.polynomial is not None:
                    result["cota_garantizada"] = F(0)
                return finish(
                    "ok",
                    (
                        "raiz_exacta"
                        if fx == 0 and f.polynomial is not None
                        else "criterio_satisfecho"
                    ),
                    x,
                    fx,
                )
            if previous == x:
                return finish(
                    "stagnated", "punto_repetido_con_residual_no_suficiente", x, fx
                )
            if (fa > 0) == (fx > 0):
                a, fa = x, fx
            else:
                b, fb = x, fx
            previous = x
        return finish("iteration_limit", "maximo_de_iteraciones", x, fx)
    derivative = None
    scheme = data.get("modo_derivada", "simbolica")
    x = decimal(data["inicial"])
    fx = f.value(x)
    if method == "newton":
        if scheme == "simbolica":
            derivative, source = f.derivative(data.get("derivada"))
            result.update(derivada=derivative.expression, origen_derivada=source)
            if source == "proporcionada_por_usuario":
                warnings.append("La derivada proporcionada se usa como dato. Revisá su equivalencia con f.")
        elif scheme in DIFFERENCES:
            h = step_size(data)
            result.update(origen_derivada="diferencia_"+scheme, paso_h=h)
        elif scheme == "horner":
            if not f.polynomial or max(f.polynomial) == 0:
                raise InputError("Horner requiere un polinomio de grado positivo.")
            result["origen_derivada"] = "horner"
        else:
            raise InputError("Elegí una forma válida de calcular la derivada.")
        multiplicity = integer(data.get("multiplicidad",1), "Multiplicidad",1,20)
        result["multiplicidad"] = multiplicity
        ctx.emit("derivar","Fijar el método para evaluar la pendiente y la multiplicidad.",
                 {"funcion":f.expression,"origen":result["origen_derivada"],"multiplicidad":multiplicity},
                 r"x_{k+1}=x_k-m\frac{f(x_k)}{f'(x_k)}")
        previous = None
    else:
        previous = decimal(data["anterior"])
        if previous == x:
            raise InputError("Secante requiere dos semillas distintas.")
    criterion = data.get("criterio", "residual_y_paso")
    result["criterio"] = criterion
    history = [x]
    if method == "secante" and f.value(previous) == 0:
        return finish(
            "ok", "residual_cero_en_primera_semilla", previous, f.value(previous)
        )
    if fx == 0:
        return finish("ok", "residual_cero_en_semilla", x, fx)
    if criterion == "residual" and abs(fx) <= decimal(tf):
        return finish("ok", "residual_inicial_suficiente", x, fx)
    for k in range(1, limit + 1):
        ctx.tick()
        try:
            if method == "newton":
                if scheme in DIFFERENCES:
                    denominator = difference(f, x, h, scheme, ctx)
                elif scheme == "horner":
                    _, synthetic, slope = horner(f, F(x), ctx)
                    fx, denominator = decimal(synthetic[-1]), decimal(slope)
                else:
                    denominator = derivative.value(x)
                if denominator == 0 or (abs(denominator) <= D("1e-16")*abs(fx)):
                    ctx.emit("derivada_pequena","Evaluar el denominador antes de dividir.",
                             {"x":x,"f_x":fx,"derivada":denominator})
                    return finish("breakdown", "derivada_nula_o_demasiado_pequena", x, fx)
                correction = multiplicity * fx / denominator
                next_x = x - correction
                formula = r"x_{k+1}=x_k-m\frac{f(x_k)}{f\prime(x_k)}"
                extra = {"derivada_x": denominator,
                         "desarrollo": rf"x_{{{k}}}\approx({x:.10g})-({multiplicity})\frac{{{fx:.10g}}}{{{denominator:.10g}}}\approx {next_x:.14g}"}
            else:
                old_value = f.value(previous)
                denominator = fx - old_value
                if denominator == 0:
                    ctx.emit("denominador_nulo", "Evaluar las dos ordenadas antes de dividir.",
                             {"anterior": previous, "actual": x, "f_anterior": old_value, "f_actual": fx,
                              "denominador": denominator}, r"f(x_k)-f(x_{k-1})=0")
                    return finish("breakdown", "denominador_secante_nulo", x, fx)
                next_x = x - fx * (x - previous) / denominator
                formula = r"x_{k+1}=x_k-f(x_k)(x_k-x_{k-1})/(f(x_k)-f(x_{k-1}))"
                extra = {
                    "anterior": previous,
                    "f_anterior": old_value,
                    "denominador": denominator,
                    "desarrollo": rf"x_{{{k}}}\approx({x:.10g})-({fx:.10g})"
                                  rf"\frac{{({x:.10g})-({previous:.10g})}}{{{denominator:.10g}}}\approx {next_x:.14g}",
                }
            if abs(next_x) > D("1e100"):
                raise DomainError("El iterado excede 1e100.")
            next_f = f.value(next_x)
        except DomainError as e:
            return finish("domain_error", "evaluacion_no_admitida: " + str(e), x, fx)
        delta = abs(next_x - x)
        relative = delta / abs(next_x) if next_x else None
        emit(
            {
                "iteracion": k,
                "x_anterior": x,
                "f_anterior_actual": fx,
                "x": next_x,
                "fx": next_f,
                "residual": abs(next_f),
                "error_aproximado_absoluto": delta,
                "error_aproximado_relativo": relative,
                "error_porcentual": 100*relative if relative is not None else None,
                "formula": formula,
                **extra,
            }
        )
        if abs(next_f) <= decimal(tf) and (
            criterion == "residual" or (relative <= decimal(tx) if relative is not None else delta <= decimal(tx))
            if criterion == "relativo_y_residual" else criterion == "residual" or delta <= decimal(tx)
        ):
            return finish("ok", "criterio_satisfecho", next_x, next_f)
        if next_x == x:
            return finish("stagnated", "precision_agotada", next_x, next_f)
        if next_x in history[-8:]:
            return finish("cycle_detected", "ciclo_detectado", next_x, next_f)
        previous, x, fx = x, next_x, next_f
        history.append(x)
    return finish("iteration_limit", "maximo_de_iteraciones", x, fx)
