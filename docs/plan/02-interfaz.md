# Operaciones, modo serio y entrada matemática

Partí de `backend.py` y `dist/workspace*`. Aplicá [las reglas de integración](01-ejecucion.md) a cada fila. La portada pública conserva su diseño. El menú serio muestra solo barra y tarjetas estáticas, con la paleta azul marino actual en ambos temas.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| U01 ✓ | Validar por objetivo usando Solo LU y Resolver por LU como casos piloto. | Con A se entregan L y U. Si se elige resolver sin b, el formulario pide b, conserva A y ofrece factorizar. El servicio devuelve un diagnóstico comprensible. |
| U02 ✓ | Exponer la selección de entregables en una operación existente de Sistemas. | Elegir solo escalonada devuelve su procedimiento y se detiene allí. La selección completa sigue disponible. |
| U03 ✓ | Agrupar las tarjetas del menú serio por Álgebra, Cálculo y Métodos numéricos. | Barra y tarjetas con título y fórmula alineados, accesibles por teclado y sin búsqueda, efectos ni animación. Comparar portada antes/después. |
| U04 ✓ | Conectar una operación nueva a la navegación actual. | Abre completa, la barra colapsada mantiene iconos identificables y la preferencia persiste. Resolver reemplaza el formulario y Editar recupera los datos. |
| U05 ✓ | Introducir un campo MathLive local para una potencia en Derivar. | Con el teclado visible se ingresa $x^3$ sin sintaxis de programación. Teclado físico y edición del historial siguen funcionando sin red tras instalar. |
| U06 ✓ | Añadir plantillas de fracción y raíz al teclado de expresiones. | El cursor recorre numerador, denominador y radicando. Un hueco señala su posición y conserva lo escrito. |
| U07 · en curso | Añadir plantillas de operadores según el tipo de campo. | Migrar un operador por subfase: límite lateral, derivada parcial, integral con diferencial o sumatoria. Expresión y variable llegan a Python con el mismo significado. |
| U08 · en curso | Extender el campo visual a una familia de operaciones por sesión. | Verificar paréntesis, signo menos, producto implícito y dominio con la misma expresión desde teclado y desde historial. Rechazar símbolos ambiguos indicando dónde corregir. |
| U09 | Unificar un tipo de salida por sesión en el visor KaTeX/MathML. | Empezar con la función y su derivada; después vectores, cabeceras y celdas. Comparar una fracción exacta con su aproximación decimal y conservar el texto copiable. |
| U10 | Alinear un bloque de matrices aumentadas grandes. | Una matriz que exceda el umbral de KaTeX conserva separador, pivotes y cabeceras en su tabla alternativa. En móvil solo el bloque ancho se desplaza. |
| U11 | Enlazar un paso, una fila y un punto mediante su índice de cálculo. | En bisección se selecciona la misma iteración desde tabla o gráfico, incluso después de la 24. Reutilizar ese control en las demás escenas. |
| U12 | Añadir reproducción manual al visor de pasos. | Avanzar, retroceder, pausar y usar teclado conserva el estado. Modo serio abre quieto y la vista pausada respeta movimiento reducido. |
| U13 | Asociar un teorema a un paso empezando con invertibilidad. | La ficha muestra enunciado, hipótesis, evidencia de la matriz y conclusión. Añadir cada teorema posterior con su operación. |

**Evidencia U01.** En la vista Resolver Ax=b, ingresar una matriz A con filas (2,1) y (4,3) y dejar b vacío ofrece factorizar esa misma matriz con el método seleccionado. Tanto LU como PLU permiten volver, ingresar b=(5,11) y obtener x=(2,1). Regresión automatizada: `test_lu_inputs_follow_requested_goal`.

**Evidencia U02.** En Sistemas lineales → Resolver y clasificar, elegí «Solo escalonada (Gauss)». Con las filas (1,1 | 3) y (2,3 | 8), la operación F₂ ← F₂ − 2F₁ deja (0,1 | 2) como segunda fila. El procedimiento termina en Gauss. «Análisis completo» permite resolver el mismo sistema. La prueba `test_system_stops_at_requested_echelon_form` cubre también una columna inicial nula y un pivote en la columna aumentada.

**Evidencia U03.** El menú serio agrupa los ocho módulos bajo Álgebra, Cálculo y Métodos numéricos. En Chromium, a 1366 y 390 píxeles de ancho, se comprobó la alineación de títulos y fórmulas en ambos temas. Tab recorre las tarjetas en orden, Enter abre cada módulo y Escape devuelve el foco a su tarjeta. Las capturas de la portada y de los módulos públicos con movimiento reducido coincidieron píxel por píxel con la versión anterior.

**Evidencia U04.** Sistemas lineales → Resolución → Resolver por Gauss o Gauss-Jordan abre la operación `sistemas.resolver`. Con las filas (0,2) y (3,1) de A y el vector b=(1,5), ambos métodos dan x=(3/2,1/2). La prueba `test_system_method_selector_is_available_from_navigation` comprueba el acceso desde el catálogo y el certificado de un sistema incompatible. En Chromium a 1366 y 390 píxeles se verificaron la resolución, la edición de los datos y la reapertura desde el historial. En escritorio el icono G/J sigue visible al plegar la barra y la preferencia se conserva al recargar.

**Evidencia U05.** En Graficadora → Cálculo → Derivada, pulsar «x», «Exponente» y «3» escribe la potencia en el campo MathLive. Al evaluar en x=2, Resolver devuelve la derivada 3x² y el valor 12. Un exponente vacío pide completarlo. En Chromium a 1366 y 390 píxeles, con las conexiones externas bloqueadas, se verificaron el teclado visual, la escritura física de un exponente negativo y la edición desde el historial después de recargar. La entrada de texto conserva la notación de los cálculos anteriores. Synapsis incluye MathLive 0.111.4 y carga el editor y sus fuentes desde el servidor local.

**Evidencia U06.** En Derivada, usá «Fracción», escribí el numerador y pulsá «Siguiente hueco» para pasar al denominador. «Raíz cuadrada» inserta el radicando y puede envolver lo seleccionado. En Qt WebEngine a 390 y 1366 píxeles se probaron los huecos incompletos, el cambio entre editor visual y texto y la recuperación desde el historial. En x=4 se verificaron las derivadas de x/2, de la raíz de x y de (x/2)³, con valores 1/2, 1/4 y 6.

**U07-integral ✓** En Graficadora → Cálculo → Primitiva de reglas admitidas, el editor muestra $\int \square\,\mathrm{d}x$. Ingresá $x/2$ con la tecla Fracción y pulsá Resolver. Python recibe el integrando y la variable $x$ y devuelve $x^2/4+C$. Con el integrando cero devuelve $0+C$. El historial anterior que solo guardaba la expresión sigue usando $x$. Se comprobaron la entrada incompleta, la edición en texto, el historial y el ejemplo del catálogo en Qt WebEngine a 390 y 1366 píxeles. La prueba `test_primitiva_respects_the_differential_and_older_inputs` comprueba también el rechazo de una variable incompatible.

Quedan tres subfases de U07, cada una en su propia sesión y commit: `U07-limite-lateral`, `U07-derivada-parcial` y `U07-sumatoria`.

**U08-intervalo ✓** En Raíces → Métodos de intervalo, Bisección y Falsa posición aceptan $-2(x-1)$ con el teclado visual. En $[0,2]$ ambos encuentran $x=1$. La misma expresión se recupera al editar y desde el historial. Un símbolo como $y$ se señala en el campo y cada método comprueba el dominio en Python. Para $1/(x-1)$ en ese intervalo se conserva el formulario con los extremos ingresados. Se verificaron ambos métodos a 390 y 1366 píxeles y la reapertura de cálculos antiguos guardados como texto. Las pruebas de notación se ejecutan con `node --test pruebas/test_expression_input.mjs`.
