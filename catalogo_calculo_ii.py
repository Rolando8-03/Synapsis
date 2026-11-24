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
    return entries, handlers, list(groups.items())


def course_groups():
    return catalog_entries(lambda *a, **k: None, lambda *a: None)[2]
