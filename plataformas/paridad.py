"""Casos reproducibles para comparar resultados, pasos, fallos y datos de gráficos."""
import json
import math

from motor_api import invoke

CASES = (
    ("catalogo", None),
    ("calcular", {"operation": "factorizacion.lu", "input": {"A": "2 1\n4 3"}, "steps": True}),
    ("calcular", {"operation": "calculo.derivar", "input": {"expresion": "x^3"}, "steps": True}),
    ("calcular", {"operation": "raices.biseccion", "input": {"expresion": "1/x", "inferior": "-1", "superior": "1"}}),
    ("calcular", {"operation": "raices.biseccion", "input": {"expresion": "x^2-2", "inferior": "1", "superior": "2"}}),
    ("kepler", {"ley": 1, "forma": .55}),
    ("kepler/escena", {"excentricidad": .55, "semieje_b": 2.25}),
)


def reference():
    return json.loads(json.dumps([invoke(action, body)[1] for action, body in CASES]))


def compare(expected, actual, at="respuesta"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            raise AssertionError(f"{at}: estructura JSON distinta")
        for key in expected:
            compare(expected[key], actual[key], f"{at}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise AssertionError(f"{at}: longitud distinta")
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, f"{at}[{index}]")
    elif isinstance(expected, float):
        if type(actual) not in (int, float) or not math.isclose(expected, actual, rel_tol=1e-11, abs_tol=1e-12):
            raise AssertionError(f"{at}: {expected!r} ≠ {actual!r}")
    elif type(expected) is not type(actual) or expected != actual:
        raise AssertionError(f"{at}: {expected!r} ≠ {actual!r}")
