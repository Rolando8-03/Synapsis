"""Cierres I01–I21 desde el catálogo y el cálculo que usa la interfaz."""
from fractions import Fraction
import unittest

from backend import calculate, catalog
from motor_matematico.domain.models import DomainError


HERE = {'inferior':'0','superior':'1'}


def solve(op, **data):
    return calculate('calculo.'+op,data)


class CalculoIITest(unittest.TestCase):
    def test_i01_primitiva_verifica_dominio_y_constante(self):
        reply = solve('primitiva',expresion='1/x')
        self.assertEqual(reply['result']['expresion'],'ln(abs(x)) + C')
        self.assertEqual(reply['result']['dominio'],'Union(Interval.open(-oo, 0), Interval.open(0, oo))')
        self.assertTrue(any(step['data'].get('diferencia')=='0' for step in reply['steps']))
        self.assertTrue(any(step['data'].get('coeficiente')=='3' for step in
                            solve('primitiva',expresion='3*sin(2*x)')['steps']))

    def test_i02_sustitucion_con_diferencial_y_retorno(self):
        reply = solve('sustitucion',expresion='4*x*(x^2+1)^3',sustitucion='x^2+1',**HERE)
        self.assertEqual(reply['result']['valor'],'15/2')
        self.assertIn('2',reply['steps'][1]['data']['integrando_en_u'])
        repeated = solve('sustitucion',expresion='2*x*exp(x^2)',sustitucion='x^2')
        self.assertEqual(repeated['result']['primitiva'],'exp(x**2) + C')
        with self.assertRaises(DomainError):
            solve('sustitucion',expresion='x',sustitucion='x^3')

    def test_i03_partes_repite_y_comprueba(self):
        reply = solve('por_partes',expresion='x*exp(x)')
        self.assertEqual(reply['result']['primitiva'],'(x - 1)*exp(x) + C')
        self.assertIn('dv=',reply['steps'][0]['formula'])
        self.assertIn('du=',reply['steps'][0]['formula'])
        self.assertEqual(reply['steps'][-1]['data']['diferencia'],'0')
        with self.assertRaises(DomainError):
            solve('por_partes',expresion='x*exp(x^2)')

    def test_i04_i05_division_factores_y_numerador(self):
        cases = {
            '1/(x*(x+1))':('-1/(x + 1) + 1/x','1'),
            '(x^3+2)/(x*(x+1))':('x - 1 - 1/(x + 1) + 2/x','x**3 + 2'),
            '(x+1)/(x-1)^2':('1/(x - 1) + 2/(x - 1)**2','x + 1'),
            '(2*x+1)/(x^2+1)':('(2*x + 1)/(x**2 + 1)','2*x + 1'),
            '1/(2*x^2+3*x+5)':('1/(2*(x**2 + 3*x/2 + 5/2))','1/2'),
        }
        for source, (decomposition,numerator) in cases.items():
            with self.subTest(source=source):
                reply = solve('fracciones_parciales',expresion=source)
                self.assertEqual(reply['result']['descomposicion'],decomposition)
                self.assertEqual(reply['result']['numerador_reconstruido'],numerator)
                self.assertEqual(reply['steps'][-1]['data']['diferencia'],'0')
        with self.assertRaises(DomainError):
            solve('fracciones_parciales',expresion='1/(x^2-2)')

    def test_i06_identidades_y_paridad_de_cada_familia(self):
        cases = [
            ('seno_coseno',3,2,'cos(x)**5/5 - cos(x)**3/3 + C'),
            ('seno_coseno',2,2,'x/8 - sin(x)*cos(x)**3/4 + sin(x)*cos(x)/8 + C'),
            ('tangente',2,0,'-x + tan(x) + C'), ('cotangente',2,0,'-x - cot(x) + C'),
            ('secante',2,0,'tan(x) + C'), ('cosecante',2,0,'-cot(x) + C'),
        ]
        for family,m,n,primitive in cases:
            with self.subTest(family=family,m=m,n=n):
                reply = solve('potencias_trigonometricas',familia=family,potencia=m,potencia_coseno=n)
                self.assertEqual(reply['result']['primitiva'],primitive)
                self.assertEqual(reply['steps'][-1]['data']['diferencia'],'0')
        with self.assertRaises(ValueError):
            solve('potencias_trigonometricas',familia='seno_coseno',potencia='3/2')

    def test_i07_radicales_y_ramas(self):
        for family, branch, domain in [('diferencia','positiva','Interval(-2, 2)'),('suma','positiva','Reals'),
                                       ('exterior','positiva','Interval(2, oo)'),('exterior','negativa','Interval(-oo, -2)')]:
            with self.subTest(family=family,branch=branch):
                reply = solve('sustitucion_trigonometrica',familia=family,parametro='2',rama=branch)
                self.assertEqual(reply['result']['dominio'],domain)
                self.assertIn(r'\theta',reply['steps'][0]['formula'])
                self.assertEqual(reply['steps'][-1]['data']['diferencia'],'0')
        with self.assertRaises(ValueError):
            solve('sustitucion_trigonometrica',familia='diferencia',parametro=0)

    def test_i08_teorema_fundamental_y_singularidad_interior(self):
        reply = solve('definida',expresion='x^2',**HERE)
        self.assertEqual(reply['result']['valor'],'1/3')
        self.assertIn('F(1)-F(0)',reply['steps'][-1]['formula'])
        self.assertEqual(solve('definida',expresion='1/x',inferior='-1',superior='1')['status'],'domain_error')

    def test_i09_cada_conjunto_de_rectangulos_usa_la_misma_suma(self):
        for method, expected in [('izquierda','1/8'),('medio','5/16'),('derecha','5/8')]:
            model = solve('riemann',expresion='x^2',muestra=method,n=2,**HERE)['result']['visual_integral']
            for frame in model['cuadros']:
                self.assertEqual(len(frame['puntos']),frame['n'])
                self.assertEqual(len(frame['particion']),frame['n']+1)
            self.assertEqual(model['cuadros'][model['inicial']]['suma'],expected)
        negative = solve('riemann',expresion='-1',muestra='medio',n=2,**HERE)['result']['visual_integral']
        self.assertEqual(negative['cuadros'][1]['suma'],'-1')
        with self.assertRaises(DomainError):
            solve('riemann',expresion='1/x',muestra='medio',n=2,inferior='-1',superior='1')

    def test_i10_cambio_y_valor_final(self):
        data = dict(expresion='12*x',unidad_cantidad='m',unidad_tiempo='s',**HERE)
        result = solve('cambio_neto',**data)['result']
        self.assertEqual((result['cambio_neto'],result['unidad']),('6','m'))
        self.assertNotIn('valor_final',result)
        with self.assertRaises(ValueError):
            solve('cambio_neto',entrega='final',**data)
        self.assertEqual(solve('cambio_neto',entrega='final',inicial='2',**data)['result']['valor_final'],'8')

    def test_i11_i12_distinguen_area_signo_y_region(self):
        result = solve('area_bajo_curva',expresion='x',inferior='-1',superior='1',entrega='resolver')['result']
        self.assertEqual((result['area'],result['integral_con_signo']),('1','0'))
        result = solve('area',expresion='x',segunda='x^2',entrega='plantear')['result']
        self.assertEqual(result['cruces'],['0','1'])
        self.assertIn(r'\int_{0}^{1}',result['formula_latex'])
        self.assertNotIn('area',result)
        with self.assertRaisesRegex(DomainError,r'\[-1, 0\].*\[0, 1\]'):
            solve('area',expresion='x^3-x',segunda='0',entrega='plantear')
        selected = solve('area',expresion='x^3-2*x',segunda='0',region='2',entrega='resolver')['result']
        self.assertEqual((selected['cruces'],selected['area']),(['0','sqrt(2)'],'1'))

    def test_i13_i14_seccion_y_eje_desplazado(self):
        disks = solve('discos',expresion='x',eje='2',entrega='resolver',**HERE)['result']
        self.assertEqual(disks['volumen'],'7*pi/3')
        self.assertEqual(disks['visual_integral']['cuadros'][32]['area'],'9*pi/4')
        holes = solve('arandelas',expresion='x+2',segunda='x+1',eje='0',entrega='resolver',**HERE)['result']
        self.assertEqual(holes['volumen'],'4*pi')
        self.assertEqual(holes['visual_integral']['cuadros'][32]['interior'],'3/2')
        crosses = solve('arandelas',expresion='3*x',segunda='0',eje='1',entrega='resolver',**HERE)['result']
        self.assertEqual(crosses['volumen'],'4*pi/3')
        self.assertEqual(crosses['visual_integral']['cuadros'][-1]['interior'],'0')

    def test_i15_i16_arco_y_superficie(self):
        r = solve('longitud_arco',expresion='3*x/4',inferior='0',superior='4',entrega='resolver')['result']
        self.assertEqual((r['valor'],r['distancia_extremos']),('5','5'))
        self.assertNotIn('valor',solve('longitud_arco',expresion='x^2',**HERE)['result'])
        surface = solve('superficie_revolucion',expresion='x+1',entrega='resolver',**HERE)['result']
        self.assertEqual(surface['valor'],'3*sqrt(2)*pi')
        self.assertEqual(surface['unidades'],'longitud al cuadrado')

    def test_i17_i18_masa_momento_y_masa_nula(self):
        data = dict(inferior='0',superior='3',densidad_izquierda='1',densidad_derecha='3')
        mass = solve('masa_barra',**data)['result']
        self.assertEqual(mass['masa'],'6')
        self.assertNotIn('centro_de_masa',mass)
        center = solve('centro_masa',origen='2',**data)['result']
        self.assertEqual((center['momento'],center['centro_de_masa']),('-3/2','7/4'))
        zero = solve('centro_masa',densidad_izquierda='0',densidad_derecha='0',**HERE)['result']
        self.assertIsNone(zero['centro_de_masa'])

    def test_i19_centroide_en_region_simetrica(self):
        r = solve('centroide',expresion='1-x^2',segunda='0',inferior='-1',superior='1')['result']
        self.assertEqual((r['area'],r['momento_x'],r['momento_y']),('4/3','8/15','0'))
        self.assertEqual(r['centroide'],['0','2/5'])
        with self.assertRaises(DomainError):
            solve('centroide',expresion='1-x^2',segunda='1-x^2',**HERE)

    def test_i20_i21_planteamiento_trabajo_y_gamma(self):
        spring = dict(constante='12',inferior='0',superior='1/2')
        self.assertNotIn('trabajo',solve('trabajo_resorte',**spring)['result'])
        self.assertEqual(Fraction(solve('trabajo_resorte',entrega='resolver',**spring)['result']['trabajo']),Fraction(3,2))
        pump = dict(altura='4',radio='2')
        self.assertNotIn('trabajo',solve('trabajo_bombeo',**pump)['result'])
        self.assertEqual(solve('trabajo_bombeo',entrega='resolver',**pump)['result']['trabajo'],'16*pi*gamma/3')
        self.assertEqual(solve('trabajo_bombeo',entrega='resolver',peso_especifico='2',relleno='2',salida='3',**pump)['result']['trabajo'],'2*pi')
        with self.assertRaises(DomainError):
            solve('trabajo_bombeo',relleno='2',salida='1',**pump)

    def test_temario_y_catalogo_usan_las_mismas_operaciones(self):
        index = catalog()
        course, groups = index['calculus_courses'][1]
        self.assertEqual(course,'Cálculo II')
        self.assertEqual(sum(len(ops) for _,ops in groups),20)
        calculator = {op for _,ops in index['modules']['grafica'] for op in ops}
        for _,ops in groups:
            self.assertTrue(set(ops) <= calculator)
            self.assertTrue(set(ops) <= index['operations'].keys())
