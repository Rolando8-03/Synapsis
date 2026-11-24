"""Referencias independientes de Q01–Q05."""
from fractions import Fraction
import unittest

from motor_matematico.application.backend import calculate
from motor_matematico.domain.models import DomainError


class QualityTest(unittest.TestCase):
    def test_chain_and_tangent(self):
        answer = calculate('calculo.derivada_cadena', {'expresion': '(x^2+1)^3'})
        trace = ' '.join(step['formula'] for step in answer['steps'])
        for term in (r'u=x^{2} + 1', "F'(u)=3 u^{2}", "u'=2 x"):
            self.assertIn(term, trace)
        frames = answer['result']['visual_integral']['cuadros']
        frame = next(frame for frame in frames if frame['x'] == '1')
        self.assertEqual((frame['y'], frame['m']), ('8','24'))
        restricted = calculate('calculo.derivada_cadena', {'expresion': 'ln(x^2-1)'})['result']
        self.assertTrue(all(abs(Fraction(frame['x'])) > 1 for frame in restricted['visual_integral']['cuadros']))
        self.assertTrue(any(y is None for _, y in restricted['visual_integral']['curva']))

    def test_region_and_washer_do_not_evaluate_a_setup(self):
        params = {'expresion':'x^3-x', 'segunda':'0', 'inferior':'-1', 'superior':'1', 'entrega':'plantear'}
        result = calculate('calculo.area', params)['result']
        self.assertNotIn('area', result)
        frames = result['visual_integral']['cuadros']
        self.assertEqual([frame['superior'] for frame in frames], ['f(x)', 'g(x)'])
        self.assertEqual([frame['derecha'] for frame in frames], ['0', '1'])
        with self.assertRaises(DomainError):
            calculate('calculo.area', {**params, 'expresion':'1/x'})
        washer = calculate('calculo.arandelas', {**params, 'expresion':'x+2','segunda':'1'})['result']
        self.assertNotIn('volumen', washer)
        frame = washer['visual_integral']['cuadros'][-1]
        self.assertEqual((frame['exterior'], frame['interior'], frame['area']), ('3','1','8*pi'))

    def test_exact_crossing_and_classifications(self):
        params = {'A': '1 1\n1 -1', 'b': '3 1/2'}
        result = calculate('libros.intersecciones', params)['result']
        self.assertEqual(result['particular'], ['7/4','5/4'])
        self.assertIn(r'\frac{1}{2}', result['visual_libro']['ecuaciones'][1])
        for b, classification in [('3 6','infinitas'),('3 7','incompatible')]:
            self.assertEqual(calculate('libros.intersecciones', {'A':'1 1\n2 2','b':b})['result']['clasificacion'],
                             classification)
        no_line = calculate('libros.intersecciones', {'A':'1 1\n0 0','b':'3 0'})['result']
        self.assertNotIn('control', no_line['visual_libro'])

    def test_stopped_method_reports_criterion_and_residual(self):
        answer = calculate('raices.newton', {'expresion':'x^2-2','inicial':'0'})
        self.assertEqual(answer['status'], 'breakdown')
        result = answer['result']
        self.assertEqual((result['ultimo_punto'], result['residual']), ('0', '2'))
        self.assertEqual(result['motivo_parada'], 'derivada_nula_o_demasiado_pequena')
        self.assertTrue(result['criterio'])
