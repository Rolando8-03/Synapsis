"""Cierres del modelo físico común de las fases K01–K04."""
import math
import unittest

from motor_matematico.algorithms.kepler import (Orbit, SOLAR_MU, eccentric_anomaly, equal_sectors, measure_sector,
                    orbital_frames, planet_positions, position, scene_frames)


class KeplerTest(unittest.TestCase):
    def test_k01_parametros_y_unidades(self):
        orbit = Orbit(3,.6,SOLAR_MU)
        self.assertAlmostEqual(orbit.b,2.4)
        self.assertEqual(orbit.units,'UA, año')
        for args in [(0,.5,1),(1,-.1,1),(1,1,1),(1,.1,0),(1,.2,math.inf),(math.nan,.5,1),(1,0,1,'km, s')]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Orbit(*args)

    def test_k02_foco_comun_distancia_y_ecuacion(self):
        first, second = Orbit(1,.55,SOLAR_MU), Orbit(2,0,SOLAR_MU)
        for time in (-.2,0,.13,.5,1,6.43):
            a,b = planet_positions(first,second,time)
            self.assertAlmostEqual(b.radius,2)
            self.assertAlmostEqual(a.radius+math.hypot(a.x+2*first.a*first.e,a.y),2*first.a)
            for orbit, state in ((first,a),(second,b)):
                self.assertAlmostEqual(state.anomaly-orbit.e*math.sin(state.anomaly),state.mean,places=13)
                self.assertAlmostEqual(state.mean/math.tau+state.turns,time/orbit.period)
        with self.assertRaises(ValueError):
            planet_positions(first,Orbit(2,0,1),.3)

    def test_k02_excentricidad_cercana_a_uno(self):
        e = 1-2**-40
        known_angle = math.pi/3
        mean = known_angle-e*math.sqrt(3)/2
        self.assertAlmostEqual(eccentric_anomaly(mean,e),known_angle,places=14)
        tiny = 1e-12
        angle = eccentric_anomaly(tiny,e)
        self.assertLess(abs(angle-e*math.sin(angle)-tiny),1e-19)
        self.assertGreater(angle,0)
        at_perihelion = position(Orbit(1,e,SOLAR_MU),0)
        self.assertEqual(at_perihelion.radius,1-e)
        self.assertTrue(math.isfinite(at_perihelion.speed))

    def test_k03_sectores_desde_perihelio_y_afelio(self):
        orbit = Orbit(1,.55,SOLAR_MU)
        current, reference = equal_sectors(orbit,0,position(orbit,0))
        self.assertAlmostEqual(current.end_time-current.start_time,reference.end_time-reference.start_time)
        expected = math.pi*orbit.a*orbit.b*.08
        self.assertAlmostEqual(current.area,expected,places=13)
        self.assertAlmostEqual(reference.area,expected,places=13)
        self.assertAlmostEqual(current.end.speed/reference.end.speed,(1+orbit.e)/(1-orbit.e))
        self.assertEqual((current.start.turns,current.end.turns),(-1,0))
        crosses = measure_sector(orbit,.96,1.04)
        self.assertEqual((crosses.start.turns,crosses.end.turns),(0,1))
        self.assertAlmostEqual(crosses.area,expected,places=13)
        self.assertAlmostEqual(measure_sector(orbit,.4,2.4).area,2*math.pi*orbit.a*orbit.b)
        with self.assertRaises(ValueError):
            measure_sector(orbit,1,0)

    def test_k04_comparacion_y_muestras_del_mismo_instante(self):
        scene = scene_frames(.55,2,.25)
        a,b = scene['A'],scene['B']
        self.assertAlmostEqual(b['periodo']/a['periodo'],2**1.5)
        self.assertAlmostEqual(a['cociente'],4*math.pi**2/scene['mu'])
        self.assertAlmostEqual(b['cociente'],a['cociente'])
        self.assertEqual(scene_frames(.55,2,0)['B']['periodo'],b['periodo'])
        self.assertEqual((scene['frames'][0]['t'],scene['frames'][-1]['t']),(0,12))
        frame = scene['frames'][643]
        self.assertEqual(frame['t'],6.43)
        self.assertEqual(frame['A']['p'],frame['actual']['fin'])
        self.assertEqual(frame['A']['v'],frame['actual']['v'])
        self.assertAlmostEqual(frame['actual']['fin_t'],frame['t'])
        self.assertAlmostEqual(frame['actual']['area'],frame['referencia']['area'],places=13)
        self.assertIs(scene_frames(.55,2,.25),scene)

    def test_escena_tierra_y_orbita_de_prueba_comparten_reloj(self):
        earth_e = .0167
        scene = scene_frames(earth_e, 2.25, .30)
        comparison = scene_frames(earth_e, 2, .75)
        self.assertEqual(scene['A'], comparison['A'])
        self.assertAlmostEqual(comparison['B']['periodo'], 2**1.5)
        for i in (0, 50, 101, 643, 1200):
            frame = comparison['frames'][i]
            self.assertEqual(frame['A'], scene['frames'][i]['A'])
            self.assertNotEqual(frame['B']['p'], scene['frames'][i]['B']['p'])
            for name in ('A', 'B'):
                self.assertAlmostEqual(frame[name]['suma_focal'], 2*comparison[name]['a'])
            self.assertAlmostEqual(frame['actual']['area'], frame['referencia']['area'])
            self.assertAlmostEqual(comparison['A']['cociente'], comparison['B']['cociente'])

    def test_ruta_de_experimentos_individuales_conserva_formato(self):
        for law,shape,width in [(1,.55,5),(2,.55,6),(3,2.25,4)]:
            with self.subTest(law=law):
                data = orbital_frames(law,shape)
                self.assertEqual(len(data['frames']),1201)
                self.assertEqual(len(data['frames'][0]),width)
                self.assertIs(orbital_frames(law,shape),data)
