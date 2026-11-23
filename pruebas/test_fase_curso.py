"""Casos de cierre de la guía de Álgebra y métodos de los Programas 1–9."""
from fractions import Fraction
import unittest

import sympy as sp

from backend import calculate, catalog
from motor_matematico.domain.models import DomainError
from test_procedimientos import input_example


def steps(response, kind):
    return [step for step in response["steps"] if step["kind"] == kind]


class FaseCursoTest(unittest.TestCase):
    def test_gauss_clasificacion_y_direcciones(self):
        for matrix, classification in (
            ([[2, 1, 5], [1, -1, 1]], "unica"),
            ([[1, 2, 3, 1], [2, 4, 6, 2]], "infinitas"),
            ([[1, 2, 1], [2, 4, 3]], "inconsistente"),
        ):
            with self.subTest(classification=classification):
                response = calculate("original.sistema", {"matrix": matrix})
                self.assertEqual(response["result"]["tipo"], classification)
                changed = next(s for s in steps(response, "fila_original") if "factor" in s["data"])
                self.assertEqual(changed["data"]["separador"], len(matrix[0])-1)
                self.assertIn(f",{len(matrix[0])}", changed["formula"])
                self.assertIn("ultima_fila_no_nula", steps(response, "teorema")[0]["data"]["teorema"]["evidencia"])
                if classification == "infinitas":
                    self.assertEqual(response["verification"]["Av"], [["0", "0"], ["0", "0"]])
                    self.assertTrue(response["verification"]["passed"])

    def test_dependencia_y_distributividad(self):
        r = calculate("original.relaciones", {"A": [[2, 1], [1, -1]], "u": [1, 2], "v": [2, -1], "c": "3"})
        self.assertEqual(len(steps(r, "distributividad_componente")), 2)
        self.assertTrue(steps(r, "combinacion_columnas"))
        r = calculate("espacios.polinomios", {"familia": "1+x\n2+2*x", "grado": "1"})
        self.assertEqual(steps(r, "relacion_dependencia")[0]["data"]["coeficientes"], ["-2", "1"])
        self.assertEqual(steps(r, "relacion_dependencia")[0]["data"]["combinacion"], ["0", "0"])

    def test_determinantes_e_inversa(self):
        A = [[0, 2, 0, 0, 0], [3, 1, 0, 0, 0], [0, 0, 2, 0, 0],
             [0, 0, 0, 3, 0], [0, 0, 0, 0, 4]]
        for method in ("cofactores", "reduccion"):
            response = calculate("determinantes.calcular", {"A": A, "metodo": method})
            self.assertEqual(int(response["result"]["valor"]), sp.Matrix(A).det())
            self.assertTrue(response["verification"]["passed"])
            if method == "reduccion":
                self.assertEqual(steps(response, "intercambio")[0]["data"]["factor_determinante"], -1)
                self.assertEqual(steps(response, "escala_fila")[0]["data"]["factor_determinante"], "1/3")
            else:
                self.assertTrue(any(len(step["data"]["matriz"]) == 2 for step in steps(response, "evaluar_menor")))
        self.assertEqual(calculate("determinantes.calcular", {"A": A, "metodo": "sarrus"})["status"], "not_applicable")
        for method in ("gauss_jordan", "adjugata"):
            response = calculate("matrices.inversa", {"A": A, "metodo": method})
            self.assertTrue(response["verification"]["passed"])
            singular = calculate("matrices.inversa", {"A": [[1, 2], [2, 4]], "metodo": method})
            self.assertEqual(singular["status"], "singular")
            self.assertTrue(singular["steps"])

    def test_parametros_algebraicos_y_determinante_identicamente_nulo(self):
        for expressions, ranks in [
            ("s*x+y=1\n2*x+s*y=0", (1, 2)),
            ("s*x+y=s\n2*x+s*y=2", (1, 1)),
        ]:
            r = calculate("sistemas.parametrico", {"ecuaciones": expressions, "variables": "x y", "parametro": "s"})
            case = r["result"]["casos_singulares"]["sqrt(2)"]
            self.assertEqual((case["rango_A"], case["rango_aumentada"]), ranks)
        r = calculate("sistemas.parametrico", {"ecuaciones": "s*x=1\n0*y=0", "variables": "x y", "parametro": "s"})
        self.assertEqual(r["result"]["fuera_de_los_valores_excepcionales"]["clasificacion"], "Infinitas soluciones")
        self.assertEqual(r["result"]["casos_singulares"]["0"]["clasificacion"], "Sin solución")

    def test_reutilizacion_lu_y_permuta_tardia_plu(self):
        A = [[2, 1], [4, 3]]
        lua = calculate("factorizacion.lu", {"A": A})
        state = steps(lua, "eliminacion_lu")[0]["data"]
        self.assertEqual(state["multiplicador"], "2")
        self.assertEqual(state["fila_despues"], ["0", "1"])
        B = [[4, 1, 2], [2, 1, 3], [1, 5, 4]]
        plu = calculate("factorizacion.plu", {"A": B})
        swap = steps(plu, "permutacion_plu")[-1]["data"]
        self.assertEqual(swap["columnas_previas_antes"], [["1/2"], ["1/4"]])
        self.assertEqual(swap["columnas_previas_despues"], [["1/4"], ["1/2"]])
        self.assertTrue(plu["verification"]["passed"])
        r = calculate("factorizacion.resolver", {"A": B, "b": [7, 6, 10], "metodo": "plu",
                                                "factores": plu["result"]})
        self.assertEqual(r["result"]["particular"], ["1", "1", "1"])
        self.assertTrue(r["result"]["reutilizo_factores"])
        self.assertTrue(r["verification"]["passed"])
        self.assertTrue(steps(r, "etapa_L") and steps(r, "etapa_U") and steps(r, "verificar_sistema_original"))
        with self.assertRaisesRegex(ValueError, "no corresponden"):
            calculate("factorizacion.resolver", {"A": A, "b": [1, 1],
                                               "factores": {**lua["result"], "U": [[1, 0], [0, 1]]}})

    def test_subespacios_bases_y_linealidad(self):
        good = calculate("espacios.subespacio", {"variables": "x y", "ecuaciones": "x=2*y"})
        self.assertTrue(steps(good, "cerradura_suma") and steps(good, "cerradura_escalar"))
        bad = calculate("espacios.subespacio", {"variables": "x y", "ecuaciones": "x=3"})
        self.assertEqual(steps(bad, "testigo_subespacio")[0]["data"]["requerido"], "3")
        nonlinear = calculate("transformaciones.formula", {"variables": "x", "componentes": "x^2"})
        witness = nonlinear["result"]["contraejemplo"]
        self.assertNotEqual(witness["T_del_vector_escalado"], witness["escalar_por_T"])
        notes = catalog()["operations"]["espacios.cambio_base"]
        exposed = input_example(notes)
        exposed["v"] = [2, 3]
        r = calculate("espacios.cambio_base", exposed)
        self.assertTrue(r["verification"]["passed"])
        self.assertEqual(r["verification"]["reconstruccion_destino"], ["2", "3"])
        r = calculate("espacios.fundamentales", {"A": [[1, 2], [2, 4]]})
        self.assertEqual(steps(r, "columnas_imagen")[0]["data"]["base_imagen"], [["1", "2"]])
        self.assertEqual(r["result"]["rango"] + r["result"]["nulidad"], 2)

    def test_modelos_y_error_sin_referencia_no_nula(self):
        for op in ("modelos.economia", "modelos.flujos", "modelos.balance"):
            example = input_example(catalog()["operations"][op])
            response = calculate(op, example)
            rows = steps(response, "ecuacion_modelo")
            self.assertTrue(rows)
            self.assertTrue(all(row["formula"] and row["data"]["unidades"] for row in rows))
        r = calculate("errores.redondeo", {"numero": "0", "decimales": "2", "cifras": "3"})
        self.assertIsNone(r["result"]["error_relativo_redondeo"])
        self.assertTrue(steps(r, "errores_de_aproximacion"))

    def test_jacobi_gauss_seidel_y_sor(self):
        data = {"A": [[4, 1], [2, 3]], "b": [1, 2], "max_iteraciones": "1", "norma": "uno"}
        jacobi = calculate("iterativos.jacobi", data)
        seidel = calculate("iterativos.gauss_seidel", data)
        sor = calculate("iterativos.sor", {**data, "omega": "1"})
        self.assertEqual(jacobi["result"]["vector"], ["1/4", "2/3"])
        self.assertEqual(seidel["result"]["vector"], ["1/4", "1/2"])
        self.assertEqual(sor["result"]["tabla"], seidel["result"]["tabla"])
        self.assertTrue(steps(sor, "relajacion") and steps(sor, "parada_iterativa"))
        self.assertEqual(steps(seidel, "normas_iterativas")[0]["data"]["norma"], "uno")

    def test_biseccion_newton_y_metodos_abiertos(self):
        r = calculate("raices.biseccion", {"expresion": "x^2-2", "inferior": "1", "superior": "2"})
        self.assertTrue(steps(r, "cota_biseccion"))
        self.assertEqual(r["result"]["tabla"][0]["intervalo_siguiente"], ["1", "3/2"])
        r = calculate("raices.biseccion", {"expresion": "1/x", "inferior": "-1", "superior": "1"})
        self.assertFalse(r["result"])
        r = calculate("raices.newton", {"expresion": "x^3-x-2", "inicial": "2"})
        self.assertEqual(r["result"]["origen_derivada"], "sympy")
        self.assertEqual(r["result"]["derivada"], "3*x**2 - 1")
        r = calculate("raices.newton", {"expresion": "log(x)-1", "inicial": "8"})
        self.assertAlmostEqual(float(r["result"]["aproximacion_decimal"]), 10, places=7)
        stopped = calculate("raices.newton", {"expresion": "x^2-2", "inicial": "0"})
        self.assertEqual((stopped["result"]["ultimo_punto"], stopped["result"]["residual"]), ("0", "2"))
        r = calculate("raices.secante", {"expresion": "x^2-2", "inicial": "1", "anterior": "-1"})
        self.assertTrue(steps(r, "denominador_nulo"))
        self.assertEqual(r["status"], "breakdown")
        r = calculate("raices.falsa_posicion", {"expresion": "x^2-2", "inferior": "1", "superior": "2"})
        self.assertEqual(Fraction(r["result"]["tabla"][0]["denominador"]), 3)
        self.assertTrue(steps(r, "iteracion_raiz")[0]["formula"])

    def test_a25_limites_del_catalogo(self):
        for op, definition in catalog()["operations"].items():
            with self.subTest(op=op):
                data = input_example(definition)
                if op != "original.sistema":
                    field = next(field["name"] for field in definition["fields"] if field["required"])
                    del data[field]
                try:
                    response = calculate(op, data)
                except (ValueError, KeyError, DomainError):
                    continue
                self.assertIn(response["status"], {"invalid_input", "not_applicable", "domain_error"})

    def test_a25_bloques_bases_y_conjuntos(self):
        r = calculate("matrices.particionar", {"A": [[1, 2], [3, 4]], "cortes_filas": "1", "cortes_columnas": "1"})
        self.assertEqual(len(steps(r, "extraer_bloque")), 4)
        r = calculate("conversiones.bases", {"numero": "F"*100, "base_origen": "16", "base_destino": "2"})
        self.assertEqual(r["result"]["numeral"], "1"*400)
        r = calculate("conjuntos.operar", {"A": "a\na", "universo": "a\nb", "operacion": "complemento"})
        self.assertEqual(r["result"]["conjunto"], ["b"])
        self.assertTrue(steps(r, "pertenencia_conjuntos"))
