"""Comprobaciones del formulario compartido sobre el motor Python."""
from fractions import Fraction
import unittest

from motor_matematico.application.backend import calculate


class WorkbenchTest(unittest.TestCase):
    def test_gauss_and_jacobi_share_augmented_data(self):
        data = {"matrix":[[4,1,1],[2,3,2]]}
        gauss = calculate("sistemas.trabajo", {**data,"metodo":"gauss"})
        jacobi = calculate("sistemas.trabajo", {**data,"metodo":"jacobi"})
        self.assertEqual(gauss["result"]["particular"],["1/10","3/5"])
        self.assertTrue(all(abs(Fraction(value)-Fraction(expected)) < Fraction("1e-7")
                            for value,expected in zip(jacobi["result"]["vector"],gauss["result"]["particular"])))
        classification = calculate("sistemas.trabajo", {**data,"objetivo":"clasificar"})
        self.assertNotIn("particular", classification["result"])

    def test_school_methods_show_distinct_traces(self):
        data = {"formato":"ecuaciones","variables":"x y","ecuaciones":"4x+y=1\n2x+3y=2"}
        for method in ("sustitucion","igualacion","reduccion"):
            with self.subTest(method=method):
                answer = calculate("sistemas.trabajo", {**data,"metodo":method})
                self.assertEqual(answer["result"]["particular"],["1/10","3/5"])
                self.assertIn(method, [step["kind"] for step in answer["steps"]])
                self.assertTrue(answer["verification"]["passed"])
        singular = calculate("sistemas.trabajo", {"matrix":[[1,1,1],[2,2,3]],"metodo":"reduccion"})
        self.assertEqual(singular["result"]["clasificacion"],"incompatible")

    def test_integral_dispatch_checks_substitution(self):
        data = {"expresion":"2*x*cos(x^2)", "operacion":"integral"}
        automatic = calculate("calculo.trabajo", data)
        chosen = calculate("calculo.trabajo", {**data,"tecnica_integral":"sustitucion","sustitucion":"x^2"})
        self.assertEqual(automatic["result"]["primitiva"], "sin(x**2) + C")
        self.assertEqual(automatic["result"], chosen["result"])
        definite = calculate("calculo.trabajo", {**data,"inferior":"0","superior":"1"})
        self.assertEqual(definite["result"]["valor"],"sin(1)")
