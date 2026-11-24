from fractions import Fraction
import unittest

from motor_matematico.application.backend import calculate, catalog


class ProcedimientosDocentesTest(unittest.TestCase):
    def test_diferencias_de_la_sesion_22(self):
        out = calculate("raices.diferencias", {
            "expresion":"x^3-2*x-5","punto":"2","paso_h":"0.01",
        })["result"]
        self.assertEqual(out["derivada_analitica"], "10")
        self.assertEqual([Fraction(row[1]) for row in out["tabla"]],
                         list(map(Fraction, ("10.0601", "9.9401", "10.0001"))))
        result = calculate("raices.newton", {
            "expresion":"x^3-2*x-5","inicial":"2","modo_derivada":"central","paso_h":"0.01",
        })
        self.assertEqual(result["status"],"ok")
        self.assertEqual(Fraction(result["result"]["tabla"][0]["derivada_x"]),Fraction("10.0001"))
        self.assertIn("diferencia_finita",[step["kind"] for step in result["steps"]])
        invalid = calculate("raices.newton", {
            "expresion":"x^2-2","inicial":"2","modo_derivada":"central","paso_h":"0",
        })
        self.assertEqual(invalid["status"], "invalid_input")

    def test_horner_y_deflacion_del_polinomio_original(self):
        f = "x^5-4*x^4+5*x^3-6*x+4"
        report = calculate("raices.horner", {"expresion":f,"punto":"-1","accion":"deflactar"})
        self.assertEqual(report["result"]["coeficientes_cociente"],["1","-5","10","-10","4"])
        self.assertEqual(report["result"]["derivada"],"30")
        self.assertTrue(report["verification"]["passed"])
        rejected = calculate("raices.horner", {"expresion":f,"punto":"0","accion":"deflactar"})
        self.assertFalse(rejected["verification"]["passed"])
        self.assertNotIn("coeficientes_cociente",rejected["result"])
        root = calculate("raices.newton", {"expresion":f,"inicial":"-1.25","modo_derivada":"horner"})
        self.assertEqual(root["status"],"ok")
        self.assertAlmostEqual(float(root["result"]["aproximacion_decimal"]),-1)
        self.assertIn("horner_derivada",[step["kind"] for step in root["steps"]])

    def test_dieta_del_profesor_reconstruye_las_metas(self):
        answer = calculate("modelos.dieta", {"A":"36 51 13\n52 34 74\n0 7 1.1","b":"33 45 3"})
        self.assertEqual(answer["verification"]["aportes_g"],["33","45","3"])
        self.assertEqual([round(float(Fraction(g)),2) for g in answer["result"]["gramos"]],[27.72,39.19,23.32])
        self.assertEqual(sum(s["kind"] == "ecuacion_modelo" for s in answer["steps"]),3)
        negative = calculate("modelos.dieta", {"A":"1 1\n2 1\n0 0","b":"2 1 0"})
        self.assertFalse(negative["result"]["factible_no_negativo"])
        with self.assertRaises(ValueError):
            calculate("modelos.dieta", {"A":"1 2\n1 0","b":"33 45 3"})

    def test_fichas_de_decision_redaccion_y_datos(self):
        raw = [
            ("sistemas.trabajo",{"matrix":[[1,1,1],[2,2,3]],"objetivo":"clasificar"},"rang"),
            ("sistemas.cramer",{"A":"1 0\n0 2","b":"1 2"},"det"),
            ("espacios.fundamentales",{"A":"1 2\n2 4"},"dim"),
            ("raices.biseccion",{"expresion":"x^2-2","inferior":"1","superior":"2"},"exists"),
            ("iterativos.jacobi",{"A":"4 1\n2 3","b":"1 2"},"rho"),
        ]
        for operation, data, symbol in raw:
            with self.subTest(operation=operation):
                result = calculate(operation,data)
                cards = [s["data"]["teorema"] for s in result["steps"] if s["kind"] == "teorema"]
                card = next(card for card in cards if symbol in card["enunciado"])
                self.assertTrue(card["hipotesis"] and card["evidencia"] and card["conclusion"])
        self.assertEqual(len(catalog()["sessions"]),22)
