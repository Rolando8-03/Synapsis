"""Índice de trabajo basado en las sesiones 01–20 de Álgebra Lineal."""


def tool(module, operation, **example):
    return module, operation, example or None


def mat(operation, **example):
    return tool("matrices", operation, **example)


def sys(operation, **example):
    return tool("sistemas", operation, **example)


def vec(operation, **example):
    return tool("vectores", operation, **example)


def numerical(module, name, **example):
    return tool(module, f"{module}.{name}", **example)


SESSIONS = [
    (1, "Notación matricial", "Encontrá entradas, orden y diagonales. Practicá intercambio, escala y reemplazo de filas.",
     r"A=(a_{ij})_{m\times n}", [mat("matrices.notacion"), mat("matrices.elemental"), mat("matrices.propiedades")]),
    (2, "Sistemas lineales", "Pasá de las ecuaciones a la matriz aumentada. Probá sistemas compatibles, incompatibles, homogéneos y rectangulares.",
     r"Ax=b\iff[A\mid b]", [sys("sistemas.ecuaciones", variables="x1 x2 x3", ecuaciones="x1-2x2+x3=0\nx2-4x3=4"),
                               sys("original.sistema", matrix=[["1","1","2"],["2","2","7"]])]),
    (3, "Forma escalonada y reducida", "Encontrá pivotes y variables libres, seguí las operaciones por fila y compará las dos formas.",
     r"A\overset{\rm filas}{\sim}\operatorname{REF}(A)\overset{\rm filas}{\sim}\operatorname{RREF}(A)",
     [mat("matrices.ref"), mat("matrices.rref"), sys("original.sistema")]),
    (4, "Existencia y unicidad", "Usá los rangos y el número de incógnitas para distinguir los tres casos.",
     r"Ax=b\ \text{compatible}\iff\operatorname{rang}(A)=\operatorname{rang}([A\mid b])",
     [sys("original.sistema", matrix=[["1","2","3"],["2","4","6"]])]),
    (5, "Combinación lineal", "Calculá combinaciones, comprobá pertenencia al espacio generado y pasá de la ecuación vectorial al sistema.",
     r"c_1v_1+\cdots+c_pv_p=b",
     [vec("vectores.combinacion"), vec("vectores.paralelogramo", u="2 2", v="-6 1"), vec("vectores.generado", vectores="1 -2 -5\n2 5 6", v="7 4 -3"), sys("sistemas.ecuaciones")]),
    (6, "Independencia lineal", "Probá dependencia en vectores y polinomios. Revisá las relaciones que producen el cero.",
     r"c_1v_1+\cdots+c_pv_p=0",
     [vec("vectores.analizar", vectores="1 -3 0\n3 0 4\n11 -6 12"), vec("espacios.polinomios"), vec("original.relaciones")]),
    (7, "Sistemas homogéneos", "Obtené una base del núcleo y relacioná la solución particular con las direcciones de la familia afín.",
     r"x=x_p+v,\quad v\in\ker A",
     [sys("sistemas.homogeneo", A="3 5 -4\n1 -9 -4"), sys("original.sistema")]),
    (8, "Aplicaciones de sistemas", "Modelá intercambio entre sectores, conservación por elemento, flujos de tráfico y mezclas a partir de balances medibles.",
     r"(I-M)p=0,\quad Ac=0,\quad Ax=b",
     [sys("modelos.economia", A="0 20 20\n5 0 30\n30 70 0", precio="100"),
      sys("modelos.balance", A="3 0 -1 0\n8 0 0 -2\n0 2 -2 -1"),
      sys("modelos.flujos", A="1 1 0 0 0\n0 1 -1 1 0\n0 0 0 1 1\n1 0 0 0 1\n0 0 1 0 0", b="800 300 500 600 400"),
      sys("sistemas.ecuaciones", variables="x1 x2 x3", ecuaciones="36x1+51x2+13x3=33\n52x1+34x2+74x3=45\n7x2+1.1x3=3")]),
    (9, "Operaciones con matrices", "Trabajá con órdenes compatibles, suma, producto, escala y transposición. Compará AB con BA.",
     r"(AB)_{ij}=\sum_k a_{ik}b_{kj}",
     [mat("matrices.suma"), mat("matrices.producto"), mat("matrices.comparar"), mat("matrices.transpuesta"), mat("matrices.propiedades")]),
    (10, "Matriz inversa", "Calculá la inversa usando Gauss-Jordan o adjugata. Revisá las condiciones equivalentes de invertibilidad.",
     r"[A\mid I]\overset{\rm filas}{\sim}[I\mid A^{-1}]",
     [mat("matrices.inversa"), mat("original.inversa_adjunta"), mat("matrices.teorema_invertible"), sys("sistemas.inversa")]),
    (11, "Determinantes y regla de Cramer", "Compará Sarrus, cofactores y reducción. Inspeccioná el efecto de operaciones elementales y los valores singulares de un parámetro.",
     r"x_i=\frac{\det A_i(b)}{\det A},\qquad\det A\ne0",
     [mat("determinantes.calcular", A="2 -1 0\n-2 3 4\n-5 1 6", metodo="sarrus"),
      mat("determinantes.cofactores"), mat("original.propiedades_det"), sys("sistemas.cramer"), sys("sistemas.parametrico", parametro="s")]),
    (12, "Factorización LU", "Calculá solo los factores de A, usá PLU cuando haya permutaciones o resolvé un sistema en una operación independiente.",
     r"A=LU,\qquad Ly=b,\quad Ux=y",
     [sys("factorizacion.lu", A="2 1\n1 -1"), sys("factorizacion.plu"), sys("factorizacion.resolver"), sys("original.triangular")]),
    (13, "Espacios vectoriales", "Verificá los criterios de subespacio para ecuaciones lineales y buscá combinaciones de un sistema de generadores.",
     r"u,v\in H,\ \alpha,\beta\in\mathbb R\implies\alpha u+\beta v\in H",
     [vec("espacios.subespacio", variables="x y", ecuaciones="x=3"), vec("vectores.generado"), vec("espacios.polinomios")]),
    (14, "Generadores, bases y dimensión", "Probá generación e independencia en el espacio objetivo. Calculá bases desde ecuaciones o desde una familia de vectores.",
     r"\operatorname{span}(v_1,\dots,v_k)=V",
     [vec("espacios.base", vectores="2 10\n10 8"), vec("espacios.subespacio"), vec("espacios.coordenadas"), vec("vectores.analizar")]),
    (15, "Subespacios vectoriales", "Analizá condiciones homogéneas y afines. Operá con bases, suma e intersección de subespacios.",
     r"H=\ker A\quad\implies\quad\dim H=n-\operatorname{rang}A",
     [vec("espacios.subespacio", variables="a b c d", ecuaciones="3b-c=0\na=0"), vec("espacios.fundamentales"),
      vec("espacios.suma"), vec("espacios.interseccion"), vec("espacios.base")]),
    (16, "Transformaciones lineales", "Comprobá la linealidad, encontrá la matriz desde imágenes de una base y calculá núcleo, imagen, rango y nulidad.",
     r"T(\alpha u+\beta v)=\alpha T(u)+\beta T(v)",
     [vec("transformaciones.formula", variables="x y", componentes="x+y\nx-y\n3y"),
      vec("transformaciones.desde_imagenes", base_dominio="1 0\n0 1", imagenes="1 2 3\n-4 0 5"),
      vec("transformaciones.analizar")]),
    (17, "Transformaciones · práctica", "Contrastá una transformación polinómica no lineal con una proyección. Evaluá la transformación en otro vector.",
     r"\dim V=\operatorname{rang}(T)+\operatorname{nul}(T)",
     [vec("transformaciones.formula", variables="x y", componentes="x^2\ny^2"),
      vec("transformaciones.analizar", A="1 0\n-1 0\n3 5", v="2 4"), vec("transformaciones.representar")]),
    (18, "Error y precisión", "Calculá medidas directas y propagación. Compará truncamiento y redondeo a lo largo de una simulación.",
     r"E_t=x_v-x_a,\qquad\Delta y\approx f'(x)\Delta x",
     [numerical("errores","calcular", referencia="3.1415926536", aproximado="3.1416"),
      numerical("errores","propagacion", expresion="sin(x)", x="0.5", delta="0.002"),
      numerical("errores","redondeo"), numerical("errores","acumulacion"), numerical("errores","taylor"),
      numerical("errores","exactitud"), numerical("errores","maquina"),
      tool("bases","bases.enteros")]),
    (19, "Raíces por bisección", "Compará cota, residual y error relativo. Podés limitar la tabla a cinco iteraciones, como en el ejercicio de clase.",
     r"x_m=\frac{a+b}{2},\qquad |r-x_m|\leq\frac{b-a}{2}",
     [numerical("raices","biseccion", expresion="x^3-4*x-1", inferior="2", superior="3", tolerancia_x="1e-4", max_iteraciones="5"),
      numerical("raices","falsa_posicion")]),
    (20, "Métodos iterativos", "Compará Jacobi, Gauss-Seidel y SOR. Elegí la norma y el criterio, y revisá la dominancia antes de iterar.",
     r"x_i^{(k+1)}=(1-\omega)x_i^{(k)}+\omega x_i^{\rm GS}",
     [numerical("iterativos","jacobi"), numerical("iterativos","gauss_seidel"),
      numerical("iterativos","sor", omega="1.2"), numerical("iterativos","dominancia")]),
    (21, "Jacobi y Gauss-Seidel · comparación", "Despejá cada ecuación y compará qué componentes usa cada método y cómo cambia el error.",
     r"x_i^{(k+1)}=\frac{b_i-\sum_{j\ne i}a_{ij}x_j}{a_{ii}}",
     [numerical("iterativos","comparar", tolerancia_absoluta="1e-4", tolerancia_relativa="0", criterio="paso_absoluto"),
      numerical("iterativos","dominancia")]),
    (22, "Newton-Raphson", "Seguí cada tangente, la derivada, el error porcentual y el residuo. Indicá la multiplicidad si se conoce.",
     r"x_{k+1}=x_k-m\frac{f(x_k)}{f'(x_k)}",
     [numerical("raices","newton", expresion="exp(-x)-x", inicial="0", tolerancia_x="1e-4"),
      numerical("raices","newton", expresion="(x-1)^3", inicial="1.75", multiplicidad="3")]),
]
