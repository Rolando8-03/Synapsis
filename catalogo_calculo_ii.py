"""Formularios y rutas de Cálculo II."""
from functools import partial

import tecnicas_integracion as methods
import aplicaciones_integrales as uses
import modelos_integrales as models

TECHNIQUES = 'Técnicas de integración'
DEFINITE = 'Integral definida y áreas'
GEOMETRY = 'Volumen, longitud y superficie'
PHYSICS = 'Masa, centroide y trabajo'


def catalog_entries(field, spec):
    entries, handlers, groups = {}, {}, {}

    def add(group, key, title, description, fields, handler):
        operation = 'calculo.' + key
        entries[operation] = spec(title, description, fields)
        handlers[operation] = handler
        groups.setdefault(group, []).append(operation)

    def expression(demo, name='expresion', label='Integrando'):
        return field(name, label, 'expression', demo, visual=True)

    def bounds(a='0', b='1'):
        return [field('inferior','Desde',default=a),field('superior','Hasta',default=b)]

    def mode():
        return field('entrega','Resultado solicitado','select','plantear',False,choices=['plantear','resolver'],
                     choice_labels={'plantear':'Solo plantear','resolver':'Plantear y resolver'})

    add(TECHNIQUES, 'por_partes', 'Integral por partes',
        'Usá un polinomio multiplicado por exp, seno o coseno de argumento afín, o por ln(x).',
        [expression('x*exp(x)')], methods.by_parts)
    add(TECHNIQUES, 'fracciones_parciales', 'Fracciones parciales',
        'Ingresá la función racional para obtener sus coeficientes y una primitiva.',
        [expression('1/(x*(x+1))')], methods.partial_fractions)
    add(TECHNIQUES, 'potencias_trigonometricas', 'Potencias trigonométricas',
        'Elegí la familia y escribí sus exponentes enteros de 0 a 12.', [
            field('familia','Familia','select','seno_coseno',choices=['seno_coseno','tangente','cotangente','secante','cosecante'],
                  choice_labels={'seno_coseno':'Seno y coseno','tangente':'Tangente','cotangente':'Cotangente',
                                 'secante':'Secante','cosecante':'Cosecante'}),
            field('potencia','Exponente de la primera función','integer','3'),
            field('potencia_coseno','Exponente del coseno','integer','2',False,
                  when={'familia':['seno_coseno']}),
        ], methods.trig_powers)
    add(TECHNIQUES, 'sustitucion_trigonometrica', 'Sustitución trigonométrica',
        'Integrá el radical de la familia elegida. El parámetro a debe ser positivo.', [
            field('familia','Radical','select','diferencia',choices=['diferencia','suma','exterior'],
                  choice_labels={'diferencia':'√(a² − x²)','suma':'√(a² + x²)','exterior':'√(x² − a²)'}),
            field('parametro','Parámetro a',default='2'),
            field('rama','Intervalo de x','select','positiva',False,choices=['positiva','negativa'],
                  when={'familia':['exterior']},choice_labels={'positiva':'x ≥ a','negativa':'x ≤ −a'}),
        ], methods.trig_substitution)
    add(DEFINITE, 'riemann', 'Suma de Riemann',
        'Compará rectángulos y suma con el punto de muestra que elijas.', [
            expression('x^2',label='Función f(x)'), *bounds(),
            field('muestra','Punto de muestra','select','medio',choices=['izquierda','medio','derecha'],
                  choice_labels={'izquierda':'Izquierdo','medio':'Punto medio','derecha':'Derecho'}),
            field('n','Rectángulos iniciales','integer','4'),
        ], uses.riemann)
    add(DEFINITE, 'cambio_neto', 'Cambio neto a partir de una tasa',
        'Integrá una tasa elemental. Para calcular el valor final, agregá el valor inicial.', [
            expression('3*x^2',label='Tasa de cambio Q′(x)'), *bounds('0','2'),
            field('entrega','Resultado solicitado','select','cambio',False,choices=['cambio','final'],
                  choice_labels={'cambio':'Cambio neto','final':'Valor final'}),
            field('inicial','Valor inicial Q(a)',default='',required=False,
                  when={'entrega':['final']},required_when={'entrega':['final']}),
            field('unidad_cantidad','Unidad de la cantidad','text','m',False),
            field('unidad_tiempo','Unidad de la variable','text','s',False),
        ], uses.net_change)
    add(DEFINITE, 'area_bajo_curva', 'Área bajo una curva',
        'Separá el área geométrica de la integral con signo.',
        [expression('x',label='Función f(x)'),*bounds('-1','1'),mode()], uses.area)
    add(GEOMETRY, 'discos', 'Volumen por discos',
        'Girás la región entre una curva polinómica y el eje horizontal y = c.', [
            expression('x',label='Frontera f(x)'), *bounds(), field('eje','Altura c del eje · 0 si se omite',required=False),mode(),
        ], uses.volume)
    add(GEOMETRY, 'arandelas', 'Volumen por arandelas',
        'Girás la región entre dos polinomios alrededor del eje horizontal y = c.', [
            expression('x+2',label='Frontera f(x)'),expression('x+1','segunda','Frontera g(x)'),
            *bounds(),field('eje','Altura c del eje · 0 si se omite',required=False),mode(),
        ], partial(uses.volume,washers=True))
    add(GEOMETRY, 'longitud_arco', 'Longitud de arco',
        'Obtené el elemento de arco de una curva polinómica.',
        [expression('3*x/4',label='Curva f(x)'),*bounds('0','4'),mode()], uses.arc_or_surface)
    add(GEOMETRY, 'superficie_revolucion', 'Superficie de revolución',
        'Girás una curva polinómica alrededor de un eje horizontal y = c.',
        [expression('x+1',label='Curva f(x)'),*bounds(),field('eje','Altura c del eje · 0 si se omite',required=False),mode()],
        partial(uses.arc_or_surface,surface=True))
    rod_fields = [*bounds('0','3'), field('densidad_izquierda','Densidad lineal inicial',default='1'),
                  field('densidad_derecha','Densidad lineal final',default='3')]
    add(PHYSICS, 'masa_barra', 'Masa de una barra',
        'Obtené la masa de una barra cuya densidad varía linealmente.', rod_fields, models.rod)
    add(PHYSICS, 'centro_masa', 'Momento y centro de masa de una barra',
        'Obtené el momento respecto a un origen y la posición del centro de masa.',
        [*rod_fields,field('origen','Origen del momento · 0 si se omite',required=False)], partial(models.rod,center=True))
    add(PHYSICS, 'centroide', 'Centroide de una lámina uniforme',
        'Usá dos fronteras polinómicas y el intervalo donde se encuentra la lámina.', [
            expression('1-x^2',label='Frontera f(x)'),expression('0','segunda','Frontera g(x)'),*bounds('-1','1'),
        ], models.centroid)
    add(PHYSICS, 'trabajo_resorte', 'Trabajo en un resorte',
        'Medí la elongación desde la longitud natural del resorte.', [
            field('constante','Constante elástica k',default='12'),
            field('inferior','Elongación inicial',default='0'),field('superior','Elongación final',default='1/2'),mode(),
        ], models.spring)
    add(PHYSICS, 'trabajo_bombeo', 'Bombeo en un cono invertido',
        'Medí las alturas desde el vértice inferior. Si omitís el peso específico, queda como γ.', [
            field('altura','Altura del tanque',default='4'),field('radio','Radio en el borde',default='2'),
            field('relleno','Altura del líquido · tanque lleno si se omite',required=False),
            field('salida','Altura de salida · al borde si se omite',required=False),
            field('peso_especifico','Peso específico del líquido',required=False),mode(),
        ], models.pumping)
    return entries, handlers, list(groups.items())
