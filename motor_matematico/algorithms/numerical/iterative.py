"""Jacobi, Gauss-Seidel y SOR con estimadores y criterios separados."""

from fractions import Fraction as F
from .functions import decimal
from ..linear.context import matrix, vector, integer, matvec, freeze, identity, tex
from ..linear.worked import dot_formula
from ...domain.models import InputError
from ...parsing.numbers import parse_number


def norm(v, kind):
    if kind == "infinito":
        return max((abs(x) for x in v), default=F(0))
    if kind == "uno":
        return sum(map(abs, v), F(0))
    return F(decimal(sum((x * x for x in v), F(0))).sqrt())


def iterative(method, data, ctx):
    A = matrix(data["A"], square=True)
    n = len(A)
    b = vector(data["b"], n)
    if any(A[i][i] == 0 for i in range(n)):
        raise InputError(
            "La diagonal debe ser no nula; no se permutan filas automáticamente."
        )
    x = vector(data["inicial"], n) if "inicial" in data else [F(0)] * n
    atol = parse_number(data.get("tolerancia_absoluta", "1e-8"))
    rtol = parse_number(data.get("tolerancia_relativa", "1e-8"))
    if not F(1, 10**24) <= atol <= 1 or not 0 <= rtol <= 1:
        raise InputError("Tolerancia absoluta 1e-24…1 y relativa 0…1.")
    limit = integer(data.get("max_iteraciones", 100), "Máximo de iteraciones", 1, 200)
    kind = data.get("norma", "infinito")
    criterion = data.get("criterio", "paso_y_residual")
    forward = method in ("gauss_seidel", "sor")
    omega = parse_number(data.get("omega", "1")) if method == "sor" else F(1)
    if not 0 < omega < 2:
        raise InputError("El factor de relajación debe satisfacer 0 < ω < 2.")
    dominant = all(
        abs(A[i][i]) > sum((abs(A[i][j]) for j in range(n) if j != i), F(0))
        for i in range(n)
    )

    def update(old, rhs, details=None, k=0):
        current = old[:]
        for i in range(n):
            ctx.tick(n)
            terms = sum(
                (
                    A[i][j]
                    * (current[j] if forward and j < i else old[j])
                    for j in range(n)
                    if j != i
                ),
                F(0),
            )
            raw = (rhs[i] - terms)/A[i][i]
            current[i] = freeze((1-omega)*old[i] + omega*raw)
            if details is not None:
                coefficients = [A[i][j] for j in range(n) if j != i]
                sources = [current[j] if forward and j < i else old[j] for j in range(n) if j != i]
                # Los decimalizados son de lectura; el motor conserva el iterado racional.
                subtotal = dot_formula(coefficients,sources)
                formula = rf"\frac{{{tex(rhs[i])}-({subtotal})}}{{{tex(A[i][i])}}}"
                if omega != 1:
                    formula = rf"({tex(1-omega)})({tex(old[i])})+({tex(omega)})" + formula
                value = format(decimal(current[i]),".12g")
                sources_text = r",\;".join(
                    rf"x_{{{j+1}}}^{{({k if forward and j < i else k-1})}}={tex(current[j] if forward and j < i else old[j])}"
                    for j in range(n) if i != j and A[i][j]
                )
                line = rf"x_{{{i+1}}}^{{({k})}}&={formula}\approx {value}"
                if sources_text:
                    line += rf"\quad\bigl({sources_text}\bigr)"
                details.append(line)
        return current

    # Matriz de iteración exacta. Su norma infinito <1 es suficiente, no necesaria.
    images = [update(e, [F(0)] * n) for e in identity(n)]
    T = [list(row) for row in zip(*images)]
    q = max(sum(map(abs, row), F(0)) for row in T)
    if method != "sor":
        margins = [abs(A[i][i])-sum(abs(A[i][j]) for j in range(n) if j != i) for i in range(n)]
        ctx.emit("teorema", "Revisar la dominancia diagonal estricta.", {"teorema":{
            "enunciado":r"\forall i:\ |a_{ii}|>\sum_{j\ne i}|a_{ij}|\implies\text{ convergencia}",
            "hipotesis":"A es cuadrada, de diagonal no nula. El método es Jacobi o Gauss-Seidel.",
            "evidencia":{"margen_por_fila":margins},
            "conclusion":"Se cumple la condición suficiente." if dominant else
                         "Los márgenes no bastan para decidir la convergencia.",
        }})
    spectrum = None
    if n <= 4 and ctx.collect_steps:
        import sympy as sp
        try:
            eigenvalues = sp.Matrix(T).eigenvals()
            if eigenvalues:
                spectrum = format(max(abs(complex(value.evalf(20))) for value in eigenvalues), ".12g")
        except (ValueError, ArithmeticError, NotImplementedError, sp.MatrixError):
            pass
    conclusion = ("La norma infinito menor que uno certifica que el radio es menor que uno." if q < 1
                  else "La norma infinito no permite certificar esta condición.")
    if spectrum is not None:
        conclusion += " El radio mostrado es una estimación numérica."
    ctx.emit("teorema","Interpretar el criterio del radio espectral.", {"teorema":{
        "enunciado":r"x^{(k+1)}=Gx^{(k)}+c\text{ converge para toda semilla}\iff \rho(G)<1",
        "hipotesis":"La iteración es lineal estacionaria y G se construyó con el método seleccionado.",
        "evidencia":{"matriz_iteracion":T,"norma_infinito":q,"radio_espectral_estimado":spectrum},
        "conclusion":conclusion,
    }}, rf"\rho(G)\le\lVert G\rVert_\infty={tex(q)}")
    table = []
    history = []
    warnings = []
    if kind == "dos":
        warnings.append(
            "La norma dos se aproxima con Decimal de 40 cifras; la cota certificada, si existe, corresponde a norma infinito."
        )
    if not dominant:
        warnings.append(
            "No hay dominancia diagonal estricta; esto no demuestra divergencia."
        )
    if q >= 1:
        warnings.append(
            "No se obtuvo una cota por contracción en norma infinito; el método puede converger."
        )
    result = {
        "metodo": method,
        "norma": kind,
        "criterio": criterion,
        "omega": omega if method == "sor" else None,
        "vector_afin": update([F(0)] * n, b),
        "inicial": x[:],
        "dominancia_diagonal_estricta": dominant,
        "norma_infinito_matriz_iteracion": q,
        "matriz_iteracion": T,
        "contraccion_suficiente": q < 1,
        "tolerancia_absoluta": atol,
        "tolerancia_relativa": rtol,
        "max_iteraciones": limit,
        "tabla": table,
        "cota_garantizada": None,
        "norma_cota_garantizada": "infinito",
        "error_verdadero": None,
    }

    def residual(v):
        return [a - c for a, c in zip(matvec(A, v, ctx), b)]

    reference = vector(data["referencia"], n) if "referencia" in data else None
    if reference is not None and any(residual(reference)):
        raise InputError(
            "La referencia debe satisfacer Ax=b exactamente para llamarla solución de referencia."
        )

    def finish(status, reason, v, r):
        ctx.emit("parada_iterativa", "Leer el motivo observado de parada y el residuo final.",
                 {"estado": status, "motivo": reason, "norma": kind, "residuo": r,
                  "norma_residual": norm(r, kind), "iteraciones": len(table)})
        result.update(
            vector=v,
            residual=r,
            norma_residual=norm(r, kind),
            iteraciones=len(table),
            convergencia=status == "ok",
            motivo_parada=reason,
        )
        if reference is not None:
            result["error_verdadero_por_componente_pct"] = [
                100*abs(a-c)/abs(c) if c else None for a,c in zip(v,reference)
            ]
            result["error_verdadero"] = norm(
                [a - c for a, c in zip(v, reference)], kind
            )
        return result, status, warnings

    ctx.emit("despejar","Aislar la incógnita diagonal en cada ecuación.",
             {"matriz":A,"b":b,"vector_inicial":x,"usa_componentes_nuevas":forward},
             r"x_i=\frac{b_i-\sum_{j\ne i}a_{ij}x_j}{a_{ii}}")
    if method == "sor":
        ctx.emit("relajacion", "Mezclar la componente anterior con la propuesta de Gauss-Seidel.",
                 {"omega": omega, "equivale_a_gauss_seidel": omega == 1},
                 r"x_i^{(k+1)}=(1-\omega)x_i^{(k)}+\omega\widehat{x}_i^{(k+1)}")
    ctx.emit("contraccion", "La contracción en norma infinito es una condición suficiente.",
             {"norma_infinito_T": q, "contraccion_suficiente": q < 1,
              "dominancia_diagonal_estricta": dominant}, r"\|T\|_\infty<1\implies\text{convergencia}")
    r = residual(x)
    threshold = atol + rtol * norm(b, kind)
    if not any(r) or (criterion == "solo_residual" and norm(r, kind) <= threshold):
        return finish("ok", "residual_inicial_suficiente", x, r)
    for k in range(1, limit + 1):
        details = [] if ctx.collect_steps else None
        new = update(x, b, details, k)
        r = residual(new)
        diff = [a-c for a,c in zip(new,x)]
        delta = norm(diff, kind)
        nr = norm(r, kind)
        current_norm = norm(new, kind)
        relative = delta / current_norm if current_norm else None
        pct = [100*abs(change/value) if value else None for change,value in zip(diff,new)]
        step_threshold = atol + rtol * current_norm
        bound = (
            q / (1 - q) * norm([a - c for a, c in zip(new, x)], "infinito")
            if q < 1
            else None
        )
        result["cota_garantizada"] = bound
        row = {
            "iteracion": k,
            "anterior": x[:],
            "vector": new[:],
            "residual": r,
            "norma_residual": nr,
            "error_aproximado_absoluto": delta,
            "error_aproximado_relativo": relative,
            "error_por_componente_pct": pct,
            "vector_decimal": [format(decimal(item),".12g") for item in new],
            "norma_residual_decimal": format(decimal(nr),".8g"),
            "umbral_paso": step_threshold,
            "umbral_residual": threshold,
            "cota_error_infinito": bound,
        }
        table.append(row)
        if details is not None:
            ctx.emit("iteracion_sistema",f"Sustituir las componentes de la iteración {k}.",
                     {**row, "norma": kind, "cambio": diff}, r"\begin{aligned}"+r"\\".join(details)+r"\end{aligned}")
            ctx.emit("normas_iterativas", "Medir el cambio y el residuo en la norma elegida.",
                     {"norma": kind, "cambio": diff, "residuo": r, "norma_del_cambio": delta,
                      "norma_del_residuo": nr, "umbral_paso": step_threshold, "umbral_residual": threshold},
                     r"\Delta x=x^{(k)}-x^{(k-1)},\quad r=Ax^{(k)}-b")
        ctx.progress(k * 99 // limit)
        checks = {
            "paso_y_residual": delta <= step_threshold and nr <= threshold,
            "paso_absoluto": delta <= atol,
            "relativo_vectorial": relative is not None and relative <= rtol,
            "porcentaje_por_componente": all(
                (value <= 100*rtol if value is not None else change == 0)
                for value,change in zip(pct,diff)
            ),
            "solo_residual": nr <= threshold,
        }
        if not any(r) or checks[criterion]:
            return finish("ok", "criterio_satisfecho", new, r)
        if new == x:
            return finish(
                "stagnated", "iterado_repetido_con_residual_no_suficiente", new, r
            )
        if new in history[-8:]:
            return finish("cycle_detected", "ciclo_detectado", new, r)
        history.append(x)
        x = new
    return finish("iteration_limit", "maximo_de_iteraciones", x, r)
