# Álgebra y métodos de los Programas 1–9

Reutilizá `curso.py`, `procedimientos.py`, `motor_grupo4/` y `motor_matematico/algorithms/`. Los casos de `pruebas/test_procedimientos.py` ya cubren parte del desarrollo. Usá la ruta existente y verificá la salida frente a la guía correspondiente.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| A01 | Gauss: desarrollar una operación de fila entrada por entrada. | En [A ∣ b], mostrar pivote, factor, antes y después, incluido el independiente. |
| A02 | Gauss-Jordan: justificar la clasificación desde la última fila y los rangos. | Probar una solución, una familia e incompatibilidad en la cuadrícula original. |
| A03 | Construir una dirección del núcleo por variable libre. | La salida general verifica $Ax_p=b$ y $Av_i=0$ para cada dirección. |
| A04 | Relacionar combinación de columnas y producto fila por columna. | Para un caso del primer examen se reconstruyen ambos lados de $A(u+v)=Au+Av$. |
| A05 | Exhibir una relación de dependencia. | Un coeficiente libre produce una combinación no trivial igual a cero; repetir en polinomios usando los coeficientes existentes. |
| A06 | Desplegar la cuenta de un menor al expandir por cofactores. | En orden cinco se puede seguir una rama hasta orden dos con signo y factores. Sarrus queda restringido a orden tres. |
| A07 | Acumular el efecto de cada operación sobre el determinante. | Intercambiar y escalar filas muestra el factor y recupera el determinante original. |
| A08 | Auditar el desarrollo de la inversa por un método por sesión. | Para Gauss-Jordan seguir [A ∣ I]. Para adjunta verificar transposición y división. Comprobar la identidad y explicar el caso singular. |
| A09 | Clasificar un valor singular algebraico en Cramer paramétrico. | En la matriz con filas $(s,1),(2,s)$ probar $s=\sqrt2$ con rangos exactos; si el determinante es idénticamente cero estudiar la compatibilidad aparte. |
| A10 | Detallar por entrada la eliminación en Solo LU. | En A con filas (2,1),(4,3), el factor 2 produce (0,1) y queda en L. Terminar con el producto. |
| A11 | Mostrar una permutación posterior al primer pivote en PLU. | Las columnas previas de L se actualizan y se comprueba $PA=LU$. |
| A12 | Encadenar las sustituciones desde los factores guardados. | Mostrar [L ∣ Pb] y [U ∣ y], verificar en el sistema original y evitar reingresar A. |
| A13 | Justificar un criterio de subespacio. | En $x=2y$ desarrollar cero y ambas cerraduras con variables generales. En $x=3$ mostrar el testigo que falla. |
| A14 | Reconstruir un cambio de base por columnas. | El mismo vector conserva sus componentes en el espacio original al volver desde las coordenadas en ambas bases. |
| A15 | Justificar la base de la imagen y rango–nulidad. | Seleccionar las columnas pivote de la matriz original y comprobar que rango más nulidad da la dimensión del dominio. |
| A16 | Desarrollar linealidad desde la fórmula. | Explicitar aditividad y homogeneidad; para $T(x)=x^2$ exhibir un contraejemplo. |
| A17 | Trazar la formulación de un modelo del curso. | Una sesión por modelo de flujos, balance o economía: justificar ecuaciones, signos, unidades y restricciones desde datos editables. |
| A18 | Distinguir una medida de error por cálculo. | Para redondeo, truncamiento o propagación mostrar fórmula, cifras perdidas y referencia; si la referencia es cero indicar cuándo el relativo está indefinido. |
| A19 | Explicar un paso de bisección con su cota. | Intervalo inicial, continuidad, signos, mitad elegida y máximo de iteraciones coherentes. Ensayar $1/x$ en [−1,1]. |
| A20 | Distinguir valores viejos y nuevos en la traza iterativa. | Con igual semilla comparar una iteración de Jacobi y Gauss-Seidel; señalar cambio y residuo en la norma elegida. |
| A21 | Justificar el parámetro de relajación de SOR. | Con $\omega=1$ se recupera Gauss-Seidel. Separar condición suficiente, diagnóstico observado y motivo de parada. |
| A22 | Obtener la derivada de Newton por SymPy según el Programa 9. | Para $x^3-x-2$ mostrar $3x^2-1$, sustitución y residuo. Conservar el cálculo propio de iteraciones y validar el dominio. |
| A23 | Corregir la presentación de Newton detenido. | Para $x^2-2$ desde cero mostrar último punto y residuo 2; probar además convergencia y límite de iteraciones. |
| A24 | Completar la traza de un método adicional de raíces por sesión. | Para secante o falsa posición mostrar operandos, denominador, decisión y comprobación; detectar denominador nulo. |
| A25 | Auditar una operación restante del catálogo por sesión. | Registrar ID, sesión, datos mínimos, pasos faltantes y caso límite en COBERTURA; cubrir también notación, bloques, conversiones, conjuntos y teoremas. |
