"""Formularios y rutas de Cálculo II."""
import tecnicas_integracion as methods

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
            field('familia','Radical','select','diferencia',choices=['diferencia','suma'],
                  choice_labels={'diferencia':'√(a² − x²)','suma':'√(a² + x²)'}),
            field('parametro','Parámetro a',default='2'),
        ], methods.trig_substitution)
    return entries, handlers, list(groups.items())


def course_groups():
    return catalog_entries(lambda *a, **k: None, lambda *a: None)[2]
