# Variantes de las 22 sesiones de Álgebra Lineal

Se cotejaron las 22 presentaciones originales de José Andrés Munguía Cortez, incluidos los casos de práctica, con el catálogo de Synapsis. Los números indican diapositivas. Las pruebas equivalentes usan datos editables del temario, casos del catálogo y los [casos de entrega](../pruebas/entrega/casos.py). Las entradas se registran por variante. Los ejemplos de cálculo conservan sus [guías de Cálculo I](plan/04-calculo-i.md) y [Cálculo II](plan/05-calculo-ii.md).

| Sesión y diapositivas | Variante | Operación | Entrada mínima | Ejercicio y comprobación |
| --- | --- | --- | --- | --- |
| 01 · 4–8 | Notación, orden y entrada | `matrices.notacion` | $A,i,j$ | Consultar $a_{24}$ en una matriz de cuatro columnas y rechazarlo en una de tres. |
| 01 · 9–14 | Cero, identidad, diagonal y triangular | `matrices.propiedades` | $A$ | $I_3$ cumple identidad y diagonal. Una triangular con entrada superior no diagonal distingue ambas clases. |
| 01 · 15–28 | Intercambio, escalamiento, suma y suma de múltiplo | `matrices.elemental` | $A$, operación, filas, factor según corresponda | Con filas $(1,2),(3,4)$, hacer $F_2-3F_1=(0,-2)$. Repetir con intercambio y escalamiento no nulo. |
| 02 · 5–12 | Ecuaciones, matriz aumentada y orden de incógnitas | `sistemas.ecuaciones` | Variables y ecuaciones | $x_1-2x_2+x_3=0, x_2-4x_3=4$, conservar los coeficientes cero y una variable libre. |
| 02 · 13–16 | Compatibilidad única, infinita o incompatible | `sistemas.trabajo` | Matriz con columna $b$ | Comparar $(1,2\mid 3),(2,4\mid 6)$ con la segunda fila $(2,4\mid 7)$. $I_2x=(1,2)$ es único. |
| 03 · 3–13 | REF, RREF, posiciones pivote y variables libres | `matrices.ref`, `matrices.rref` | $A$ | Reducir $\begin{bmatrix}1&2&0\\2&4&1\end{bmatrix}$. Pivotes en columnas 1 y 3. |
| 03 · 11–16 | Gauss con sustitución regresiva y Gauss–Jordan | `sistemas.trabajo` | Matriz aumentada, método | $(2,1\mid 5),(1,-1\mid 1)$. Ambos métodos dan $(2,1)$ con procedimientos distintos. |
| 04 · 3–6 | Rouché–Frobenius, existencia y unicidad | `sistemas.trabajo` | Matriz aumentada, objetivo Clasificar | En $(1,1\mid 1),(2,2\mid 3)$, rangos 1 y 2. Ver la contradicción y la ficha del criterio. |
| 05 · 3–9 | Suma en $\mathbb R^n$ y paralelogramo en $\mathbb R^2$ | `vectores.suma`, `vectores.paralelogramo` | $u,v$, escalares para paralelogramo | $(2,2)+(-6,1)=(-4,3)$, que coincide con la diagonal. |
| 05 · 10–16 | Combinación, ecuación vectorial y pertenencia | `vectores.combinacion`, `vectores.generado` | Vectores y escalares, o generadores y vector objetivo | Con $e_1,e_2$, reconstruir $(3,4)$. Con solo $e_1$, $(3,4)$ queda fuera. |
| 06 · 3–10 | Producto (Ax) por filas y combinación de columnas, distributividad | `original.relaciones` | $A,u,v,c$ | Para $A=I_2$, $u=(1,2),v=(2,1),c=2$, comprobar (A(u+v)) y (A(cu)). |
| 06 · 11–23 | Dependencia de columnas, vectores nulos, múltiplos e independencia | `vectores.analizar` | Familia de vectores | $u=(1,2),v=(2,4)$. Exhibir una relación no trivial. Con $e_1,e_2$ solo hay relación trivial. |
| 06 · 24 | Dependencia de polinomios | `espacios.polinomios` | Familia y grado | $x-2x^2, x^2-4x, -7x+8x^2$. Comprobar dependencia por coeficientes. |
| 07 · 3–6 | Homogéneos y base del núcleo | `sistemas.homogeneo` | $A$ | $(3,5,-4),(1,-9,-4)$. Multiplicar $A$ por la dirección obtenida y verificar cero. |
| 07 · 7–9 | Particular más espacio homogéneo | `original.sistema` | Matriz aumentada | $x+y=3$. Verificar $Ax_p=3, Av=0$. |
| 08 · 3–6 y 23–29 | Economía de intercambio y escala de precios | `modelos.economia` | Matriz de intercambio y unidad declarada, precio opcional | Intercambio simétrico de dos sectores, matriz $\begin{bmatrix}0&1\\1&0\end{bmatrix}$. Los precios de equilibrio coinciden. |
| 08 · 7–10 y 27 | Balance químico por elemento | `modelos.balance` | Matriz de conservación | Propano y oxígeno. Comprobar los coeficientes $1,5,3,4$ por carbono, hidrógeno y oxígeno. |
| 08 · 11–15 y 28 | Dieta exacta, porciones no negativas y conversión a masa | `modelos.dieta` | $A,b$, peso de porción opcional | Leche, soya y suero. Reconstruir $33,45,3$ g y obtener $27.72,39.19,23.32$ g aproximadamente. |
| 08 · 16–22 | Conservación del flujo por nodo, familia y restricciones | `modelos.flujos` | $A,b$ | Una entrada de 30 con dos salidas. Cada salida queda entre 0 y 30. |
| 09 · 3–7 | Igualdad, suma, resta y múltiplo escalar | `matrices.comparar`, `matrices.suma`, `matrices.resta`, `matrices.escalar` | $A,B$ para dos operandos o $A,k$ | Con $I_2$ y $2I_2$, comparar y obtener $3I_2,-I_2$. Multiplicar $I_2$ por 2. |
| 09 · 8–12 | Producto rectangular, dimensiones y no conmutatividad | `matrices.producto`, `matrices.comparar` | $A,B$ | $(1,2)(3,4)^T=11$. Dos matrices elementales fuera de la diagonal muestran $AB\ne BA$. |
| 09 · 13–16 | Transpuesta y propiedades | `matrices.transpuesta`, `matrices.propiedades` | $A$ | Transponer una fila $(1,2,3)$ y verificar que cambia a $3\times 1$. |
| 10 · 3–14 | Inversa de orden dos, adjugata, Gauss–Jordan y singularidad | `matrices.inversa` | $A$, método opcional | $\begin{bmatrix}2&1\\1&1\end{bmatrix}$. Verificar ambas rutas con $AA^{-1}=I$. Matriz singular con dos filas proporcionales. |
| 10 · 15–20 | Resolver con inversa y equivalencias de invertibilidad | `sistemas.inversa`, `matrices.teorema_invertible` | $A,b$ o solo $A$ | Usar $A=I_2, b=(2,3)$. Confirmar rango, determinante y solución. |
| 11 · 3–18 | Determinante de orden dos, orientación, menores y cofactores | `determinantes.calcular`, `determinantes.cofactores`, `libros.area_orientada` | $A$ y método para determinante | Intercambiar dos columnas de $I_2$, cambia el signo. Expandir una matriz triangular de orden 3. |
| 11 · 19–27 | Propiedades por fila y columna, triangular y Sarrus | `original.propiedades_det`, `determinantes.calcular` | $A$, método o parámetros de la operación elemental | Diagonal $(2,3,4)$, determinante 24. Sarrus coincide con reducción y se rechaza fuera de orden 3. |
| 11 · 28–38 | Cramer y valores excepcionales del parámetro | `sistemas.cramer`, `sistemas.parametrico` | $A,b$ o ecuaciones, variables y parámetro | $sx+y=1, 2x+sy=0$. Identificar $s=\pm\sqrt2$ y clasificar por rangos en esos casos. |
| 11 · 39–42 | Adjunta y cofactores | `original.inversa_adjunta` | $A$ | Para $\begin{bmatrix}2&1\\1&1\end{bmatrix}$ transponer cofactores y verificar la inversa. |
| 12 · 3–16 | Dos sustituciones triangulares y comprobación | `original.triangular`, `factorizacion.resolver` | $L,U,b$ o $A,b$ y método | $A=((2,1),(4,3)), b=(5,11)$ da $x=(2,1)$. Mostrar $Ly=b$ y $Ux=y$. |
| 12 · 17–24 | Multiplicadores, solo (LU) y pivoteo | `factorizacion.lu`, `factorizacion.plu` | $A$ | $A=((0,1),(1,0))$ requiere permutar para obtener $PA=LU$. |
| 13 · 3–12 | Axiomas de espacio vectorial y criterio de subespacio | `espacios.subespacio` para las operaciones usuales | Variables y ecuaciones lineales | Verificar origen, suma y producto escalar en $x=2y$. El catálogo trabaja sobre operaciones usuales. |
| 13 · 13–19 | Subespacio homogéneo y conjunto afín que falla en el origen | `espacios.subespacio` | Variables y ecuaciones | Contrastar $x=2y$ con $x=3$. |
| 13 · 20–25 | Combinar vectores de $\mathbb R^5$ y diagnosticar fuera del generado | `vectores.generado` | Generadores y vector objetivo | Con $e_1,e_2\in\mathbb R^5$, $2e_1+e_2$ pertenece y $e_3$ queda fuera. |
| 14 · 3–12 | Generadores con y sin dimensión ambiente completa | `vectores.analizar`, `espacios.base` | Familia de vectores, dimensión ambiente de la familia | $(2,10),(10,8)$ generan $\mathbb R^2$. Los mismos vectores con tercera entrada cero no generan $\mathbb R^3$. |
| 14 · 13–27 | Base, dimensión, coordenadas y base por ecuaciones | `espacios.base`, `espacios.coordenadas`, `espacios.subespacio` | Familia, o base y $v$, o ecuaciones | $x=2y, z=0$ tiene base $(2,1,0)$ y dimensión 1. $(4,2,0)$ tiene coordenada 2. |
| 15 · 3–22 | Subespacios cartesianos, bases y dimensión en $\mathbb R^2,\mathbb R^3,\mathbb R^4$ | `espacios.subespacio`, `espacios.fundamentales` | Variables y ecuaciones o $A$ | En $a=0, 3b-c=0$, obtener base y dimensión 2. Verificar rango–nulidad. |
| 15 · 23–35 | Generación con dependencia, independencia y polinomios | `vectores.analizar`, `espacios.polinomios` | Familia, grado en polinomios | $(1,0),(0,1),(1,1)$ generan el plano y son dependientes. $1,x,x^2$ forman base de $P_2$. |
| 16 · 3–14 | Aditividad, homogeneidad y contraejemplos | `transformaciones.formula` | Variables y componentes | $T(x,y)=(x+y,x-y,3y)$ es lineal. $T(x,y)=(x^2,y)$ falla bajo escalamiento. |
| 16 · 15–19 | Imágenes de base, evaluación y matriz | `transformaciones.desde_imagenes`, `transformaciones.analizar` | Base e imágenes o $A$, vector opcional | Usar $T(e_1)=(1,2,3),T(e_2)=(-4,0,5)$. Verificar $T(e_1+e_2)=(-3,2,8)$. |
| 16 · 20–28 | Núcleo, imagen, rango y nulidad | `transformaciones.analizar` | $A$ | $T(x,y,z)=(x,y)$, rango 2, nulidad 1, núcleo generado por $e_3$. |
| 17 · 3–8 | Proyección, constante afín, cuadrados y extensión lineal | `transformaciones.formula`, `transformaciones.desde_imagenes` | Variables y componentes, o base e imágenes | $T(0)\ne0$ para $(1,y)$, y $(x^2,y^2)$ incumple homogeneidad. |
| 17 · 9–12 | Núcleo e imagen de una proyección o funcional | `transformaciones.formula`, `transformaciones.analizar` | Componentes o $A$ | $T(x,y)=x+y$, núcleo generado por $(-1,1)$, rango 1. |
| 18 · 3–16 | Taylor, truncamiento, redondeo y acumulación | `errores.taylor`, `errores.redondeo`, `errores.acumulacion` | Punto y orden, valor y precisión, o capital, tasa y períodos | Comparar $e^{0.5}$ con su Taylor y los cambios tras redondear a cuatro decimales. |
| 18 · 17–23 | Overflow, underflow, épsilon, exactitud y error relativo | `errores.maquina`, `errores.exactitud`, `errores.calcular` | $a,b$, mediciones y referencia, o aproximación y referencia | Referencia 250 y aproximación 248.5, error absoluto 1.5 y porcentual 0.6. |
| 18 · 24–28 | Propagación y notación posicional | `errores.propagacion`, `bases.enteros` | $f,x,\Delta x$ o numeral y bases | Para $x^2$ en $x=2,\Delta x=.01$, diferencial .04. Convertir $10101101_2=173$. |
| 19 · 3–13 | Bolzano, continuidad, tolerancia, error y cota de bisección | `raices.biseccion` | $f,a,b$, criterio y tolerancia opcionales | $x^2-2$ en $[1,2]$, verificar signos y disminución de la cota. Rechazar $1/x$ en $[-1,1]$. |
| 19 · 14–21 | Tabla, raíces por intervalo y contraste de aproximaciones | `raices.biseccion` | $f,a,b$ | $x^4-5x^3+0.5x^2-11x+10$ en $[0,1]$. La tabla conserva intervalo y signo en cada fila. |
| 20 · 3–12 y 15 | Matriz de iteración, métodos Jacobi y Gauss–Seidel, criterios | `iterativos.jacobi`, `iterativos.gauss_seidel` | $A,b$, semilla opcional | $A=((4,1),(2,3)), b=(1,2)$. Desde cero la primera iteración es $(1/4,2/3)$ y $(1/4,1/2)$. |
| 20 · 13–17 | Dominancia estricta, reordenamiento, radio espectral y SOR | `iterativos.dominancia`, `iterativos.jacobi`, `iterativos.sor` | $A$, o $A,b$ y $\omega$ para SOR | Intercambiar las filas de una matriz diagonal ordenada al revés. $omega=1$ reproduce Gauss–Seidel. |
| 21 · Ejemplos 1–2 y Chapra 11.3 | Misma semilla, comparación con solución directa y error porcentual por componente | `iterativos.comparar`, `sistemas.resolver` | $A,b$, tolerancia o criterio si se quiere replicar la tabla de clase | Con $A=((4,1),(2,3)), b=(1,2)$ contrastar con $x=(1/10,3/5)$ y comparar las iteraciones. |
| 22 · 3–24 | Newton analítico, criterio, tangente, multiplicidad y estancamiento | `raices.newton` | $f,x_0$, tolerancia y multiplicidad opcionales | $e^{-x}-x$ desde 0 da aproximadamente .567143. $x^2-2$ desde 0 detecta derivada nula. |
| 22 · 25–28 | Diferencias adelante, atrás, central y aplicación de paso (h) en Newton | `raices.diferencias`, `raices.newton` | $f,x,h$ o $f,x_0,$ esquema y (h) | $x^3-2x-5$ en 2 con $h=.01$. Las pendientes son 10.0601, 9.9401 y 10.0001. |
| 22 · 29–31 | Secante con dos semillas y error | `raices.secante` | $f,x_0,x_1$ | $e^{-x}-x$, semillas 0 y 1. Comparar con Newton y verificar el residual. |
| 22 · 32–33 | Horner para (p,p'), Newton con Horner y deflación | `raices.horner`, `raices.newton` | $p,r$ y acción, o $p,x_0$ y modo Horner | $p=x^5-4x^4+5x^3-6x+4$, $r=-1$. Verificar resto cero y reconstrucción exacta. Rechazar $r=0$ con tolerancia cero. |
| 22 · práctica final | Refinar una raíz en el polinomio original. Comparar raíces reales y complejas | `raices.newton`, `raices.horner` | Polinomio original y semilla real o candidato | Del cociente deflactado, reiniciar en otra raíz real y validar el residuo original. El método de Bairstow y la enumeración de todas las raíces complejas quedan fuera del alcance de los métodos reales disponibles. |

## Teoremas usados en el procedimiento

| Compendio | Hipótesis que se comprueban | Evidencia presentada al resolver |
| --- | --- | --- |
| §3 · Rouché–Frobenius | $A$ y $b$ representan las mismas ecuaciones sobre los reales. | Rangos, cantidad de incógnitas y clasificación. La reducción original conserva también la última fila no nula. |
| §3 y §9 · Matriz invertible | $A$ cuadrada. | Determinante en inversa y Cramer. La ficha dedicada contrasta determinante y rango, y distingue la matriz singular. |
| §18 y §21 · Rango–nulidad | Transformación lineal y dominio de dimensión finita. | Columnas pivote originales, vectores del núcleo, sus productos nulos y la suma de dimensiones. |
| §26 · Bolzano | Continuidad en un intervalo cerrado y signos opuestos en los extremos. | Intervalo y evaluaciones. La garantía numérica depende de que los signos se hayan determinado de forma fiable. |
| §25 · Dominancia y criterio espectral | Jacobi o Gauss–Seidel para la condición de filas. Iteración lineal estacionaria para el criterio espectral. | Márgenes por fila, matriz $G$ y norma infinito. En orden hasta cuatro, se muestra además una estimación de (
ho(G)) cuando puede calcularse. Una norma menor que uno certifica la condición. |

Los resultados describen el modelo matemático de las diapositivas. Las actividades docentes sobre motivación, historia y demostraciones generales sirven como material de estudio. La calculadora aplica sus criterios a los datos del ejercicio.

## Reproducción

```sh
python -m unittest discover -s pruebas -q
node --test pruebas/test_expression_input.mjs
python -m plataformas.web --check
```

El índice de las sesiones ejecuta sus ejemplos desde [temario.py](../temario.py). La auditoría de rutas y de pasos está en [test_procedimientos.py](../pruebas/test_procedimientos.py). Los valores de Horner, diferencias, dieta y fichas tienen [pruebas independientes](../pruebas/test_fase_procedimientos_pdf.py).
