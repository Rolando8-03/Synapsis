# Cobertura de los procedimientos

| Material del curso | Dónde revisar el desarrollo |
| --- | --- |
| Programas 1 y 2, primer y segundo sistemáticos | Sistemas muestra el planteamiento, matriz inicial, operaciones de Gauss/Gauss-Jordan, pivotes, parametrización y sustitución exacta. |
| Programas 3 y 4, primer examen | Operaciones de vectores y matrices desglosan entradas y productos punto. Independencia reduce la matriz de vectores y trabaja con el sistema homogéneo. |
| Programa 5, quinto y sexto sistemáticos, segundo examen | Matrices muestra productos por entrada, menores/cofactores, determinante y sus efectos de fila, adjunta, inversa y productos de comprobación. |
| Programa 6 | LU y PLU muestran multiplicadores, eliminación, factores y producto. La resolución por LU sigue las dos etapas y verifica el sistema original. |
| Séptimo sistemático y segundo examen | Subespacios y transformaciones enseñan los criterios, la reducción, núcleos, bases de la imagen y rango–nulidad. |
| Programa 7 y octavo sistemático | Bisección comprueba el intervalo, registra los signos, cotas y errores y muestra la gráfica. El contraste independiente usa SciPy si está instalado y mpmath en el entorno estándar. Errores y bases cubren precisión, propagación y desarrollo posicional. |
| Programa 8 y sesión 21 | El comparador utiliza la misma semilla, método de parada y datos en Jacobi y Gauss-Seidel. Muestra sustituciones, gráficas de error y referencia cuando la solución exacta es única. |
| Programa 9 y sesión 22 | Newton-Raphson expone la derivada, cada sustitución, error y residuo. Identifica derivadas problemáticas y límites de iteración. Permite indicar multiplicidad. |

Los resultados teóricos se expresan mediante fórmulas y criterios. Los problemas de aplicación requieren pasar el enunciado a ecuaciones o matrices. En modelos de flujos con restricciones, el procedimiento muestra la formulación y los extremos certificados por el optimizador. Los gráficos usan puntos y tangentes calculados por Python.

Para fórmulas amplias, el panel permite desplazarse horizontalmente. Las tablas y pasos extensos se cargan al abrir su pestaña. Los valores aproximados impresos en iteraciones conservan menos cifras que los datos internos.

## Color

La portada y sus animaciones, los dos modos, la calculadora y el laboratorio comparten una paleta monocromática con base en azul marino `#0B172B`. Los acentos azul claro y azul profundo se ajustan al fondo de cada modo. Los gráficos usan también trazos y etiquetas para distinguir sus series. Referencia de [contraste WCAG](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum).

## Auditoría del catálogo

`test_procedimientos.py` ejecuta el ejemplo de cada operación y comprueba que haya pasos de lectura. También prueba los enlaces de las 22 sesiones. `test_fase_curso.py` comprueba que cada operación diagnostique la ausencia de su primera entrada obligatoria. Los demás campos se dejan con los valores del ejemplo. En la cuadrícula original, el caso límite omite la matriz aumentada. Los criterios de la guía tienen además casos matemáticos representativos e independientes.

| Familia | Caso límite o alcance del desarrollo |
| --- | --- |
| Notación | La fila y columna deben existir. La entrada, su fila y su columna se leen de la matriz ingresada. |
| Bloques | Los cortes separan filas y columnas existentes. Se muestran los bloques resultantes y se contrasta su ensamblaje con la matriz u operación sin partición. |
| Conversiones | Posicional admite bases 2, 8, 10 y 16. La conversión de un entero hexadecimal de 100 cifras a binario produjo 400 cifras y la comprobación inversa exacta. |
| Conjuntos | Complemento exige universo explícito. Con A={a} y U={a,b} se obtiene {b} aunque la entrada repita a. |
| Teoremas | Invertibilidad acepta matrices cuadradas, muestra determinante y rango y distingue la matriz singular. La aplicación de rango–nulidad identifica las columnas originales seleccionadas. |
| Cramer paramétrico | Las filas singulares con parámetros irracionales se clasifican por rangos exactos. La parametrización explícita en esas filas se limita aquí a raíces racionales. |
| Modelos | Las ecuaciones se construyen con los coeficientes editables de la matriz. Balance con varias direcciones muestra una base del núcleo y deja la elección de una combinación positiva al usuario. |
| Cálculo simbólico | La derivada de Newton se presenta cuando el resultado de SymPy puede evaluarse en el motor. Si la derivada excede ese lenguaje, la operación permite ingresar una expresión explícita. |
| Fases de ampliación | El registro de operaciones existentes conserva los pasos del catálogo. Las demostraciones generales, los nuevos métodos y el desarrollo adicional de Cálculo se rigen por sus guías temáticas. |

### Operaciones verificadas

La sesión corresponde a los enlaces actuales del temario. «Catálogo» indica una operación disponible desde su módulo. Se indican los campos mínimos requeridos por el esquema. Algunas opciones requieren datos adicionales al seleccionarlas.

| ID | Sesión | Campos requeridos | Pasos del ejemplo |
| --- | --- | --- | --- |
| `original.sistema` | 2, 3, 4, 7 | `matrix` | 16 |
| `sistemas.resolver` | Catálogo | `A`, `b` | 11 |
| `sistemas.homogeneo` | 7 | `A` | 5 |
| `sistemas.cramer` | 11 | `A`, `b` | 28 |
| `sistemas.parametrico` | 11 | `variables`, `parametro`, `ecuaciones` | 6 |
| `sistemas.inversa` | 10 | `A`, `b` | 20 |
| `factorizacion.lu` | 12 | `A` | 5 |
| `factorizacion.plu` | 12 | `A` | 5 |
| `factorizacion.resolver` | 12 | `A`, `b`, `metodo` | 17 |
| `original.triangular` | 12 | `A`, `B`, `b` | 13 |
| `sistemas.ecuaciones` | 2, 5, 8 | `variables`, `ecuaciones` | 6 |
| `modelos.economia` | 8 | `A`, `unidades` | 27 |
| `modelos.balance` | 8 | `A` | 23 |
| `modelos.flujos` | 8 | `A`, `b` | 35 |
| `matrices.notacion` | 1 | `A`, `fila`, `columna` | 1 |
| `matrices.comparar` | 9 | `A`, `B` | 7 |
| `matrices.suma` | 9 | `A`, `B` | 2 |
| `matrices.resta` | Catálogo | `A`, `B` | 2 |
| `matrices.producto` | 9 | `A`, `B` | 2 |
| `matrices.escalar` | Catálogo | `A`, `k` | 2 |
| `matrices.transpuesta` | 9 | `A` | 2 |
| `matrices.traza` | Catálogo | `A` | 1 |
| `matrices.potencia` | Catálogo | `A`, `exponente` | 1 |
| `matrices.analizar` | Catálogo | `A` | 16 |
| `matrices.ref` | 3 | `A` | 5 |
| `matrices.rref` | 3 | `A` | 8 |
| `matrices.elemental` | 1 | `A` | 1 |
| `matrices.propiedades` | 1, 9 | `A` | 17 |
| `determinantes.calcular` | 11 | `A` | 8 |
| `determinantes.cofactores` | 11 | `A` | 4 |
| `matrices.inversa` | 10 | `A` | 20 |
| `original.inversa_adjunta` | 10 | `A` | 13 |
| `original.propiedades_det` | 11 | `A`, `B`, `eje`, `fila_i`, `fila_j`, `k` | 9 |
| `matrices.teorema_invertible` | 10 | `A` | 37 |
| `matrices.particionar` | Catálogo | `A` | 1 |
| `matrices.suma_bloques` | Catálogo | `A`, `B` | 3 |
| `matrices.producto_bloques` | Catálogo | `A`, `B` | 1 |
| `vectores.suma` | Catálogo | `u`, `v` | 3 |
| `vectores.resta` | Catálogo | `u`, `v` | 3 |
| `vectores.escalar` | Catálogo | `u`, `k` | 3 |
| `vectores.producto_punto` | Catálogo | `u`, `v` | 2 |
| `vectores.producto_cruz` | Catálogo | `u`, `v` | 4 |
| `vectores.norma` | Catálogo | `u` | 2 |
| `vectores.angulo` | Catálogo | `u`, `v` | 3 |
| `vectores.combinacion` | 5 | `u`, `v`, `alpha`, `beta` | 3 |
| `vectores.paralelogramo` | 5 | `u`, `v`, `alpha`, `beta` | 2 |
| `vectores.proyeccion` | Catálogo | `u`, `v` | 5 |
| `vectores.analizar` | 6, 14 | `vectores` | 5 |
| `vectores.generado` | 5, 13 | `vectores`, `v` | 7 |
| `espacios.polinomios` | 6, 13 | `grado`, `familia` | 13 |
| `espacios.subespacio` | 13, 14, 15 | `variables`, `ecuaciones` | 12 |
| `espacios.fundamentales` | 15 | `A` | 10 |
| `espacios.base` | 14, 15 | `vectores` | 2 |
| `espacios.suma` | 15 | `U`, `V` | 12 |
| `espacios.interseccion` | 15 | `U`, `V` | 12 |
| `espacios.coordenadas` | 14 | `base`, `v` | 7 |
| `espacios.cambio_base` | Catálogo | `base_origen`, `base_destino` | 22 |
| `transformaciones.formula` | 16, 17 | `variables`, `componentes` | 18 |
| `transformaciones.analizar` | 16, 17 | `A` | 10 |
| `transformaciones.desde_imagenes` | 16 | `base_dominio`, `imagenes` | 5 |
| `transformaciones.componer` | Catálogo | `A`, `B` | 1 |
| `transformaciones.representar` | 17 | `A`, `base_dominio`, `base_codominio` | 5 |
| `original.relaciones` | 6 | `A`, `u`, `v`, `c` | 14 |
| `grafica.explicita` | Catálogo | `expr`, `from`, `to` | 10 |
| `grafica.parametrica` | Catálogo | `expr`, `y`, `from`, `to` | 10 |
| `funciones.evaluar` | Catálogo | `expresion`, `punto` | 1 |
| `calculo.derivar` | Catálogo | `expresion` | 2 |
| `calculo.primitiva` | Catálogo | `expresion` | 3 |
| `original.primitiva` | Catálogo | `expresion` | 2 |
| `calculo.definida` | Catálogo | `expresion`, `inferior`, `superior` | 2 |
| `calculo.numerica` | Catálogo | `expresion`, `inferior`, `superior` | 5 |
| `calculo.limite_lateral` | Catálogo | `expresion`, `punto`, `lado` | 2 |
| `calculo.derivada_parcial` | Catálogo | `expresion`, `variable` | 1 |
| `calculo.sumatoria` | Catálogo | `expresion`, `inferior`, `superior` | 1 |
| `raices.biseccion` | 19 | `expresion`, `inferior`, `superior` | 30 |
| `raices.falsa_posicion` | 19 | `expresion`, `inferior`, `superior` | 13 |
| `raices.newton` | 22 | `expresion`, `inicial` | 6 |
| `raices.secante` | Catálogo | `expresion`, `anterior`, `inicial` | 6 |
| `iterativos.jacobi` | 20 | `A`, `b` | 45 |
| `iterativos.gauss_seidel` | 20 | `A`, `b` | 25 |
| `iterativos.sor` | 20 | `A`, `b`, `omega` | 28 |
| `iterativos.dominancia` | 20, 21 | `A` | 4 |
| `iterativos.comparar` | 21 | `A`, `b` | 76 |
| `errores.calcular` | 18 | `aproximado` | 1 |
| `errores.redondeo` | 18 | `numero`, `decimales`, `cifras` | 4 |
| `errores.propagacion` | 18 | `expresion`, `x`, `delta` | 3 |
| `errores.acumulacion` | 18 | `capital`, `tasa`, `periodos`, `decimales` | 14 |
| `errores.taylor` | 18 | `x`, `delta`, `terminos`, `decimales` | 6 |
| `errores.exactitud` | 18 | `mediciones`, `referencia` | 3 |
| `errores.maquina` | 18 | `a`, `b` | 3 |
| `calculadora.evaluar` | Catálogo | `expresion` | 2 |
| `bases.enteros` | 18 | `numero`, `origen`, `destino` | 3 |
| `conversiones.bases` | Catálogo | `numero` | 8 |
| `bases.romanos` | Catálogo | `sentido`, `numero` | 3 |
| `conjuntos.operar` | Catálogo | `A` | 2 |
