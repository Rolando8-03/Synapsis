"""Fórmulas del resultado de Derivada y su representación copiable."""
import ast
from decimal import Decimal, localcontext
from fractions import Fraction

from ..algorithms.calculo import analizar
from ..algorithms.linear.context import tex


def number_tex(text):
    mantissa, sep, exponent = text.lower().replace("_", "").partition("e")
    return rf"{mantissa}\times 10^{{{int(exponent)}}}" if sep else mantissa


def grouped(term, minimum):
    text, priority = term
    return rf"\left({text}\right)" if priority < minimum else text


def expression_tex(tree, source="", *, at_x=None):
    """En el árbol generado, source conserva los literales y permite omitir factores neutros."""
    def visit(node):
        if isinstance(node, ast.Constant):
            literal = getattr(node, "_literal", None) or ast.get_source_segment(source, node)
            text = number_tex(literal)
            return text, 2 if r"\times" in text else 5
        if isinstance(node, ast.Name):
            if at_x is not None and node.id == "x":
                return at_x, 5
            return {"pi": r"\pi", "Ans": r"\mathrm{Ans}"}.get(node.id, node.id), 5
        if isinstance(node, ast.Call):
            name = node.func.id
            arg, _ = visit(node.args[0])
            if name == "sqrt":
                return rf"\sqrt{{{arg}}}", 5
            if name == "abs":
                return rf"\left|{arg}\right|", 5
            fn = {"asin": r"\arcsin", "acos": r"\arccos", "atan": r"\arctan",
                  "log": r"\log_{10}", "factorial": r"\operatorname{factorial}"}.get(name, "\\" + name)
            return rf"{fn}\left({arg}\right)", 4
        if isinstance(node, ast.UnaryOp):
            sign = "-" if isinstance(node.op, ast.USub) else "+"
            return sign + grouped(visit(node.operand), 4), 3

        left, right = visit(node.left), visit(node.right)
        a, b = left[0], right[0]
        if isinstance(node.op, ast.Div):
            return rf"\frac{{{a}}}{{{b}}}", 5
        if isinstance(node.op, ast.Pow):
            if source and a == "x" and b in {"0", "1"}:
                return ("1" if b == "0" else "x"), 5
            return rf"{grouped(left, 5)}^{{{b}}}", 4
        if isinstance(node.op, ast.Mult):
            if source and a == "1":
                return right
            if source and b == "1":
                return left
            join = r"\," if b.startswith("x") else r"\cdot "
            return grouped(left, 2) + join + grouped(right, 4), 2
        b = grouped(right, 2)
        if isinstance(node.op, ast.Add):
            return a + (b if b.startswith(("-", "+")) else "+" + b), 1
        if b.startswith(("-", "+")):
            b = rf"\left({b}\right)"
        return a + "-" + b, 1

    return visit(tree)[0]


def derivative_lines(data, result):
    source = data["expresion"]
    derivative = result["expresion"]
    lines = [{"texto": "f(x) = " + source, "latex": "f(x)=" + expression_tex(analizar(source, variable=True))}]
    line = {"texto": "f′(x) = " + derivative}
    # Una expansión larga puede exceder el límite de anidación del parser.
    if len(derivative) <= 16000:
        python_derivative = derivative.replace("^", "**")
        try:
            tree = ast.parse(python_derivative, mode="eval").body
            line["latex"] = "f'(x)=" + expression_tex(tree, python_derivative)
        except (SyntaxError, RecursionError):
            pass
    lines.append(line)
    if "valor" not in result:
        return lines

    point = str(data["punto"])
    value = result["valor"]
    exact = result["exactitud"] == "exacta"
    relation = "=" if exact else r"\approx "
    rhs = tex(Fraction(value)) if exact else number_tex(value)
    plain = f"f′({point}) {'=' if exact else '≈'} {value}"
    if exact and "/" in value:
        fraction = Fraction(value)
        with localcontext() as context:
            context.prec = 12
            decimal = Decimal(fraction.numerator) / Decimal(fraction.denominator)
        same = Fraction(decimal) == fraction
        rhs += ("=" if same else r"\approx ") + number_tex(str(decimal))
        plain += f" {'=' if same else '≈'} {decimal}"
    lines.append({"texto": plain, "latex": rf"f'\left({expression_tex(analizar(point))}\right){relation}{rhs}"})
    return lines
