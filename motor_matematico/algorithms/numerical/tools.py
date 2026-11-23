"""Errores, bases posicionales y conjuntos finitos: operaciones exactas."""

from fractions import Fraction as F
import re
from ..linear.context import integer, tex
from ...domain.models import InputError
from ...parsing.numbers import parse_number

DIGITS = "0123456789ABCDEF"


def errors(data, ctx):
    value = parse_number(data["aproximado"])
    result = {"valor_aproximado": value}
    if "referencia" not in data and "anterior" not in data:
        raise InputError("Indicá una referencia o la aproximación anterior.")
    for field, prefix in [
        ("referencia", "respecto_referencia"),
        ("anterior", "aproximado"),
    ]:
        if field not in data:
            continue
        other = parse_number(data[field])
        absolute = abs(value - other)
        denominator = abs(other) if field == "referencia" else abs(value)
        result[prefix] = {
            "error_con_signo": other - value if field == "referencia" else value - other,
            "absoluto": absolute,
            "relativo": absolute / denominator if denominator else None,
            "porcentual": 100 * absolute / denominator if denominator else None,
            "porcentual_con_signo": 100 * (other - value) / other if field == "referencia" and other else None,
            "denominador": denominator,
            "motivo_no_definido": None if denominator else "denominador_cero",
        }
        description = ("Comparar contra la referencia." if field == "referencia"
                       else "Medir el cambio desde la aproximación anterior.")
        relative = (rf",\quad e_r=\frac{{{tex(absolute)}}}{{{tex(denominator)}}}"
                    rf"={tex(absolute/denominator)}" if denominator else
                    r",\quad e_r\text{ indefinido: denominador cero}")
        ctx.emit("medidas_error", description, result[prefix],
                 rf"E_a=|({tex(value)})-({tex(other)})|={tex(absolute)}" + relative)
    return result


def parse_positional(text, base, limit=256):
    if not isinstance(text, str) or len(text) > limit:
        raise InputError(f"Escribí un numeral de hasta {limit} caracteres.")
    text = text.strip().upper()
    match = re.fullmatch(
        r"([+-]?)([0-9A-F]+)(?:\.([0-9A-F]*)(?:\(([0-9A-F]+)\))?)?", text
    )
    if not match:
        raise InputError("Numeral no admitido. Ejemplo periódico: 0.(3).")
    sign, whole, frac, repeat = match.groups()
    frac = frac or ""
    repeat = repeat or ""
    if any(DIGITS.index(c) >= base for c in whole + frac + repeat):
        raise InputError("El numeral contiene un dígito ajeno a su base.")
    total = F(int(whole, base)) + (
        F(int(frac, base), base ** len(frac)) if frac else F(0)
    )
    if repeat:
        total += F(int(repeat, base), base ** len(frac) * (base ** len(repeat) - 1))
    return -total if sign == "-" else total, (whole, frac, repeat)


def whole_digits(value, base):
    if not value:
        return "0"
    out = ""
    while value:
        value, r = divmod(value, base)
        out = DIGITS[r] + out
    return out


def convert(data, ctx):
    source = integer(data["base_origen"], "Base origen")
    target = integer(data["base_destino"], "Base destino")
    if source not in (2, 8, 10, 16) or target not in (2, 8, 10, 16):
        raise InputError("Bases admitidas: 2,8,10,16.")
    precision = integer(data.get("precision", 16), "Dígitos fraccionarios", 1, 64)
    value, parts = parse_positional(data["numero"], source)
    absolute = abs(value)
    whole = absolute.numerator // absolute.denominator
    ctx.emit("desarrollo_posicional", "Calcular el valor racional y separar la parte entera.",
             {"numeral": data["numero"], "base": source, "valor": value, "parte_entera_magnitud": whole})
    quotient = whole
    while quotient:
        following, digit = divmod(quotient, target)
        ctx.emit("division_base", "Dividir la parte entera y leer los residuos de abajo hacia arriba.",
                 {"dividendo": quotient, "base": target, "cociente": following, "digito": DIGITS[digit]},
                 rf"{quotient}=({following})({target})+{digit}")
        quotient = following
    remainder = absolute.numerator % absolute.denominator
    seen = {}
    fraction = ""
    repeat_at = None
    while remainder and len(fraction) < precision:
        ctx.tick()
        if remainder in seen:
            repeat_at = seen[remainder]
            break
        seen[remainder] = len(fraction)
        remainder *= target
        digit, remainder = divmod(remainder, absolute.denominator)
        fraction += DIGITS[digit]
        ctx.emit(
            "digito_base",
            "Multiplicar el residuo por la base destino.",
            {"posicion": len(fraction), "digito": DIGITS[digit], "residuo": F(remainder)},
        )
    if remainder in seen and remainder:
        repeat_at = seen[remainder]
    exact = remainder == 0 or repeat_at is not None
    if repeat_at is not None:
        fraction = fraction[:repeat_at] + "(" + fraction[repeat_at:] + ")"
    text = (
        ("-" if value < 0 else "")
        + whole_digits(whole, target)
        + ("." + fraction if fraction else "")
    )
    reconstructed, _ = parse_positional(text, target, limit=1100)
    error = abs(value - reconstructed)
    bound = F(0) if exact else F(1, target**precision)
    whole, frac, rep = parts
    terms = [
        {
            "digito": c,
            "exponente": len(whole) - 1 - i,
            "aporte": F(DIGITS.index(c)) * source ** (len(whole) - 1 - i),
        }
        for i, c in enumerate(whole)
    ]
    terms += [
        {
            "digito": c,
            "exponente": -i - 1,
            "aporte": F(DIGITS.index(c), source ** (i + 1)),
        }
        for i, c in enumerate(frac)
    ]
    return {
        "representacion": text + " (base " + str(target) + ")",
        "numeral": text,
        "base_origen": source,
        "base_destino": target,
        "valor_racional": value,
        "desarrollo_posicional_magnitud": terms,
        "periodo_origen": rep or None,
        "signo": -1 if value < 0 else 1,
        "aporte_periodico_magnitud": (
            F(int(rep, source), source ** len(frac) * (source ** len(rep) - 1))
            if rep
            else F(0)
        ),
        "exacta": exact,
        "precision_fraccionaria": precision,
        "valor_conversion_inversa": reconstructed,
        "error_absoluto_conversion": error,
        "cota_garantizada_conversion": bound,
        "comprobacion_inversa": reconstructed == value if exact else error < bound,
    }


def finite_set(value):
    if isinstance(value, str):
        value = (
            []
            if value.strip() == "[]"
            else [x.strip() for x in value.splitlines() if x.strip()]
        )
    if (
        not isinstance(value, list)
        or len(value) > 100
        or any(not isinstance(x, str) or not x or len(x) > 100 for x in value)
    ):
        raise InputError(
            "Usá hasta 100 etiquetas de texto de hasta 100 caracteres, una por línea; [] indica vacío."
        )
    return set(value)


def sets(data, ctx):
    A = finite_set(data["A"])
    B = finite_set(data.get("B", "[]"))
    method = data.get("operacion", "union")
    U = finite_set(data["universo"]) if "universo" in data else None
    if U is not None and not (A | B) <= U:
        raise InputError("El universo debe contener los conjuntos proporcionados.")
    operations = {
        "union": lambda: A | B,
        "interseccion": lambda: A & B,
        "diferencia": lambda: A - B,
        "diferencia_simetrica": lambda: A ^ B,
        "complemento": lambda: U - A if U is not None else None,
        "producto_cartesiano": lambda: [[a, b] for a in sorted(A) for b in sorted(B)],
    }
    if method == "complemento" and U is None:
        raise InputError("El complemento requiere universo explícito.")
    if len(A) * len(B) > 2500 and method == "producto_cartesiano":
        raise InputError("El producto cartesiano admite hasta 2500 pares.")
    result = operations[method]()
    result = sorted(result) if isinstance(result, set) else result
    ctx.tick(max(1, len(result)))
    formulas = {
        "union": r"x\in A\cup B\iff x\in A\lor x\in B",
        "interseccion": r"x\in A\cap B\iff x\in A\land x\in B",
        "diferencia": r"x\in A\setminus B\iff x\in A\land x\notin B",
        "diferencia_simetrica": r"A\triangle B=(A\setminus B)\cup(B\setminus A)",
        "complemento": r"x\in U\setminus A\iff x\in U\land x\notin A",
        "producto_cartesiano": r"(a,b)\in A\times B\iff a\in A\land b\in B",
    }
    if method != "producto_cartesiano":
        selected = set(result)
        candidates = U if method == "complemento" else A | B
        ctx.emit("pertenencia_conjuntos", "Comprobar qué etiquetas cumplen la condición.",
                 {"etiquetas": [{"etiqueta": x, "en_A": x in A, "en_B": x in B, "en_resultado": x in selected}
                                for x in sorted(candidates)]}, formulas[method])

    ctx.emit(
        "conjuntos",
        "Aplicar la operación a etiquetas únicas, con universo explícito cuando corresponde.",
        {"A": sorted(A), "B": sorted(B), "resultado": result}, formulas[method],
    )
    return {
        "conjunto": result,
        "cardinalidad": len(result),
        "A_subconjunto_B": A <= B,
        "A_igual_B": A == B,
        "A_subconjunto_propio_B": A < B,
        "disjuntos": A.isdisjoint(B),
        "operacion": method,
        "universo": sorted(U) if U is not None else None,
    }
