"""Evaluación anidada, división sintética y diferencias de la sesión 22."""
from fractions import Fraction

from .functions import Function, decimal
from ..linear.context import freeze, tex
from ...domain.models import InputError
from ...parsing.numbers import parse_number


DIFFERENCES = {
    "adelante": r"\frac{f(x+h)-f(x)}{h}",
    "atras": r"\frac{f(x)-f(x-h)}{h}",
    "central": r"\frac{f(x+h)-f(x-h)}{2h}",
}


def step_size(data):
    h = decimal(data.get("paso_h", "0.01"))
    if not 0 < h <= 1:
        raise InputError("El paso h debe ser mayor que cero y menor o igual que uno.")
    return h


def difference(f, x, h, method, ctx):
    left = x if method == "adelante" else x-h
    right = x if method == "atras" else x+h
    width = right-left
    if width <= 0 or (method == "central" and (left == x or right == x)):
        raise InputError("El paso h es demasiado pequeño para distinguir los puntos vecinos.")
    lower, upper = f.value(left), f.value(right)
    slope = (upper-lower)/width
    ctx.emit("diferencia_finita", f"Estimar la pendiente por diferencia {method}.",
             {"h":h,"x_izquierda":left,"x_derecha":right,"f_izquierda":lower,
              "f_derecha":upper,"pendiente":slope,"orden":2 if method == "central" else 1},
             rf"f'(x)\approx {DIFFERENCES[method]}\approx\frac{{({upper:.12g})-({lower:.12g})}}{{{width:.12g}}}\approx {slope:.12g}")
    return slope


def difference_report(data, ctx):
    f = Function(data["expresion"], ctx)
    x, h = decimal(data["punto"]), step_size(data)
    methods = ["adelante","atras","central"] if data.get("esquema", "comparar") == "comparar" else [data["esquema"]]
    derivative, _ = f.derivative()
    reference = derivative.value(x)
    rows = []
    for method in methods:
        if method not in DIFFERENCES:
            raise InputError("Elegí un esquema de diferencia finita.")
        result = difference(f, x, h, method, ctx)
        rows.append([method, result, abs(result-reference)])
    ctx.emit("comparacion", "Contrastar con la derivada analítica y medir el error absoluto.",
             {"valor_analitico":reference}, r"E=|D_hf(x)-f'(x)|")
    return {"punto":x,"h":h,"derivada_analitica":reference,"tabla":rows,
            "encabezados":["Esquema","Derivada aproximada","Error absoluto"]}


def horner(f, x, ctx):
    if f.polynomial is None or not f.polynomial or max(f.polynomial) < 1:
        raise InputError("Ingresá un polinomio en x de grado positivo para usar Horner.")
    coefficients = [f.polynomial.get(k, Fraction(0)) for k in range(max(f.polynomial),-1,-1)]
    b, c = [coefficients[0]], [coefficients[0]]
    for coefficient in coefficients[1:]:
        b.append(freeze(coefficient+x*b[-1]))
        if len(b) < len(coefficients):
            c.append(freeze(b[-1]+x*c[-1]))
    ctx.emit("horner", "Completar los dos renglones de Horner, incluido el coeficiente de cada potencia ausente.",
             {"punto":x,"coeficientes":coefficients,"fila_b":b,"fila_c":c,"grado":len(coefficients)-1},
             rf"b_0=a_0,\ b_j=a_j+rb_{{j-1}},\quad p(r)={tex(b[-1])}")
    ctx.emit("horner_derivada", "Leer el último valor de la segunda fila como derivada evaluada.",
             {"derivada":c[-1]}, rf"c_0=b_0,\ c_j=b_j+rc_{{j-1}},\quad p'(r)={tex(c[-1])}")
    return coefficients, b, c[-1]


def horner_report(data, ctx):
    f = Function(data["expresion"], ctx)
    root = parse_number(data["punto"])
    coefficients, row, derivative = horner(f,root,ctx)
    remainder = row[-1]
    out = {"punto":root,"p":remainder,"derivada":derivative,
           "tabla":[[len(coefficients)-1-i,a,b] for i,(a,b) in enumerate(zip(coefficients,row))],
           "encabezados":["Potencia","Coeficiente","Fila b"]}
    verification = {"evaluacion_original":f.exact(root),"passed":f.exact(root) == remainder}
    if data.get("accion","evaluar") == "deflactar":
        tolerance = parse_number(data.get("tolerancia_residuo","0"))
        if not 0 <= tolerance <= 1:
            raise InputError("La tolerancia del residuo debe estar entre 0 y 1.")
        accepted = abs(remainder) <= tolerance
        quotient = row[:-1]
        reconstructed = [quotient[0]] + [quotient[i]-root*quotient[i-1] for i in range(1,len(quotient))]
        reconstructed.append(remainder-root*quotient[-1])
        out.update(residuo=remainder, division_aceptada=accepted, raiz_exacta=remainder == 0)
        if accepted:
            out["coeficientes_cociente"] = quotient
            out["formula_latex"] = r"p(x)=(x-r)q(x)+p(r)"
        ctx.emit("deflacion", "Reconstruir el polinomio original y contrastar el resto con la tolerancia.",
                 {"coeficientes_reconstruidos":reconstructed,"residuo":remainder,"tolerancia":tolerance,
                  "decision":"Aceptar la división" if accepted else "Refinar la raíz en el polinomio original"},
                 rf"p(r)={tex(remainder)},\quad |p(r)|{'\\le' if accepted else '>'}{tex(tolerance)}")
        verification.update(reconstruccion=reconstructed == coefficients,
                            residuo_admitido=accepted, passed=accepted and reconstructed == coefficients)
    return out, verification
