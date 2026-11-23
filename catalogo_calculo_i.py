"""Catálogo y agrupación de las operaciones de Cálculo I."""
from functools import partial

import calculo_i as calculus

def catalog_entries(field, spec):
    def expr(default, label="Función f(x)", **options):
        return field("expresion",label,"expression",default,visual=True,**options)
    def point(default="0",required=True,label="Punto x"):
        return field("punto",label,default=default,required=required)
    def bounds(a,b,required=True):
        return [field("inferior","Extremo inferior",default=a,required=required),
                field("superior","Extremo superior",default=b,required=required)]
    def side(default="+",choices=("-","+")):
        return field("lado","Lado", "select",default,choices=list(choices))
    def mode(default="resolver"):
        return field("entrega","Resultado solicitado","select",default,choices=["plantear","resolver"])
    def secondary(name,label,default="",required=False):
        return field(name,label,"expression",default,required,visual=True)
    def units(x,y):
        return [field("unidad_x","Unidad de x","text",x,False), field("unidad_y","Unidad de f","text",y,False)]

    entries, handlers, groups = {}, {}, {}
    def add(group, key, title, description, fields, handler):
        op = "calculo."+key
        entries[op] = spec(title,description,fields)
        handlers[op] = handler
        groups.setdefault(group,[]).append(op)

    functions = "Funciones y dominio"
    limits = "Límites y continuidad"
    derivatives = "Reglas de derivación"
    applications = "Aplicaciones de la derivada"
    integrals = "Integrales y áreas"
    piece = secondary("derecha","Función a la derecha · opcional")
    add(functions,"dominio","Dominio real","Intersecá las restricciones de la función original.",[expr("(x^2-1)/(x-1)")],calculus.domain)
    add(functions,"composicion","Composición de funciones","Calculá f(g(x)) y su dominio.",[
        secondary("exterior","Función exterior f(x)","sqrt(x)",True),
        secondary("interior","Función interior g(x)","x-2",True),point("3",False)],calculus.composition)
    add(functions,"inversa","Función inversa","Elegí una rama inyectiva de una función afín o cuadrática.",
        [expr("x^2"),*bounds("0","3")],calculus.inverse)
    add(limits,"limite_lateral","Límite lateral","Compará las aproximaciones. Podés escribir otra función para el lado derecho.",
        [expr("(x^2-1)/(x-1)",editor="limite"),point("1",label="Punto de aproximación"),side("+",("-","+","ambos")),piece],calculus.one_sided)
    add(limits,"limite_factorizacion","Límite por factorización","Eliminá una indeterminación 0/0 en un cociente de polinomios.",
        [expr("(x^2-1)/(x-1)"),point("1")],calculus.factoring)
    add(limits,"limite_racionalizacion","Límite por racionalización","Usá el conjugado de un numerador de la forma √u−v.",
        [expr("(sqrt(x+1)-1)/x"),point()],calculus.rationalizing)
    add(limits,"limite_infinito","Límite infinito en un punto","Estudiá el comportamiento lateral cerca de una singularidad.",
        [expr("1/x"),point(),side()],calculus.infinite_limit)
    add(limits,"limite_al_infinito","Límite al infinito","Compará los términos dominantes de un cociente de polinomios.",
        [expr("(2*x^2+1)/(x^2-3)"),field("lado","Sentido","select","+",choices=["-","+"],
            choice_labels={"-":"Hacia −∞","+":"Hacia +∞"})],calculus.infinity_limit)
    add(limits,"continuidad","Continuidad en un punto","Contrastá ambos límites y el valor de la función.",
        [expr("(x^2-1)/(x-1)"),point("1"),piece,
         field("valor_punto","Valor en el punto · opcional","scalar","",False)],calculus.continuity)
    add(derivatives,"derivada_definicion","Derivada por definición","Usá el cociente incremental de un polinomio.",[expr("x^2")],calculus.by_definition)
    for key,title,demo in [
        ("cadena","Cadena","(x^2+1)^3"),("producto","Producto","x*exp(x)"),
        ("cociente","Cociente","x/(x+1)"),("exponencial","Exponencial","exp(2*x)"),
        ("logaritmica","Logarítmica","ln(x^2+1)"),("trigonometrica","Trigonométrica","sin(x^2)"),
    ]:
        add(derivatives,"derivada_"+key,"Regla de derivación · "+title,
            "Desarrollá los operandos y la regla que produce la derivada.",
            [expr(demo)],partial(calculus.derivative_rule,rule=key))
    add(derivatives,"derivada_implicita","Derivada implícita","Derivá ambos lados de una ecuación polinómica en x e y.",
        [secondary("izquierda","Miembro izquierdo","x^2+y^2",True),
         secondary("derecha","Miembro derecho","1",True)],calculus.implicit)
    add(derivatives,"parcial_sucesiva","Derivadas parciales sucesivas","Elegí el orden de las derivadas mediante una lista de variables.",
        [expr("x^2*y","Polinomio en x e y",editor="bivariado"),
         field("orden","Variables en orden","text","x y")],calculus.successive)
    add(applications,"criticos","Números críticos","Encontrá ceros de la derivada y puntos donde no existe dentro del dominio.",
        [expr("abs(x)")],calculus.critical)
    add(applications,"signos","Signos y concavidad","Construí la tabla de la primera y segunda derivada de un polinomio.",
        [expr("x^3-3*x")],calculus.signs)
    add(applications,"optimizacion","Optimización en intervalo cerrado","Compará extremos y candidatos interiores, o planteá el problema.",
        [expr("x^2-4*x"),*bounds("0","5"),mode()],calculus.optimization)
    add(applications,"hessiano","Clasificación por el hessiano","Comprobá y clasificá un punto crítico de un polinomio en x e y.",
        [expr("x^2-y^2","Polinomio en x e y",editor="bivariado"),
         field("x","Coordenada x",default="0"),field("y","Coordenada y",default="0")],calculus.hessian)
    add(applications,"tasa_media","Tasa media","Calculá el cambio por unidad de x en el intervalo.",
        [expr("x^2"),*bounds("1","3"),*units("s","m")],partial(calculus.rate,method="media"))
    add(applications,"tasa_instantanea","Tasa instantánea","Evaluá la derivada e identificá las unidades de la tasa.",
        [expr("x^2"),point("3"),*units("s","m")],partial(calculus.rate,method="instantanea"))
    add(applications,"tasas_relacionadas","Tasas relacionadas","Despejá dy/dt a partir de una ecuación F(x,y)=0 y de dx/dt.",
        [expr("x^2+y^2-25","Relación polinómica F(x,y)",editor="bivariado"),field("x","x",default="3"),
         field("y","y",default="4"),field("tasa_x","Tasa dx/dt",default="2"),
         field("unidad_y","Unidad de y","text","m",False),field("unidad_t","Unidad de tiempo","text","s",False)],calculus.related)
    add(applications,"elasticidad","Elasticidad puntual","Medí el cambio relativo en la función por un cambio relativo en x.",
        [expr("12-x"),point("4")],partial(calculus.rate,method="elasticidad"))
    for key,title,demo in [("rolle","Teorema de Rolle","x^2-1"),("medio","Teorema del valor medio","x^2"),
                           ("intermedio","Teorema del valor intermedio","x^3")]:
        level = [field("nivel","Valor objetivo",default="0")] if key == "intermedio" else []
        add(applications,key,title,"Comprobá las hipótesis. Elegí resolver para buscar los puntos.",
            [expr(demo),*bounds("-1","1"),*level,
             field("entrega","Resultado solicitado","select","plantear",choices=["plantear","resolver"],
                   choice_labels={"plantear":"Verificar hipótesis","resolver":"Hallar puntos"})],partial(calculus.theorem,method=key))
    add(integrals,"sustitucion","Integral por sustitución","Ajustá el diferencial y verificá por derivación.",
        [expr("2*x*(x^2+1)^3"),secondary("sustitucion","Sustitución u(x)","x^2+1",True),
         *bounds("0","1",False)],calculus.substitution)
    add(integrals,"area","Área geométrica entre curvas","Planteá el área separando los tramos donde cambia la función superior.",
        [expr("x"),secondary("segunda","Segunda función · opcional","x^2"),*bounds("0","1"),mode("plantear")],calculus.area)
    add(integrals,"promedio","Valor promedio en un intervalo","Dividí la integral definida por la longitud del intervalo.",
        [expr("x^2"),*bounds("0","3")],calculus.average)
    return entries, handlers, list(groups.items())
