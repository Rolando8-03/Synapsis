# Álgebra y métodos de los Programas 1–9

Reutilizá `curso.py`, `procedimientos.py`, `motor_grupo4/` y `motor_matematico/algorithms/`. Los casos de `pruebas/test_procedimientos.py` ya cubren parte del desarrollo. Usá la ruta existente y verificá la salida frente a la guía correspondiente.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| A01 ✓ | Gauss: desarrollar una operación de fila entrada por entrada. | En [A ∣ b], mostrar pivote, factor, antes y después, incluido el independiente. |
| A02 ✓ | Gauss-Jordan: justificar la clasificación desde la última fila y los rangos. | Probar una solución, una familia e incompatibilidad en la cuadrícula original. |
| A03 ✓ | Construir una dirección del núcleo por variable libre. | La salida general verifica $Ax_p=b$ y $Av_i=0$ para cada dirección. |
| A04 ✓ | Relacionar combinación de columnas y producto fila por columna. | Para un caso del primer examen se reconstruyen ambos lados de $A(u+v)=Au+Av$. |
| A05 ✓ | Exhibir una relación de dependencia. | Un coeficiente libre produce una combinación no trivial igual a cero; repetir en polinomios usando los coeficientes existentes. |
| A06 ✓ | Desplegar la cuenta de un menor al expandir por cofactores. | En orden cinco se puede seguir una rama hasta orden dos con signo y factores. Sarrus queda restringido a orden tres. |
| A07 ✓ | Acumular el efecto de cada operación sobre el determinante. | Intercambiar y escalar filas muestra el factor y recupera el determinante original. |
| A08 ✓ | Auditar el desarrollo de la inversa por un método por sesión. | Para Gauss-Jordan seguir [A ∣ I]. Para adjunta verificar transposición y división. Comprobar la identidad y explicar el caso singular. |
| A09 ✓ | Clasificar un valor singular algebraico en Cramer paramétrico. | En la matriz con filas $(s,1),(2,s)$ probar $s=\sqrt2$ con rangos exactos; si el determinante es idénticamente cero estudiar la compatibilidad aparte. |
| A10 ✓ | Detallar por entrada la eliminación en Solo LU. | En A con filas (2,1),(4,3), el factor 2 produce (0,1) y queda en L. Terminar con el producto. |
| A11 ✓ | Mostrar una permutación posterior al primer pivote en PLU. | Las columnas previas de L se actualizan y se comprueba $PA=LU$. |
| A12 ✓ | Encadenar las sustituciones desde los factores guardados. | Mostrar [L ∣ Pb] y [U ∣ y], verificar en el sistema original y evitar reingresar A. |
| A13 ✓ | Justificar un criterio de subespacio. | En $x=2y$ desarrollar cero y ambas cerraduras con variables generales. En $x=3$ mostrar el testigo que falla. |
| A14 ✓ | Reconstruir un cambio de base por columnas. | El mismo vector conserva sus componentes en el espacio original al volver desde las coordenadas en ambas bases. |
| A15 ✓ | Justificar la base de la imagen y rango–nulidad. | Seleccionar las columnas pivote de la matriz original y comprobar que rango más nulidad da la dimensión del dominio. |
| A16 ✓ | Desarrollar linealidad desde la fórmula. | Explicitar aditividad y homogeneidad; para $T(x)=x^2$ exhibir un contraejemplo. |
| A17 ✓ | Trazar la formulación de un modelo del curso. | Una sesión por modelo de flujos, balance o economía: justificar ecuaciones, signos, unidades y restricciones desde datos editables. |
| A18 ✓ | Distinguir una medida de error por cálculo. | Para redondeo, truncamiento o propagación mostrar fórmula, cifras perdidas y referencia; si la referencia es cero indicar cuándo el relativo está indefinido. |
| A19 ✓ | Explicar un paso de bisección con su cota. | Intervalo inicial, continuidad, signos, mitad elegida y máximo de iteraciones coherentes. Ensayar $1/x$ en [−1,1]. |
| A20 ✓ | Distinguir valores viejos y nuevos en la traza iterativa. | Con igual semilla comparar una iteración de Jacobi y Gauss-Seidel; señalar cambio y residuo en la norma elegida. |
| A21 ✓ | Justificar el parámetro de relajación de SOR. | Con $\omega=1$ se recupera Gauss-Seidel. Separar condición suficiente, diagnóstico observado y motivo de parada. |
| A22 ✓ | Obtener la derivada de Newton por SymPy según el Programa 9. | Para $x^3-x-2$ mostrar $3x^2-1$, sustitución y residuo. Conservar el cálculo propio de iteraciones y validar el dominio. |
| A23 ✓ | Corregir la presentación de Newton detenido. | Para $x^2-2$ desde cero mostrar último punto y residuo 2; probar además convergencia y límite de iteraciones. |
| A24 ✓ | Completar la traza de un método adicional de raíces por sesión. | Para secante o falsa posición mostrar operandos, denominador, decisión y comprobación; detectar denominador nulo. |
| A25 ✓ | Auditar una operación restante del catálogo por sesión. | Registrar ID, sesión, datos mínimos, pasos faltantes y caso límite en COBERTURA; cubrir también notación, bloques, conversiones, conjuntos y teoremas. |


## Evidencia de cierre

| Fase | Caso verificado |
| --- | --- |
| A01–A03 | La cuadrícula de Sistemas muestra cada sustitución en $[A\mid b]$, la última fila de Gauss-Jordan y los rangos. Se probaron solución única, familia con dos variables libres e incompatibilidad. Para la familia se comprobaron la particular y las dos direcciones con la matriz original. |
| A04–A05 | La operación de relaciones desarrolla el producto fila por fila y la combinación de columnas de $A(u+v)$. Para $1+x$ y $2+2x$, la relación de coeficientes $(-2,1)$ reconstruye el polinomio cero. |
| A06–A08 | Una matriz de orden cinco tiene determinante −144 por cofactores y por reducción. La traza llega a un menor de orden dos y registra el factor acumulado de intercambios y escalas. Se probaron Sarrus fuera de 3×3 y ambas rutas de inversa con matrices invertibles y singulares. |
| A09 | Para $A=[[s,1],[2,s]]$ y $s=\sqrt2$, los rangos son $(1,2)$ con $b=(1,0)$ y $(1,1)$ con $b=(s,2)$. Con $sx=1$ y $0y=0$ la compatibilidad cambia en $s=0$ aunque el determinante sea idénticamente cero. |
| A10–A12 | En LU el multiplicador 2 deja la fila $(0,1)$. En PLU con filas $(4,1,2),(2,1,3),(1,5,4)$ se intercambian los multiplicadores $1/2$ y $1/4$ después del primer pivote. «Resolver con estos factores» conserva A, desarrolla $[L\mid Pb]$ y $[U\mid y]$ y comprueba $x=(1,1,1)$ para $b=(7,6,10)$. |
| A13–A16 | $x=2y$ contiene el origen y satisface ambas cerraduras. $x=3$ falla en el origen. Se verifican la reconstrucción en ambas bases, las columnas originales que generan la imagen y el contraejemplo numérico para $T(x)=x^2$. |
| A17–A18 | Economía, balance y flujos exponen las ecuaciones con signos y unidades. Redondeo y propagación identifican la referencia y explican cuándo el error relativo queda indefinido. |
| A19–A21 | Bisección rechaza $1/x$ en $[-1,1]$ y justifica el intervalo siguiente y su cota. Para semilla cero, $A=[[4,1],[2,3]]$ y $b=(1,2)$, Jacobi da $(1/4,2/3)$ y Gauss-Seidel da $(1/4,1/2)$ en la primera iteración. SOR con $\omega=1$ reproduce la tabla de Gauss-Seidel. |
| A22–A24 | Newton obtiene $3x^2-1$ mediante SymPy y usa la derivada en el cálculo de sus iterados. Para $x^2-2$ desde cero muestra el último punto 0 y el residuo 2. Se probaron el máximo de iteraciones, el denominador nulo de secante y la sustitución de falsa posición. |
| A25 | Se revisaron los ejemplos y la falta de una entrada esencial de las 95 operaciones. El registro de cobertura incluye el vínculo con las sesiones y los casos límite de notación, bloques, conversiones, conjuntos y teoremas. |
