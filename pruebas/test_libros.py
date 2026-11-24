"""Criterios verificables de L01–L27 por la entrada normal de la calculadora."""
from fractions import Fraction
import unittest

from backend import calculate, catalog


def run(name, **updates):
    operation = "libros."+name
    spec = catalog()["operations"][operation]
    inputs = {f["name"]: f["default"] for f in spec["fields"] if f["default"] != ""}
    inputs.update(updates)
    response = calculate(operation, inputs)
    assert response["status"] == "ok" and response["steps"]
    return response["result"]


class BooksTest(unittest.TestCase):
    def test_intersection_of_lines_planes_and_higher_dimensions(self):
        self.assertEqual(run("intersecciones")["particular"], ["2","1"])
        r = run("intersecciones", A="1 0 0\n0 1 0", b="1 2")
        self.assertEqual(r["direcciones"], [["0","0","1"]])
        self.assertEqual(r["visual_libro"]["tipo"], "planos")
        r = run("intersecciones", A="1 0 0 1\n0 1 0 0", b="1 2")
        self.assertEqual(r["pivotes"], [0,1])
        self.assertEqual(run("intersecciones", A="1 1\n2 2", b="2 5")["clasificacion"], "incompatible")

    def test_transform_preserves_vector_when_basis_changes(self):
        first = run("transformacion", B="1 0\n0 1")
        second = run("transformacion", B="1 1\n0 1")
        self.assertNotEqual(first["coordenadas"], second["coordenadas"])
        self.assertEqual(first["imagen"], second["imagen"])
        self.assertNotEqual(first["imagenes_base"], second["imagenes_base"])

    def test_norms_and_oriented_area(self):
        for norm in ("uno","dos","infinito"):
            r = run("normas", norma=norm)
            self.assertEqual([r[k] for k in ("norma_1","norma_2","norma_infinito")], ["7","5","4"])
            self.assertEqual(r["visual_libro"]["selector"][-1], norm)
        for values, determinant in [("2 2\n1 1","0"),("2 3\n1 1","-1"),("2 1\n1 3","5")]:
            self.assertEqual(run("area_orientada", A=values)["determinante"], determinant)

    def test_pivoting_and_conditioning(self):
        r = run("pivoteo")
        self.assertLess(Fraction(r["con_pivoteo"]["error_infinito"]), Fraction(r["sin_pivoteo"]["error_infinito"]))
        for norm in ("uno","infinito"):
            comparison = run("sensibilidad", norma=norm)
            self.assertTrue(comparison["verificacion"])
            self.assertLessEqual(Fraction(comparison["cambio_relativo_x"]), Fraction(comparison["cota"]))
        self.assertIsNone(run("sensibilidad",A="1 1\n2 2",b="1 2")["condicion"])

    def test_candidate_scan_and_fixed_point(self):
        r = run("intervalos",expresion="(x-1)/x",inferior="-1",superior="2",n="10")
        self.assertTrue(r["intervalos_con_dominio_no_verificado"])
        self.assertTrue(r["intervalos_candidatos"])
        self.assertFalse(run("intervalos",expresion="(x-1/7)^2",inferior="0",superior="1",n="8")["intervalos_candidatos"])
        r = run("punto_fijo")
        self.assertEqual(r["g1"]["q_en_la_cota"],"1/2")
        self.assertLessEqual(Fraction(r["g1"]["iteraciones"][-1]["residuo_original"]), Fraction("1e-5"))
        self.assertIsNone(r["g2"]["iteraciones"][-1]["cota_al_punto_fijo"])

    def test_projection_qr_and_least_squares(self):
        self.assertTrue(run("proyeccion")["ortogonal"])
        self.assertTrue(run("gram_schmidt", A="1 2\n2 4")["columnas_dependientes"])
        r = run("qr")
        self.assertTrue(r["ortonormal"] and r["reconstruccion"])
        sim = r["comparacion_simulada"]
        self.assertLess(Fraction(sim["modificado"]["error_ortogonalidad"]), Fraction(sim["clasico"]["error_ortogonalidad"]))
        self.assertTrue(run("minimos_cuadrados")["unica"])
        r = run("minimos_cuadrados", A="1 2\n2 4\n3 6")
        self.assertFalse(r["unica"])
        self.assertEqual(r["normal"], [["0"],["0"]])

    def test_eigenvalues_spaces_and_spectral_theorem(self):
        rotation = "0 -1\n1 0"
        self.assertFalse(run("valores_propios", A=rotation)["valores_propios"])
        self.assertEqual({item["valor"] for item in run("valores_propios", A=rotation, cuerpo="complejo")["valores_propios"]}, {"I","-I"})
        self.assertEqual(run("espacio_propio", A=rotation, **{"lambda":"0","imag":"1"})["dimension"],1)
        r = run("espacio_propio", A="0 2\n1 0", **{"lambda":"sqrt(2)"})
        self.assertTrue(r["es_valor_propio"] and r["verificacion"])
        self.assertFalse(run("diagonalizacion", A="1 1\n0 1")["diagonalizable"])
        self.assertTrue(run("diagonalizacion", A=rotation,cuerpo="complejo")["verificacion"])
        r = run("espectral", A="2 1\n1 2")
        self.assertTrue(r["ortonormal"] and r["reconstruccion"])
        self.assertEqual(len(r["diagrama_vectores"]),2)
        with self.assertRaisesRegex(ValueError,"simétrica"):
            run("espectral",A="2 0\n1 2")

    def test_power_and_markov(self):
        r = run("potencia",A="3 0\n0 1",b="1 1")
        self.assertAlmostEqual(float(r["valor_propio"]),3)
        self.assertLessEqual(Fraction(r["residuo"]),Fraction("1e-8"))
        r = run("markov")
        self.assertTrue(r["regular"])
        self.assertEqual(r["comparacion_periodica"][:3],[[0,"1","0"],[1,"0","1"],[2,"1","0"]])
        self.assertFalse(run("markov",A="0 1\n1 0")["regular"])
        with self.assertRaisesRegex(ValueError,"sumar 1"):
            run("markov",A="1 0\n1 1")

    def test_svd_truncation_and_image(self):
        for A in ("3 0\n0 2\n0 0","3 0 0\n0 2 0"):
            r = run("svd",A=A,rango="1")
            self.assertTrue(r["verificacion"])
            self.assertEqual(r["valores_singulares"],["3.0","2.0"])
            self.assertEqual(float(r["error_truncamiento"]),2)
        self.assertTrue(run("svd",A="0 0\n0 0")["verificacion"])
        r = run("compresion")
        self.assertEqual(r["visual_libro"]["tipo"],"imagen")
        self.assertEqual(r["visual_libro"]["rango"],2)

    def test_regression_interpolation_and_spline(self):
        points = "0 1\n1 3\n2 5"
        self.assertEqual(run("regresion",puntos=points)["suma_cuadratica"],"0")
        self.assertTrue(run("newton")["verificacion"])
        self.assertTrue(run("lagrange")["coincide_con_newton"])
        self.assertTrue(all(run("spline")["verificacion"].values()))
        for op in ("newton","lagrange","spline"):
            with self.subTest(op=op), self.assertRaisesRegex(ValueError,"distintas"):
                run(op,puntos="0 0\n0 1")

    def test_quadrature_and_finite_differences(self):
        r = run("cuadratura")
        self.assertEqual(r["simpson_13"]["valor_en_malla_n"],"1/3")
        self.assertEqual(r["simpson_13"]["cota_garantizada_en_malla_n"],"0")
        self.assertEqual(run("romberg")["valor"],"1/5")
        with self.assertRaisesRegex(ValueError,"par"):
            run("cuadratura",n="3")
        errors = [Fraction(run(k)["error_truncamiento"]) for k in ("adelante","atras","centrada","richardson")]
        self.assertLess(errors[2],min(errors[:2]))
        self.assertEqual(errors[3],0)

    def test_ode_and_applications(self):
        self.assertLess(float(run("euler")["valor_final"]),2)
        for method in ("heun","rk4"):
            self.assertAlmostEqual(float(run(method)["valor_final"]),2)
        with self.assertRaisesRegex(ValueError,"referencia"):
            run("rk4",referencia="1")
        self.assertTrue(run("red_electrica")["verificacion"])
        self.assertEqual(run("caminos")["camino"],[1,2,3])
        self.assertFalse(run("caminos",origen="3",destino="1")["alcanzable"])
        self.assertEqual(run("codigo_binario")["sindrome"],["1","1"])
