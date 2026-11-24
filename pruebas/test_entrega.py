"""Comprueba las referencias independientes registradas en COBERTURA."""
import unittest

from motor_matematico.application.backend import calculate
from motor_matematico.domain.models import DomainError, InputError, ResourceLimitError
from pruebas.entrega.casos import ALGEBRA, CALCULUS, CASES


def field_at(result, key):
    for part in key.split("."):
        result = result[part]
    return result


class DeliveryCases(unittest.TestCase):
    def test_examples_and_procedures(self):
        self.assertEqual((len(ALGEBRA), len(CALCULUS)), (22,31))
        for case in CASES:
            with self.subTest(topic=case.reference):
                result = calculate(case.route.split("/")[1], case.inputs)
                self.assertEqual(result["status"], case.status)
                self.assertTrue(result["steps"])
                for key, value in case.expected.items():
                    self.assertEqual(field_at(result["result"], key), value)
                for key in case.absent:
                    self.assertNotIn(key, result["result"])
                if case.absent:
                    self.assertIn(r"\int_{0}^{1}", result["result"]["formula_latex"])

    def test_algebra_boundaries(self):
        for case in ALGEBRA:
            with self.subTest(topic=case.reference):
                try:
                    answer = calculate(case.route.split("/")[1], {**case.inputs, **case.failure})
                except (DomainError, InputError, ResourceLimitError, ValueError, ArithmeticError):
                    self.assertTrue(case.rejected)
                else:
                    if case.rejected:
                        self.assertNotIn(answer["status"], ("ok", "infinite"))
                        self.assertTrue(answer["error"]["message"])
                    else:
                        for key, value in case.invalid.items():
                            self.assertEqual(field_at(answer["result"], key), value)


if __name__ == "__main__":
    unittest.main()
