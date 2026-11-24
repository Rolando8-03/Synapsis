"""Cierres de la guía C01–C18 por la entrada habitual del motor."""
from fractions import Fraction
import unittest

from motor_matematico.application.backend import calculate, catalog
from motor_matematico.domain.models import DomainError


def solve(name, **data):
    return calculate("calculo." + name, data)["result"]


class CalculoITest(unittest.TestCase):
    def test_dominio_y_composicion_no_pierden_exclusiones(self):
        for expression, expected in [
            ("(x^2-1)/(x-1)", "Union(Interval.open(-oo, 1), Interval.open(1, oo))"),
            ("sqrt(x-2)", "Interval(2, oo)"),
            ("ln(x)/(x-1)", "Union(Interval.open(0, 1), Interval.open(1, oo))"),
            ("x^-2", "Union(Interval.open(-oo, 0), Interval.open(0, oo))"),
            ("1/(1/x)", "Union(Interval.open(-oo, 0), Interval.open(0, oo))"),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(solve("dominio", expresion=expression)["dominio"], expected)
        self.assertEqual(solve("composicion", exterior="sqrt(x)", interior="x-2", punto="3")["valor"], "1")
        with self.assertRaises(DomainError):
            solve("composicion", exterior="sqrt(x)", interior="x-2", punto="1")

    def test_ramas_inversas(self):
        for a,b,result in [("0","2","sqrt(y)"),("-2","0","-sqrt(y)")]:
            self.assertEqual(solve("inversa", expresion="x^2", inferior=a, superior=b)["inversa"], result)
        self.assertEqual(solve("inversa", expresion="x^2+2*x+2", inferior="-4", superior="-1")["inversa"],
                         "-sqrt(y - 1) - 1")
        with self.assertRaises(DomainError):
            solve("inversa", expresion="x^2", inferior="-2", superior="2")

    def test_limites_y_continuidad(self):
        result = solve("limite_lateral", expresion="1+x", derecha="2-x", punto="0", lado="ambos")
        self.assertEqual((result["izquierda"],result["derecha"],result["limite_bilateral"]), ("1","2",None))
        result = solve("limite_lateral", expresion="sqrt(x)", punto="0", lado="ambos")
        self.assertEqual((result["izquierda"],result["derecha"]), (None,"0"))
        options = {"expresion":"(x^2-1)/(x-1)", "punto":"1"}
        self.assertEqual(solve("limite_factorizacion", **options)["limite"], "2")
        self.assertFalse(solve("continuidad", **options)["continua"])
        self.assertTrue(solve("continuidad", **options, valor_punto="2")["continua"])
        self.assertEqual(solve("limite_racionalizacion", expresion="(sqrt(x+1)-1)/x", punto="0")["limite"], "1/2")
        self.assertEqual(solve("limite_infinito", expresion="1/x", punto="0", lado="-")["limite"], "-oo")
        self.assertEqual(solve("limite_al_infinito", expresion="(2*x^2+1)/(x^2-3)", lado="+")["limite"], "2")

    def test_reglas_e_implicita(self):
        cases = (
            ("definicion","x^2","2*x"), ("cadena","(x^2+1)^3","6*x*(x**2 + 1)**2"),
            ("producto","x*exp(x)","(x + 1)*exp(x)"), ("cociente","x/(x+1)","(x + 1)**(-2)"),
            ("exponencial","exp(2*x)","2*exp(2*x)"), ("logaritmica","ln(x^2+1)","2*x/(x**2 + 1)"),
            ("trigonometrica","sin(x^2)","2*x*cos(x**2)"),
        )
        for rule,expression,expected in cases:
            with self.subTest(rule=rule):
                self.assertEqual(solve("derivada_"+rule, expresion=expression)["derivada"], expected)
        self.assertEqual(solve("derivada_implicita", izquierda="x^2+y^2", derecha="1")["derivada"], "-x/y")
        self.assertEqual(solve("derivada_parcial", expresion="x^2*y", variable="y")["derivada"], "x**2")
        self.assertEqual(solve("parcial_sucesiva", expresion="x^2*y", orden="x y")["derivada"], "2*x")

    def test_criticos_signos_y_optimizacion(self):
        self.assertEqual(solve("criticos", expresion="abs(x)")["numeros_criticos"], "{0}")
        self.assertEqual(solve("criticos", expresion="1/x")["numeros_criticos"], "EmptySet")
        self.assertEqual(solve("signos", expresion="x^3-3*x")["inflexiones"], ["0"])
        self.assertFalse(solve("signos", expresion="x^4")["inflexiones"])
        data = {"expresion":"x^2-4*x","inferior":"0","superior":"5"}
        self.assertNotIn("minimo", solve("optimizacion", **data, entrega="plantear"))
        result = solve("optimizacion", **data, entrega="resolver")
        self.assertEqual((result["minimo"],result["maximo"]), ("-4","5"))
        self.assertEqual(solve("hessiano", expresion="x^2-y^2", x="0", y="0")["clasificacion"], "Punto silla")
        self.assertEqual(solve("hessiano", expresion="x^4+y^4", x="0", y="0")["clasificacion"], "Prueba inconclusa")

    def test_tasas_y_teoremas(self):
        self.assertEqual(solve("tasa_media", expresion="x^2", inferior="1", superior="3")["valor"], "4")
        self.assertEqual(solve("tasa_instantanea", expresion="x^2", punto="3")["valor"], "6")
        self.assertEqual(solve("tasas_relacionadas", expresion="x^2+y^2-25", x="3", y="4", tasa_x="2")["valor"], "-3/2")
        self.assertEqual(solve("elasticidad", expresion="12-x", punto="4")["valor"], "-1/2")
        limits = {"inferior":"-1","superior":"1"}
        self.assertFalse(solve("rolle", **limits, expresion="abs(x)", entrega="resolver")["hipotesis_satisfechas"])
        self.assertNotIn("puntos", solve("rolle", **limits, expresion="x^2", entrega="plantear"))
        self.assertEqual(solve("rolle", **limits, expresion="x^2", entrega="resolver")["puntos"], "{0}")
        self.assertEqual(solve("medio", **limits, expresion="x^2", entrega="resolver")["puntos"], "{0}")
        self.assertEqual(solve("intermedio", **limits, expresion="x^3", nivel="0", entrega="resolver")["puntos"], "{0}")

    def test_integrales_de_los_dos_temarios_y_promedio(self):
        course_groups = catalog()["calculus_courses"]
        shared = set(course_groups[1][1][0][1])
        self.assertEqual(shared, {"calculo.primitiva","calculo.definida","calculo.sustitucion","calculo.area"})
        self.assertTrue(shared <= {op for _,ids in course_groups[0][1] for op in ids})
        data = {"expresion":"x","segunda":"x^2","inferior":"0","superior":"1"}
        self.assertNotIn("area", solve("area", **data, entrega="plantear"))
        self.assertEqual(solve("area", **data, entrega="resolver")["area"], "1/6")
        crossing = solve("area", expresion="x", inferior="-1", superior="1", entrega="resolver")
        self.assertEqual((crossing["cruces"], crossing["area"]), (["0"], "1"))
        self.assertEqual(solve("sustitucion", expresion="2*x*(x^2+1)^3", sustitucion="x^2+1",
                               inferior="0", superior="1")["valor"], "15/4")
        mean = solve("promedio", expresion="x^2", inferior="0", superior="3")
        self.assertEqual(Fraction(mean["valor"]), 3)
        with self.assertRaises(ValueError):
            solve("promedio", expresion="x^2", inferior="0", superior="0")
