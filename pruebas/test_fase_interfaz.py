"""Regresiones del contrato entre el área de trabajo y el motor."""
import unittest

from backend import calculate


class FaseInterfazTest(unittest.TestCase):
    def test_operadores_exactos(self):
        for expression, point, side, expected in (
            ("(x^2-1)/(x-1)", "1", "-", "2"),
            ("1/x", "0", "-", "-oo"),
            ("1/x", "0", "+", "oo"),
        ):
            result = calculate("calculo.limite_lateral", {
                "expresion": expression, "punto": point, "lado": side,
            })
            self.assertEqual(result["result"]["limite"], expected)
        for variable, expected in (("x", "2*x*y"), ("y", "x**2")):
            result = calculate("calculo.derivada_parcial", {
                "expresion": "x^2*y", "variable": variable,
            })
            self.assertEqual(result["result"]["derivada"], expected)
        result = calculate("calculo.sumatoria", {"expresion": "k^2", "inferior": "-1", "superior": "3"})
        self.assertEqual(result["result"]["valor"], "15")

    def test_biseccion_conserva_los_indices_despues_de_24(self):
        result = calculate("raices.biseccion", {
            "expresion": "x^2-2", "inferior": "1", "superior": "2", "tolerancia_x": "1e-12",
        })
        table = result["result"]["tabla"]
        self.assertGreater(len(table), 24)
        indices = [row["iteracion"] for row in table]
        self.assertEqual([point[0] for point in result["result"]["grafico_raiz"]["iteraciones"]], indices)
        self.assertEqual([step["data"]["iteracion"] for step in result["steps"]
                          if step["kind"] == "iteracion_raiz"], indices)

    def test_ficha_de_invertibilidad_usa_la_evidencia_del_resultado(self):
        for matrix, expected in (("1 2\n2 4", False), ("1 2\n0 1", True)):
            response = calculate("matrices.teorema_invertible", {"A": matrix})
            card, = (step["data"]["teorema"] for step in response["steps"] if step["kind"] == "teorema")
            self.assertEqual(card["evidencia"]["determinante"], response["result"]["determinante"])
            self.assertEqual(response["result"]["invertible"], expected)
