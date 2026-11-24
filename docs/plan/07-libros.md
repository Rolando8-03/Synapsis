# Ampliaciones de los cuatro libros

Estas fases amplían el catálogo de Synapsis. Las fuentes de estudio incluyen Grossman, *Álgebra lineal*, 7.ª ed., caps. 5–8; Lay, *Álgebra lineal y sus aplicaciones*, 3.ª ed., caps. 4–7; Poole, *Álgebra lineal. Una introducción moderna*, 3.ª ed., §§1.3, 2.2, 4.5, 5.3 y cap. 7; Chapra y Canale, *Métodos numéricos para ingenieros*, 5.ª ed., caps. 5–6, 9–11, 17–18, 21–23 y 25. Vinculá cada ampliación con la operación del curso que consume sus resultados.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| L01 ✓ | Graficar intersecciones de rectas o planos. | Comenzar en 2D con dos rectas editables. En otra sesión enlazar el caso 3D a rangos exactos; para más dimensiones mostrar pivotes. |
| L02 ✓ | Visualizar una transformación del plano. | Al mover un vector se actualizan su imagen y las imágenes de la base. En cambio de base mantener fijo el vector geométrico. |
| L03 ✓ | Comparar tres normas de un vector. | Para (3,4) obtener 7, 5 y 4; mostrar la bola unitaria correspondiente y enlazar con los iterativos. |
| L04 ✓ | Mostrar determinante como área orientada. | Arrastrar una columna hasta la dependencia anula el área; cruzar la otra cambia el signo. |
| L05 ✓ | Comparar pivoteo con precisión limitada. | Con el mismo A y b contrastar referencia racional y redondeo simulado con y sin pivoteo; señalar el paso que amplifica el error. |
| L06 ✓ | Calcular sensibilidad a perturbaciones de b. | Mostrar norma elegida, número de condición si A es invertible y cambio relativo medido. Separar condicionamiento del error del algoritmo. |
| L07 ✓ | Explorar intervalos candidatos a raíces. | Marcar cambios de signo y discontinuidades; una raíz de multiplicidad par puede escapar a la exploración. |
| L08 ✓ | Incorporar punto fijo. | Comparar dos despejes para la misma raíz; graficar la iteración, verificar el residuo original y comprobar hipótesis antes de ofrecer cota. |
| L09 ✓ | Extender proyección de recta a subespacio. | Mostrar la proyección, el residuo y su ortogonalidad a cada vector de una base. |
| L10 ✓ | Agregar Gram–Schmidt. | Mostrar cada proyección y normalización; detectar dependencia antes de dividir. |
| L11 ✓ | Construir la QR reducida desde la base ortonormal. | Confirmar $Q^TQ=I$ y $QR=A$. En otra sesión comparar la variante modificada con columnas casi dependientes. |
| L12 ✓ | Resolver mínimos cuadrados. | Comprobar $A^Tr=0$ y distinguir cuándo los coeficientes son únicos. Reutilizar QR para columnas independientes. |
| L13 ✓ | Obtener valores propios. | Construir y resolver el polinomio característico de una matriz pequeña. Explicitar el cuerpo real o complejo y multiplicidades. |
| L14 ✓ | Construir un espacio propio. | Reducir $A-\lambda I$ con el motor actual y verificar cada vector con $Av=\lambda v$. |
| L15 ✓ | Decidir diagonalización. | Verificar que los espacios propios aportan una base y comprobar $AP=PD$. Mostrar una matriz defectiva. |
| L16 ✓ | Aplicar el teorema espectral. | Para A real simétrica verificar una base propia ortonormal. En otra fase visualizar los ejes de la forma cuadrática. |
| L17 ✓ | Agregar el método de la potencia. | Normalizar, explicar la semilla y el autovalor dominante; detener por un criterio que muestre el residuo. |
| L18 ✓ | Explorar cadenas de Markov. | Validar probabilidades y convención por columnas; comparar una cadena regular y otra periódica desde el mismo estado inicial. |
| L19 ✓ | Visualizar la SVD. | Verificar reconstrucción para una matriz rectangular. En sesiones posteriores añadir truncamiento por rango y compresión de una imagen de ejemplo. |
| L20 ✓ | Ajustar una recta por regresión. | Mover un dato actualiza los residuos y su suma cuadrática; reutilizar mínimos cuadrados. |
| L21 ✓ | Construir interpolación de Newton. | Con nodos distintos mostrar tabla de diferencias divididas y comprobar todos los valores en sus nodos. |
| L22 ✓ | Construir el mismo interpolante con Lagrange. | Exponer cada polinomio base y verificar que ambas formas coinciden. |
| L23 ✓ | Agregar spline cúbico natural. | Mostrar condiciones en extremos, continuidad y paso por los nodos. Detectar abscisas repetidas. |
| L24 ✓ | Comparar trapecios con el Simpson compuesto existente. | Elegir n, comprobar paridad en Simpson 1/3, mostrar pesos y separar estimación de cota. En otra sesión extender a Romberg. |
| L25 ✓ | Derivar con diferencias finitas. | Un esquema por sesión: hacia adelante, atrás y centrado. Variar h y distinguir truncamiento y redondeo. Después añadir extrapolación de Richardson. |
| L26 ✓ | Integrar una EDO con Euler. | Paso, pendiente, siguiente punto y contraste con solución conocida; añadir Heun y RK4 en sesiones independientes. |
| L27 ✓ | Agregar una aplicación visual por sesión. | Elegir red eléctrica, caminos en grafos o código binario. Vincular cada elemento del dibujo con la ecuación o entrada matricial que representa. |

## Verificación de L01–L27

Las 36 operaciones del catálogo llevan el prefijo `libros.`. Se abren desde los módulos existentes. Los casos de cierre usan datos propios. El motor calcula las trazas y las muestras que muestran las vistas Resultado, Procedimiento y Tabla.

| Fase | Entrada en Synapsis | Evidencia |
| --- | --- | --- |
| L01 ✓ | Sistemas → Intersección de rectas y planos | Dos rectas dan el punto (2,1) y al mover la segunda se recalcula el cruce. En 3D los planos $x=1$, $y=2$ dejan una recta de dirección (0,0,1). Por encima de tres incógnitas se muestran rangos y pivotes. |
| L02 ✓ | Vectores → Transformación del plano y cambio de base | Cambiar $B$ cambia las coordenadas del mismo $v$ y mantiene $T(v)$. La escena actualiza $v$, $T(v)$ y las imágenes de ambas columnas de la base. |
| L03 ✓ | Vectores → Tres normas y bolas unitarias | Para (3,4), la norma 1 da 7, la euclidiana da 5 y la infinita da 4. El selector alterna entre rombo, círculo y cuadrado, y enlaza a Jacobi. |
| L04 ✓ | Matrices → Determinante como área orientada | Con primera columna (2,1), las segundas columnas (1,3), (2,1) y (3,1) producen, respectivamente, los determinantes 5, 0 y −1. |
| L05 ✓ | Sistemas → Pivoteo con redondeo simulado | El ejemplo a tres cifras significativas conserva la referencia racional. El pivoteo parcial reduce el error observado y la traza muestra los multiplicadores de ambas variantes. |
| L06 ✓ | Sistemas → Sensibilidad a perturbaciones | Ambas normas inducidas verifican la cota. Un sistema singular informa que la sensibilidad de una solución única queda indefinida. |
| L07 ✓ | Raíces → Intervalos candidatos | La malla de $(x-1)/x$ señala el hueco en torno a 0 y resalta el cambio de signo continuo cerca de 1. $(x-1/7)^2$ muestra por qué puede pasar inadvertida una raíz par. |
| L08 ✓ | Raíces → Punto fijo con dos despejes | Para $x^2-x=0$, $g_1(x)=(x+1)/2$ en $[3/4,5/4]$ certifica $q=1/2$ y comprueba el residuo. $g_2(x)=x^2$ muestra la trayectoria hasta salir del intervalo. |
| L09 ✓ | Vectores → Proyección sobre un subespacio | Se comprueba que cada producto del residuo con la base ortogonal es cero. |
| L10 ✓ | Vectores → Gram–Schmidt | Cada columna muestra sus proyecciones y su normalización. Con columnas proporcionales, se detecta el resto nulo antes de dividir. |
| L11 ✓ | Matrices → QR exacta y comparación de variantes | Se verifican $Q^TQ=I$ y $QR=A$. Con las columnas casi dependientes del ejemplo, la variante modificada reduce el error de ortogonalidad a cinco cifras significativas. |
| L12 ✓ | Sistemas → Mínimos cuadrados | Se usa QR cuando las columnas son independientes. Para columnas dependientes se muestran una solución, las direcciones de la familia y $A^Tr=0$. |
| L13 ✓ | Matrices → Valores propios | La rotación de 90° tiene los valores $i$ y $-i$ sobre $\mathbb C$. Sobre $\mathbb R$ la lista está vacía. |
| L14 ✓ | Matrices → Espacio propio | Para la matriz con filas (0,2) y (1,0), el espacio propio de $\sqrt{2}$ verifica $Av=\sqrt{2}v$. También se comprueba el espacio complejo de la rotación. |
| L15 ✓ | Matrices → Diagonalización | El bloque de Jordan de orden dos es defectivo. La rotación se diagonaliza en el cuerpo complejo y cumple $AP=PD$. |
| L16 ✓ | Matrices → Teorema espectral | Para la matriz con filas (2,1) y (1,2) se muestran ambos ejes y se comprueban ortonormalidad y reconstrucción. Se rechaza una matriz no simétrica. |
| L17 ✓ | Iterativos → Método de la potencia | Con diagonal (3,1) y semilla (1,1), la estimación converge a 3. Cada paso calcula el residuo y el resultado explicita las hipótesis sobre la semilla. |
| L18 ✓ | Matrices → Cadenas de Markov | El ejemplo regular se compara desde el mismo estado con el ciclo que alterna (1,0) y (0,1). Las columnas y el estado inicial deben sumar uno. |
| L19 ✓ | Matrices → SVD y truncamiento / Compresión de una imagen | Una matriz rectangular de valores singulares 3 y 2 deja error de Frobenius 2 al conservar rango 1. El deslizador recalcula la imagen gris de ejemplo. |
| L20 ✓ | Graficadora → Regresión lineal | Los puntos (0,1), (1,3) y (2,5) tienen suma cuadrática cero. Al mover un punto se actualizan la recta, los residuos y su suma. |
| L21 ✓ | Graficadora → Interpolación de Newton | La tabla por órdenes muestra cada diferencia dividida. El interpolante pasa por todos los nodos. |
| L22 ✓ | Graficadora → Interpolación de Lagrange | Se muestran las bases cardinales. La diferencia simbólica con Newton se expande a cero. |
| L23 ✓ | Graficadora → Spline cúbico natural | Se verifican las condiciones naturales, la continuidad hasta la segunda derivada y el paso por cada nodo. Se rechazan abscisas repetidas. |
| L24 ✓ | Graficadora → Trapecios y Simpson 1/3 / Romberg | Simpson obtiene $1/3$ para $x^2$ en [0,1]. Romberg obtiene $1/5$ para $x^4$. La prueba de entradas rechaza una malla impar en Simpson. |
| L25 ✓ | Graficadora → Hacia adelante, Hacia atrás, Centrada y Richardson | Para $x^3$ en $x=1$, la centrada reduce el error respecto de las fórmulas laterales y Richardson recupera el valor exacto. Se puede cambiar $h$ en el resultado. |
| L26 ✓ | Graficadora → Euler, Heun y Runge–Kutta de orden 4 | Para $y'=2x$ y $y(0)=1$, a $x=1$ se contrastan los tres métodos con $y=x^2+1$. La referencia se verifica primero en la EDO y en la condición inicial. |
| L27 ✓ | Sistemas → Red de conductancias · Matrices → Caminos de peso mínimo · Bases → Código binario y síndrome | Se comprueban las corrientes nodales, el camino $1\to2\to3$ y un error binario con síndrome (1,1). Cada escena etiqueta los elementos usados en la matriz o las ecuaciones. |

Las matrices pequeñas, los nodos y las iteraciones tienen límites para mantener los ejemplos tratables. Valores propios y diagonalización trabajan hasta orden 3. La SVD usa precisión interna de 50 cifras en matrices de hasta 6×6 y muestra errores de reconstrucción y ortogonalidad. Las EDO usan pendientes polinómicas de grado total hasta 8 y hasta 60 pasos. Punto fijo certifica una cota cuando prueba contracción e invariancia y conserva aritmética exacta en el recorrido.

**Pruebas.** `python -m unittest discover -s pruebas -v` incluye los criterios anteriores y ejecuta los ejemplos de las 36 operaciones desde el catálogo. `node --test pruebas/test_expression_input.mjs` cubre la entrada matemática. En Qt WebEngine se recorrieron los 36 ejemplos y sus pestañas de procedimiento a 390 y 1366 píxeles. Con el movimiento pausado, la portada coincide píxel por píxel con la versión anterior a ambos anchos. Se comprobaron desde los resultados la edición de la recta, la bola unitaria, la columna del determinante, un punto de regresión, el rango de compresión y el paso de diferencias finitas.

## Referencias por tema

- Grossman, §§2.8 y 4.5, capítulos 6 y 8. Rectas, planos, redes, mínimos cuadrados y valores característicos.
- Lay, §§4.9 y 6.3–6.6, capítulo 7. Cadenas de Markov, proyección, Gram–Schmidt, ajuste y descomposición en valores singulares.
- Poole, §§4.5, 5.3 y 7.2–7.4. Método de la potencia, comparación de variantes QR y compresión por rango.
- Chapra y Canale, §§6.1, 9.2–9.4, 11.1–11.2, 17.1, 18.1–18.2, 18.6, 21.1–21.2, 22.2, 23.1–23.2 y 25.1–25.3. Criterios de parada, pivoteo, interpolación, cuadratura, diferencias y EDO.
- Consultas complementarias sobre [proyección y ajuste](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/resources/lecture-16-projection-matrices-and-least-squares/), [interpolación](https://dlmf.nist.gov/3.3) y [cuadratura](https://dlmf.nist.gov/3.5).
