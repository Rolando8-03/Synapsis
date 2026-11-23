"""Pruebas del catálogo y de desarrollos representativos del curso."""
from fractions import Fraction
import json
import unittest

from backend import calculate, catalog


def input_example(record):
    data = {}
    for field in record["fields"]:
        value = field["default"]
        if field["kind"] == "boolean":
            value = str(value).lower() == "true"
        if value != "":
            data[field["name"]] = value
    return data


class ProceduresTest(unittest.TestCase):
    def test_each_operation_has_worked_output(self):
        definitions = catalog()
        self.assertEqual(list(range(1, 23)), [row[0] for row in definitions["sessions"]])
        for op, record in definitions["operations"].items():
            with self.subTest(op=op):
                data = input_example(record)
                if op == "original.sistema":
                    data["matrix"] = [[2, 1, 5], [1, -1, 1]]
                result = calculate(op, data)
                self.assertTrue(result.get("result"), result.get("error"))
                self.assertTrue(result["steps"])
                self.assertTrue(all(step["description"] for step in result["steps"]))
                self.assertFalse(calculate(op, data, False)["steps"])
                json.dumps(result, allow_nan=False)

    def test_links_in_the_22_sessions(self):
        data = catalog()
        for n, _, _, _, entries in data["sessions"]:
            for module, op, example in entries:
                with self.subTest(session=n, op=op):
                    self.assertIn(op, [item for _, group in data["modules"][module] for item in group])
                    fields = input_example(data["operations"][op])
                    if op == "original.sistema":
                        fields.setdefault("matrix", [[2, 1, 5], [1,-1,1]])
                    result = calculate(op, {**fields, **(example or {})})
                    self.assertTrue(result.get("result"),result.get("error"))
                    self.assertTrue(result["steps"])

    def test_matrix_product_contains_each_entry(self):
        r = calculate("matrices.producto", {"A":"1 2 3\n4 5 6","B":"1 0\n2 1\n0 3"})
        self.assertEqual([["5","11"],["14","23"]],r["result"]["matrix"])
        rows = [step for step in r["steps"] if step["kind"] == "fila_producto"]
        self.assertEqual(2,len(rows))
        self.assertIn(r"(AB)_{1,2}",rows[0]["formula"])

    def test_inverse_5x5_uses_two_sided_products(self):
        A="0 1 1 1 1\n1 1 1 0 0\n1 0 1 1 1\n1 1 2 0 0\n0 1 1 1 0"
        r=calculate("matrices.inversa",{"A":A,"metodo":"gauss_jordan"})
        self.assertEqual("ok",r["status"])
        self.assertTrue(r["verification"]["passed"])
        self.assertIn(5,[step["data"].get("separador") for step in r["steps"]])
        self.assertEqual(5,sum(step["kind"]=="fila_producto" for step in r["steps"]))

    def test_no_rhs_is_used_for_lu_only(self):
        r=calculate("factorizacion.lu",{"A":"2 1 3\n1 4 0","b":"5 1"})
        self.assertNotIn("particular",r["result"])
        self.assertTrue(r["verification"]["passed"])
        self.assertTrue(any(r"\frac" in step["formula"] for step in r["steps"]))

    def test_homogeneous_parameters_and_rank(self):
        r=calculate("original.sistema",{"matrix":[[1,2,3,4,5,10],[0,1,1,1,1,3],[0,0,1,2,3,4],[0,0,0,1,1,2]]})
        self.assertEqual([4],r["result"]["variables_libres"])
        self.assertEqual(4,r["result"]["rango_A"])
        self.assertTrue(r["result"]["latex_solucion"])
        self.assertTrue(any(s["kind"]=="sustitucion" for s in r["steps"]))

    def test_linearity_has_both_proofs(self):
        r=calculate("transformaciones.formula",{"variables":"x y z","componentes":"0\ny-z"})
        self.assertEqual((1,2),(r["result"]["rango"],r["result"]["nulidad"]))
        self.assertTrue({"aditividad","homogeneidad","rango_nulidad"} <= {s["kind"] for s in r["steps"]})

    def test_bisection_six_iterations_or_relative_tolerance(self):
        data={"expresion":"x^4-5*x^2+4","inferior":"0.6","superior":"1.2","tolerancia_x":"0.015",
              "max_iteraciones":"6","criterio":"relativo"}
        r=calculate("raices.biseccion",data)
        rows=r["result"]["tabla"]
        self.assertLessEqual(len(rows),6)
        self.assertIsNone(rows[0]["error_porcentual"])
        self.assertTrue(all(row["signo_fa_por_fx"] in ("+","-","0") for row in rows))
        self.assertTrue(r["result"]["grafico_raiz"])
        if r["status"]=="ok" and rows[-1]["error_porcentual"] is not None:
            self.assertLessEqual(Fraction(rows[-1]["error_porcentual"]),Fraction(3,2))

    def test_bisection_reference_and_domain(self):
        args={"expresion":"x^2-2","inferior":"1","superior":"2"}
        result=calculate("raices.biseccion",args)
        reference=result["verification"]["contraste_independiente"]
        self.assertLess(float(reference["diferencia_absoluta"]),2e-8)
        self.assertEqual("invalid_input",calculate("raices.biseccion",{**args,"expresion":"x^2+1"})["status"])
        interrupted=calculate("raices.biseccion",{"expresion":"1/x","inferior":"-1","superior":"1"})
        self.assertFalse(interrupted["result"])

    def test_Newton_convergence_failures_and_multiplicity(self):
        r=calculate("raices.newton",{"expresion":"(x-1)^3","inicial":"1.75","multiplicidad":"3"})
        self.assertAlmostEqual(1,float(r["result"]["aproximacion_decimal"]))
        self.assertTrue(r["result"]["grafico_raiz"]["tangents"])
        self.assertTrue(any(s["kind"]=="iteracion_raiz" for s in r["steps"]))
        zero=calculate("raices.newton",{"expresion":"x^2-2","inicial":"0"})
        self.assertEqual("breakdown",zero["status"])
        self.assertIn("derivada",zero["result"]["motivo_parada"])
        limit=calculate("raices.newton",{"expresion":"x^2-2","inicial":"1","max_iteraciones":"1"})
        self.assertEqual("iteration_limit",limit["status"])

    def test_comparison_reorders_without_changing_reference(self):
        data={"A":"1 4\n5 1","b":"6 7","reordenar":True}
        r=calculate("iterativos.comparar",data)
        self.assertEqual([2,1],r["result"]["diagnostico"]["orden_de_filas"])
        self.assertTrue(r["result"]["jacobi"]["convergencia"])
        self.assertTrue(r["result"]["gauss_seidel"]["convergencia"])
        self.assertTrue(r["result"]["series"]["points"])
        self.assertTrue(any(r"\begin{aligned}" in step["formula"] for step in r["steps"]))


if __name__=="__main__":
    unittest.main()
