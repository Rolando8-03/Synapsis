"""La escena consume las filas y las fórmulas del mismo cálculo."""
from fractions import Fraction
import unittest

from backend import calculate


class AnimatedGraphsTest(unittest.TestCase):
    def test_newton_second_iteration_preserves_tangent_and_table(self):
        def exercise(expression, initial):
            answer = calculate('raices.newton', {'expresion':expression, 'inicial':initial})
            row = answer['result']['tabla'][1]
            frame = answer['result']['grafico_raiz']['cuadros'][1]
            trace = next(step for step in answer['steps'] if step['data'].get('iteracion') == 2)
            self.assertEqual(frame['iteracion'], row['iteracion'])
            self.assertEqual(frame['formula'],trace['formula'])
            self.assertIn(row['x_decimal'],frame['formula'])
            self.assertEqual(float(frame['siguiente']),float(row['x']))
            return frame

        first = exercise('x^2-2','1')
        second = exercise('x^2-3','1.4')
        [[x,y],[cross,height]] = first['recta']
        self.assertEqual((x,y,height),(1.5,.25,0))
        self.assertAlmostEqual(cross,x-y/3)
        self.assertNotEqual(first['recta'],second['recta'])

    def test_modified_newton_distinguishes_intercept_from_next_approximation(self):
        data = {'expresion':'(x-1)^3','inicial':'1.75','multiplicidad':'3'}
        frame = calculate('raices.newton',data)['result']['grafico_raiz']['cuadros'][0]
        self.assertAlmostEqual(float(frame['recta'][1][0]),1.5)
        self.assertAlmostEqual(float(frame['siguiente']),1)
        stopped = calculate('raices.newton',{'expresion':'x^2-2','inicial':'0'})
        self.assertEqual(stopped['result']['grafico_raiz']['cuadros'],[])

    def test_brackets_and_updated_interval_use_same_rows(self):
        for operation in ('raices.biseccion','raices.falsa_posicion'):
            result = calculate(operation,{'expresion':'x^2-2','inferior':'1','superior':'2'})['result']
            graph = result['grafico_raiz']
            self.assertEqual(len(graph['cuadros']),len(result['tabla']))
            for frame,row in zip(graph['cuadros'],result['tabla']):
                self.assertEqual(frame['formula'],row['desarrollo'])
                self.assertEqual(list(map(float,frame['intervalo'])),
                                 [float(Fraction(row[key])) for key in ('a','b')])
                self.assertEqual(list(map(float,frame['intervalo_siguiente'])),
                                 [float(Fraction(value)) for value in row['intervalo_siguiente']])
