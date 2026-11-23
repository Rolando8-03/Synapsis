# Operaciones, modo serio y entrada matemática

Partí de `backend.py` y `dist/workspace*`. Aplicá [las reglas de integración](01-ejecucion.md) a cada fila. La portada pública conserva su diseño. El menú serio muestra solo barra y tarjetas estáticas, con la paleta azul marino actual en ambos temas.

| Fase | Tarea de una sesión | Prueba de cierre |
| --- | --- | --- |
| U01 ✓ | Validar por objetivo usando Solo LU y Resolver por LU como casos piloto. | Con A se entregan L y U. Si se elige resolver sin b, el formulario pide b, conserva A y ofrece factorizar. El servicio devuelve un diagnóstico comprensible. |
| U02 ✓ | Exponer la selección de entregables en una operación existente de Sistemas. | Elegir solo escalonada devuelve su procedimiento y se detiene allí. La selección completa sigue disponible. |
| U03 | Agrupar las tarjetas del menú serio por Álgebra, Cálculo y Métodos numéricos. | Barra y tarjetas con título y fórmula alineados, accesibles por teclado y sin búsqueda, efectos ni animación. Comparar portada antes/después. |
| U04 | Conectar una operación nueva a la navegación actual. | Abre completa, la barra colapsada mantiene iconos identificables y la preferencia persiste. Resolver reemplaza el formulario y Editar recupera los datos. |
| U05 | Introducir un campo MathLive local para una potencia en Derivar. | Con el teclado visible se ingresa $x^3$ sin sintaxis de programación. Teclado físico y edición del historial siguen funcionando sin red tras instalar. |
| U06 | Añadir plantillas de fracción y raíz al teclado de expresiones. | El cursor recorre numerador, denominador y radicando. Un hueco señala su posición y conserva lo escrito. |
| U07 | Añadir plantillas de operadores según el tipo de campo. | Migrar un operador por subfase: límite lateral, derivada parcial, integral con diferencial o sumatoria. Expresión y variable llegan a Python con el mismo significado. |
| U08 | Extender el campo visual a una familia de operaciones por sesión. | Verificar paréntesis, signo menos, producto implícito y dominio con la misma expresión desde teclado y desde historial. Rechazar símbolos ambiguos indicando dónde corregir. |
| U09 | Unificar un tipo de salida por sesión en el visor KaTeX/MathML. | Empezar con la función y su derivada; después vectores, cabeceras y celdas. Comparar una fracción exacta con su aproximación decimal y conservar el texto copiable. |
| U10 | Alinear un bloque de matrices aumentadas grandes. | Una matriz que exceda el umbral de KaTeX conserva separador, pivotes y cabeceras en su tabla alternativa. En móvil solo el bloque ancho se desplaza. |
| U11 | Enlazar un paso, una fila y un punto mediante su índice de cálculo. | En bisección se selecciona la misma iteración desde tabla o gráfico, incluso después de la 24. Reutilizar ese control en las demás escenas. |
| U12 | Añadir reproducción manual al visor de pasos. | Avanzar, retroceder, pausar y usar teclado conserva el estado. Modo serio abre quieto y la vista pausada respeta movimiento reducido. |
| U13 | Asociar un teorema a un paso empezando con invertibilidad. | La ficha muestra enunciado, hipótesis, evidencia de la matriz y conclusión. Añadir cada teorema posterior con su operación. |

**Evidencia U01.** En la vista Resolver Ax=b, ingresar una matriz A con filas (2,1) y (4,3) y dejar b vacío ofrece factorizar esa misma matriz con el método seleccionado. Tanto LU como PLU permiten volver, ingresar b=(5,11) y obtener x=(2,1). Regresión automatizada: `test_lu_inputs_follow_requested_goal`.

**Evidencia U02.** En Sistemas lineales → Resolver y clasificar, elegí «Solo escalonada (Gauss)». Con las filas (1,1 | 3) y (2,3 | 8), la operación F₂ ← F₂ − 2F₁ deja (0,1 | 2) como segunda fila. El procedimiento termina en Gauss. «Análisis completo» permite resolver el mismo sistema. La prueba `test_system_stops_at_requested_echelon_form` cubre también una columna inicial nula y un pivote en la columna aumentada.
