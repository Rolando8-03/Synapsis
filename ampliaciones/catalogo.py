"""Entradas y rutas de las ampliaciones de libros en el catálogo de Synapsis."""
from functools import partial

from . import algebra as a, geometria as g, numerico as n, redes as r


def entries(field, spec):
    definitions, handlers, groups = {},{},{}
    def add(module, group, key, title, description, fields, handler):
        op = "libros."+key
        definitions[op] = spec(title,description,fields)
        handlers[op] = handler
        groups.setdefault(module,{}).setdefault(group,[]).append(op)

    def mat(name="A", label="Matriz A", default="1 0\n1 1\n0 1"):
        return field(name,label,"matrix",default)

    def vec(name="b", label="Vector b", default="1 3 2"):
        return field(name,label,"vector",default)

    def scalar(name,label,default,required=True):
        return field(name,label,"scalar",default,required)

    def expr(name="expresion",label="Función f(x)",default="x^2",variables=None,required=True):
        opts = {"variables":variables} if variables else {}
        return field(name,label,"expression",default,required,visual=True,**opts)

    def number(name,label,default):
        return field(name,label,"integer",default)

    def select(name,label,*choices):
        return field(name,label,"select",choices[0],choices=list(choices))

    def toggle(name,label,default=False):
        return field(name,label,"boolean",default)

    def limits(start="0",end="1"):
        return [scalar("inferior","Desde",start),scalar("superior","Hasta",end)]

    geom, orth, eig, applications = "Geometría de los libros","Ortogonalidad y ajuste","Espectro y factorizaciones","Redes y aplicaciones"
    interp, numeric, ode = "Interpolación y ajuste","Aproximación numérica","Ecuaciones diferenciales"
    points = mat("puntos","Pares (x, y)","0 1\n1 2\n2 5\n3 10")
    digits = number("cifras","Cifras significativas simuladas","5")
    body = select("cuerpo","Cuerpo","real","complejo")
    add("sistemas",geom,"intersecciones","Intersección de rectas y planos","Ingresá coeficientes A y términos independientes b. Se usan rangos exactos. En 2D podés desplazar la segunda recta y en 3D girar los planos.",
        [mat(default="1 1\n1 -1"),vec(default="3 1")],g.intersections)
    add("vectores",geom,"transformacion","Transformación del plano y cambio de base","Desplazá el vector y compará v, T(v) y la imagen de la base.",
        [mat(label="Transformación A",default="2 1\n0 1"), mat("B","Base por columnas","1 1\n0 1"),vec("v","Vector v","2 1")],g.transform)
    add("vectores",geom,"normas","Tres normas y bolas unitarias","Compará las normas del mismo vector y elegí la bola unitaria que querés ver.",
        [vec("v","Vector del plano","3 4"),select("norma","Bola unitaria","uno","dos","infinito")],g.norms)
    add("matrices",geom,"area_orientada","Determinante como área orientada","Arrastrá la segunda columna para cruzar la recta de dependencia.",
        [mat(default="2 1\n1 3")],g.oriented_area)
    add("sistemas","Estabilidad numérica","pivoteo","Pivoteo con redondeo simulado","Compará eliminación con y sin pivoteo parcial bajo la misma precisión.",
        [mat(default="1/10000 1\n1 1"),vec(default="1 2"),number("cifras","Cifras significativas simuladas","3")],a.pivoting)
    add("sistemas","Estabilidad numérica","sensibilidad","Sensibilidad a perturbaciones","Medí el cambio relativo de la solución al perturbar b.",
        [mat(default="1 1\n1 101/100"),vec(default="2 201/100"),vec("delta","Perturbación Δb","0 1/100"),select("norma","Norma inducida","uno","infinito")],a.sensitivity)
    add("raices","Exploración y punto fijo","intervalos","Intervalos candidatos","Buscá signos opuestos y detectá intervalos cuyo dominio requiere revisión.",
        [expr(default="(x-2)/x"),*limits("-3","4"),number("n","Subintervalos","12")],n.candidates)
    add("raices","Exploración y punto fijo","punto_fijo","Punto fijo con dos despejes","Compará dos iteraciones. La cota requiere una contracción demostrada y que el intervalo sea invariante.",
        [expr(default="x^2-x"),expr("g1","Despeje g₁(x)","(x+1)/2"),expr("g2","Despeje g₂(x)","x^2"),
         *limits("3/4","5/4"),scalar("inicial","Valor inicial","9/10"),scalar("tolerancia","Tolerancia","1e-5"),number("n","Iteraciones","24")],n.fixed_point)
    add("vectores",orth,"proyeccion","Proyección sobre un subespacio","Obtené la proyección y un residuo ortogonal a toda la base.",
        [mat(label="Generadores por columnas"),vec(default="1 0 1")],a.project)
    add("vectores",orth,"gram_schmidt","Gram–Schmidt","Restá cada proyección y normalizá las columnas independientes.",[mat()],a.gram_schmidt)
    add("matrices",orth,"qr","QR exacta y comparación de variantes","Verificá QᵀQ y QR. Compará el efecto del redondeo en Gram–Schmidt clásico y modificado.",
        [mat(default="1 1 1\n1/1000 0 0\n0 1/1000 0\n0 0 1/1000"),toggle("comparar","Comparar variantes con redondeo",True),digits],a.qr_operation)
    add("sistemas",orth,"minimos_cuadrados","Mínimos cuadrados","Aproximá Ax=b y comprobá la ortogonalidad del residuo.",
        [mat(),vec(default="1 0 1")],a.fit)
    add("matrices",eig,"valores_propios","Valores propios","Construí el polinomio característico de una matriz de orden hasta tres.",
        [mat(default="2 1\n0 3"),body],a.eigenvalues)
    add("matrices",eig,"espacio_propio","Espacio propio","Con un valor real o complejo, resolvé el sistema homogéneo y verificá Av=λv.",
        [mat(default="2 1\n0 3"),scalar("lambda","Parte real de λ","2"),scalar("imag","Parte imaginaria de λ","0",False)],a.eigenspace)
    add("matrices",eig,"diagonalizacion","Diagonalización","Compará multiplicidades, cambiá de base y comprobá AP=PD.",
        [mat(default="2 1\n0 3"),body],a.diagonalize)
    add("matrices",eig,"espectral","Teorema espectral","Para matrices reales simétricas de orden dos o tres, encontrá una base propia ortonormal y visualizá los ejes en 2D.",
        [mat(default="2 1\n1 2")],a.spectral)
    add("iterativos",eig,"potencia","Método de la potencia","Normalizá cada iteración y medí el residuo del par propio aproximado.",
        [mat(default="3 1\n1 2"),vec(label="Semilla",default="1 0"),scalar("tolerancia","Tolerancia","1e-8"),number("n","Iteraciones","40")],n.power)
    add("matrices",applications,"markov","Cadenas de Markov","Usá probabilidades por columna y compará con un ciclo que parte del mismo estado inicial.",
        [mat(label="Transición P",default="3/4 1/3\n1/4 2/3"),vec(label="Estado inicial",default="1 0"),number("pasos","Pasos","8")],g.markov)
    add("matrices",eig,"svd","SVD y truncamiento","Reconstruí una matriz rectangular y medí la pérdida al recortar el rango.",
        [mat(default="3 0\n0 2\n0 0"),field("rango","Rango de truncamiento · opcional","integer","",False)],a.singular_values)
    add("matrices",eig,"compresion","Compresión de una imagen con SVD","Editá una imagen en tonos de gris de hasta 6 × 6. Compará sus píxeles con los del rango truncado.",
        [mat(label="Intensidades de la imagen",default="255 255 0 0\n255 220 0 0\n0 0 140 140\n0 0 140 120"),
         number("rango","Rango de truncamiento","2")],lambda data,ctx: a.singular_values({**data,"imagen":True},ctx))
    add("grafica",interp,"regresion","Regresión lineal","Mové un punto y comprobá el efecto en la recta y la suma de residuos cuadrados.",[points],g.regression)
    for method,title in [("newton","Interpolación de Newton"),("lagrange","Interpolación de Lagrange")]:
        add("grafica",interp,method,title,"Construí el interpolante y comprobá que pasa por cada nodo.",[points],partial(n.interpolation,method=method))
    add("grafica",interp,"spline","Spline cúbico natural","Obtené los tramos con condiciones naturales y continuidad hasta la segunda derivada.",[points],n.spline)
    add("grafica",numeric,"cuadratura","Trapecios y Simpson 1/3","Compará pesos, refinamientos y cotas. Ingresá un número par de subintervalos.",
        [expr(),*limits(),number("n","Subintervalos pares","6")],n.quadrature)
    add("grafica",numeric,"romberg","Integración de Romberg","Construí la tabla triangular por refinamiento y extrapolación.",
        [expr(default="x^4"),*limits(),number("n","Niveles","4")],partial(n.quadrature,romberg=True))
    for method,label in [("adelante","Hacia adelante"),("atras","Hacia atrás"),("centrada","Centrada"),("richardson","Extrapolación de Richardson")]:
        add("grafica",numeric,method,label,"Variá h y separá la referencia, la aproximación y el redondeo simulado.",
            [expr(default="x^3"),scalar("x","Punto x","1"),scalar("h","Paso h","1/10"),digits],partial(n.finite_difference,method=method))
    for method,title in [("euler","Método de Euler"),("heun","Método de Heun"),("rk4","Runge–Kutta de orden 4")]:
        add("grafica",ode,method,title,"Resuelve una EDO polinómica y′=f(x,y). Podés contrastar con una solución polinómica verificada.",
            [expr(label="Pendiente f(x,y)",default="2*x",variables=["x","y"]),scalar("x","x inicial","0"),scalar("y","y inicial","1"),
             scalar("h","Paso h","1/10"),number("n","Pasos","10"),expr("referencia","Solución exacta · opcional","x^2+1",required=False)],
            partial(n.ode,method=method))
    add("sistemas",applications,"red_electrica","Red de conductancias","Aplicá la ley de corrientes de Kirchhoff a una red resistiva ideal.",
        [mat(label="Conductancias",default="0 2 1\n2 0 1\n1 1 0"),vec(label="Corrientes externas",default="1 0 -1")],r.circuits)
    add("matrices",applications,"caminos","Caminos de peso mínimo","Usá una matriz de adyacencia dirigida para seguir las aristas de Dijkstra.",
        [mat(label="Adyacencia ponderada",default="0 2 6\n0 0 1\n0 0 0"),number("origen","Vértice de origen","1"),number("destino","Vértice de destino","3")],r.shortest)
    add("bases",applications,"codigo_binario","Código binario y síndrome","Introduce una palabra válida, una matriz de paridad H y un patrón de error.",
        [mat(label="Matriz binaria de paridad H",default="1 1 0\n0 1 1"),vec(label="Palabra original",default="1 1 1"),vec("error","Patrón de error","0 1 0")],r.binary)
    return definitions, handlers, groups
