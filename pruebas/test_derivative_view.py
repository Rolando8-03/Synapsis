import unittest

from motor_matematico.application.backend import calculate


class DerivativeViewTest(unittest.TestCase):
    def lines(self, source, point=None):
        data = {"expresion": source}
        if point is not None:
            data["punto"] = point
        answer = calculate("calculo.derivar", data, steps=False)
        self.assertEqual(answer["status"], "ok", answer["error"])
        return answer["metadata"]["formulas_derivada"]

    def test_original_derivative_and_recurring_decimal(self):
        f, df, value = self.lines("x^2/3", "1")
        self.assertEqual(f["latex"], r"f(x)=\frac{x^{2}}{3}")
        self.assertEqual(df["latex"], r"f'(x)=\frac{2}{3}\,x")
        self.assertEqual(value["texto"], "f′(1) = 2/3 ≈ 0.666666666667")

    def test_terminating_decimal_and_approximate_evaluation(self):
        self.assertEqual(self.lines("(-x)^2", "1/8")[-1]["texto"], "f′(1/8) = 1/4 = 0.25")
        self.assertIn(r"\approx", self.lines("sin(x)", "1")[-1]["latex"])

    def test_grouping_and_omitted_point(self):
        f, df = self.lines("(-x)^2-(x-1)")
        self.assertEqual(f["latex"], r"f(x)=\left(-x\right)^{2}-\left(x-1\right)")
        self.assertTrue(df["texto"].startswith("f′(x) = "))
        self.assertEqual(self.lines("pi*x")[0]["latex"], r"f(x)=\pi\,x")
