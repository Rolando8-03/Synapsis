"""Ejercicios propios para la verificación de V01 y V02."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Case:
    reference: str
    route: str
    inputs: dict
    hand: str
    expected: dict
    failure: dict = field(default_factory=dict)
    invalid: dict = field(default_factory=dict)
    rejected: bool = True
    status: str = "ok"
    absent: tuple = ()


ALGEBRA = [
    Case("Sesión 01", "matrices/matrices.notacion", {"A":"1 2\n3 4","fila":"2","columna":"1"},
         "a₂₁ es la primera entrada de la segunda fila.", {"entrada":"3"}, {"fila":"3"}),
    Case("Sesión 02 / Programa 1", "sistemas/sistemas.resolver",
         {"A":"2 1\n4 3","b":"5 11","metodo":"gauss"},
         "F₂−2F₁ deja y=1 y, por sustitución, x=2.", {"particular":["2","1"]}, {"b":"5"}),
    Case("Sesión 03 / Programa 2", "sistemas/sistemas.resolver",
         {"A":"1 2\n2 5","b":"5 13","metodo":"gauss_jordan"},
         "F₂−2F₁ deja y=3. F₁−2F₂ da x=−1.", {"particular":["-1","3"]}, {"A":""}),
    Case("Sesión 04", "sistemas/original.sistema", {"matrix":[["1","2","3"],["2","4","6"]]},
         "La segunda ecuación es el doble de la primera. Queda una variable libre.", {"rango_A":1,"rango_aumentada":1},
         {"matrix":[["1","2","3"],["2","4","7"]]}, {"rango_A":1,"rango_aumentada":2}, False),
    Case("Sesión 05 / Programa 3", "vectores/vectores.combinacion", {"u":"1 2","v":"2 -1","alpha":"2","beta":"-1"},
         "2(1,2)−(2,−1)=(0,5).", {"vector":["0","5"]}, {"v":"2"}),
    Case("Sesión 06 / Programa 4", "vectores/vectores.analizar", {"vectores":"1 2\n2 4"},
         "El segundo vector es el doble del primero.", {"dimension_generado":1}, {"vectores":""}),
    Case("Sesión 07", "sistemas/sistemas.homogeneo", {"A":"1 2\n2 4"},
         "x=−2y. El núcleo tiene dimensión uno.", {"dimension":1}, {"A":""}),
    Case("Sesión 08", "sistemas/modelos.balance", {"A":"1 -1"},
         "El balance a−b=0 tiene (1,1) como proporción primitiva positiva.", {"coeficientes_enteros_minimos":[1,1]}, {"A":""}),
    Case("Sesión 09 / Programa 5", "matrices/matrices.producto", {"A":"1 2\n3 4","B":"2\n1"},
         "Los dos productos punto son 2+2 y 6+4.", {"matrix":[["4"],["10"]]}, {"B":"1 2"}),
    Case("Sesión 10", "matrices/matrices.inversa", {"A":"1 2\n0 1","metodo":"gauss_jordan"},
         "La inversa lleva −2 sobre la diagonal. Al multiplicar se recupera I.", {"matrix":[["1","-2"],["0","1"]]}, {"A":"1 2\n2 4"}),
    Case("Sesión 11", "matrices/determinantes.calcular", {"A":"2 1\n3 4","metodo":"reduccion"},
         "2·4−1·3=5.", {"valor":"5"}, {"metodo":"sarrus"}),
    Case("Sesión 12 / Programa 6", "sistemas/factorizacion.lu", {"A":"2 1\n4 3"},
         "El factor es 2 y la última fila de U queda (0,1). LU recupera A.", {"L":[["1","0"],["2","1"]],"U":[["2","1"],["0","1"]]}, {"A":"0 1\n2 1"}),
    Case("Sesión 13", "vectores/espacios.subespacio", {"variables":"x y","ecuaciones":"x-y=0"},
         "La ecuación homogénea contiene el cero y se conserva por combinación lineal.", {"es_subespacio":True},
         {"ecuaciones":"x-y=1"}, {"es_subespacio":False}, False),
    Case("Sesión 14", "vectores/espacios.base", {"vectores":"1 0\n0 1\n1 1"},
         "Los dos primeros vectores son una base y su suma produce el tercero.", {"dimension_objetivo":2}, {"vectores":""}),
    Case("Sesión 15", "vectores/espacios.fundamentales", {"A":"1 2\n2 4"},
         "Una columna pivote y una variable libre dan rango y nulidad uno.", {"rango":1,"nulidad":1}, {"A":""}),
    Case("Sesión 16", "vectores/transformaciones.formula", {"variables":"x y","componentes":"x+y\nx-y"},
         "Las imágenes de e₁=(1,0) y e₂=(0,1) son (1,1) y (1,−1).", {"lineal":True}, {"componentes":"x+z"}),
    Case("Sesión 17", "vectores/transformaciones.formula", {"variables":"x y","componentes":"x^2\ny^2"},
         "T(2,0)=(4,0) mientras 2T(1,0)=(2,0).", {"lineal":False}, {"componentes":"x+"}),
    Case("Sesión 18", "errores/errores.calcular", {"referencia":"4","aproximado":"3"},
         "|4−3|=1 y el error relativo es 1/4.", {"respecto_referencia.absoluto":"1","respecto_referencia.relativo":"1/4"}, {"referencia":"?"}),
    Case("Sesión 19 / Programa 7", "raices/raices.biseccion", {"expresion":"x-2","inferior":"1","superior":"3"},
         "El primer punto medio es 2 y f(2)=0.", {"aproximacion":"2","residual":"0"}, {"expresion":"1/(x-2)"}),
    Case("Sesión 20", "iterativos/iterativos.sor", {"A":"2 0\n0 2","b":"2 4","omega":"1"},
         "Con ω=1 y matriz diagonal, cada componente es bᵢ/2.", {"vector":["1","2"]}, {"omega":"2"}),
    Case("Sesión 21 / Programa 8", "iterativos/iterativos.comparar", {"A":"2 0\n0 2","b":"2 4"},
         "Los dos métodos dan (1,2) para la diagonal, con residuo cero.", {"referencia_exacta":["1","2"]}, {"b":"1"}),
    Case("Sesión 22 / Programa 9", "raices/raices.newton", {"expresion":"2*x-4","inicial":"0"},
         "La derivada es 2 y el paso desde cero es 0−(−4)/2=2.", {"aproximacion":"2","residual":"0"},
         {"expresion":"x^2-2"}, {"aproximacion":"0","residual":"2"}, False),
]


def ci(week, name, inputs, hand, expected, **options):
    return Case(f"Cálculo I · semana {week:02}", f"grafica/calculo.{name}", inputs, hand, expected, **options)


def cii(week, name, inputs, hand, expected, **options):
    return Case(f"Cálculo II · semana {week:02}", f"grafica/calculo.{name}", inputs, hand, expected, **options)


CALCULUS = [
    ci(1,"dominio",{"expresion":"1/(x-2)"},"El denominador excluye x=2.",{"dominio":"Union(Interval.open(-oo, 2), Interval.open(2, oo))"}),
    ci(2,"composicion",{"exterior":"sqrt(x)","interior":"x-2","punto":"6"},"La función interior da 4 y √4=2.",{"valor":"2"}),
    ci(3,"inversa",{"expresion":"x^2","inferior":"0","superior":"3"},"En la rama no negativa, y=x² implica x=√y.",{"inversa":"sqrt(y)"}),
    ci(4,"limite_factorizacion",{"expresion":"(x^2-4)/(x-2)","punto":"2"},"Cancelar x−2 fuera de 2 deja x+2, con límite 4.",{"limite":"4"}),
    ci(5,"derivada_definicion",{"expresion":"x^2"},"El cociente incremental es 2x+h y su límite es 2x.",{"derivada":"2*x"}),
    ci(6,"derivada_cadena",{"expresion":"(x^2+1)^3"},"Multiplicar 3(x²+1)² por 2x.",{"derivada":"6*x*(x**2 + 1)**2"}),
    ci(7,"derivada_logaritmica",{"expresion":"ln(2*x)"},"Para x>0, (2x)′/(2x)=1/x.",{"derivada":"1/x"}),
    ci(8,"derivada_implicita",{"izquierda":"x^2+y^2","derecha":"4"},"2x+2y·y′=0 da −x/y si y≠0.",{"derivada":"-x/y"}),
    ci(9,"parcial_sucesiva",{"expresion":"x^2*y","orden":"x y"},"Derivar primero respecto de x da 2xy y luego respecto de y da 2x.",{"derivada":"2*x"}),
    ci(10,"signos",{"expresion":"x^3-3*x"},"f″=6x cambia de signo en cero.",{"inflexiones":["0"]}),
    ci(11,"hessiano",{"expresion":"x^2-y^2","x":"0","y":"0"},"El determinante del hessiano es −4 en el crítico.",{"clasificacion":"Punto silla"}),
    ci(12,"rolle",{"expresion":"x^2","inferior":"-2","superior":"2","entrega":"resolver"},"Los extremos valen 4 y 2x se anula solo en cero.",{"puntos":"{0}"}),
    ci(13,"primitiva",{"expresion":"3*x^2"},"x³+C verifica la primitiva por derivación.",{"expresion":"1*x^3 + C"}),
    ci(14,"sustitucion",{"expresion":"2*x*(x^2+1)","sustitucion":"x^2+1","inferior":"0","superior":"1"},"Integrar u entre 1 y 2 da (4−1)/2.",{"valor":"3/2"}),
    ci(15,"promedio",{"expresion":"x^2","inferior":"0","superior":"3"},"La integral vale 9 y la longitud 3.",{"valor":"3"}),
    cii(1,"derivada_trigonometrica",{"expresion":"sin(x)"},"La derivada de sen(x) es cos(x).",{"derivada":"cos(x)"}),
    cii(2,"primitiva",{"expresion":"6*x^2"},"Derivar 2x³+C devuelve 6x².",{"expresion":"2*x^3 + C"}),
    cii(3,"por_partes",{"expresion":"x*exp(x)"},"u=x y dv=eˣ dx dejan xeˣ−eˣ+C.",{"primitiva":"(x - 1)*exp(x) + C"}),
    cii(4,"fracciones_parciales",{"expresion":"1/(x*(x+1))"},"1/x−1/(x+1) recompone el numerador 1.",{"numerador_reconstruido":"1"}),
    cii(5,"potencias_trigonometricas",{"familia":"seno_coseno","potencia":"1","potencia_coseno":"2"},"u=cos(x) da −u³/3+C.",{"primitiva":"-cos(x)**3/3 + C"}),
    cii(6,"potencias_trigonometricas",{"familia":"secante","potencia":"2"},"La derivada de tan(x) es sec²(x).",{"primitiva":"tan(x) + C"}),
    cii(7,"sustitucion_trigonometrica",{"familia":"exterior","parametro":"2","rama":"positiva"},"El radical √(x²−4) exige x≥2 en esta rama.",{"dominio":"Interval(2, oo)"}),
    cii(8,"definida",{"expresion":"x^2","inferior":"0","superior":"1"},"Evaluar x³/3 en 1 y 0 da 1/3.",{"valor":"1/3"}),
    cii(9,"cambio_neto",{"expresion":"3","inferior":"0","superior":"2"},"La tasa constante por el tiempo es 3·2=6.",{"cambio_neto":"6"}),
    cii(10,"area",{"expresion":"x","segunda":"x^2","entrega":"plantear"},
        "Los cortes 0 y 1 delimitan la región. En ella x≥x². El examen pide dejar escrita la integral.",{"cruces":["0","1"]},absent=("area","valor")),
    cii(11,"arandelas",{"expresion":"2","segunda":"1","inferior":"0","superior":"1","entrega":"resolver"},
        "El área constante de la sección es π(2²−1²)=3π.",{"volumen":"3*pi"}),
    cii(12,"longitud_arco",{"expresion":"3*x/4","inferior":"0","superior":"4","entrega":"resolver"},
        "El segmento avanza 4 y sube 3, por lo que mide 5.",{"valor":"5"}),
    cii(13,"centro_masa",{"inferior":"0","superior":"2","densidad_izquierda":"2","densidad_derecha":"2"},
        "La masa 4 es uniforme y el centro está en x=1.",{"masa":"4","centro_de_masa":"1"}),
    cii(14,"centroide",{"expresion":"1","segunda":"0","inferior":"-1","superior":"1"},
        "El centroide del rectángulo está en su centro por simetría.",{"centroide":["0","1/2"]}),
    cii(15,"trabajo_bombeo",{"altura":"4","radio":"2","entrega":"resolver"},
        "r=h/2. Integrar γ·πh²/4·(4−h) de 0 a 4 da 16πγ/3.",{"trabajo":"16*pi*gamma/3"}),
    cii(16,"trabajo_resorte",{"constante":"12","inferior":"0","superior":"1/2","entrega":"resolver"},
        "La integral de 12x de 0 a 1/2 da 3/2.",{"trabajo":"3/2"}),
]

CASES = ALGEBRA + CALCULUS
