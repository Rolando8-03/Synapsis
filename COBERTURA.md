# Cobertura de los procedimientos

[Auditoría de variantes de las 22 sesiones y los teoremas aplicados](docs/cobertura-sesiones.md).

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


## V01 · Sesiones 01–22 y Programas 1–9

Son ejercicios propios que reproducen una técnica de cada sesión. Los Programas 1–9 se vincularon con las consignas y la técnica verificada. Los datos indicados son suficientes para el caso. Las opciones omitidas usan el valor habitual. El campo o valor de la última columna se reemplaza sobre esa misma entrada.

| Sesión o programa | Módulo y método | Entrada | Comprobación a mano | Resultado observado | Caso límite |
| --- | --- | --- | --- | --- | --- |
| Sesión 01 | `"matrices/matrices.notacion"` | `"A"` = `"1 2\n3 4"`, `"fila"` = `"2"`, `"columna"` = `"1"` | a₂₁ es la primera entrada de la segunda fila. | `"entrada"` = `"3"` | `"fila"` = `"3"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 02 / Programa 1 | `"sistemas/sistemas.resolver"` | `"A"` = `"2 1\n4 3"`, `"b"` = `"5 11"`, `"metodo"` = `"gauss"` | F₂−2F₁ deja y=1 y, por sustitución, x=2. | `"particular"` = `["2", "1"]` | `"b"` = `"5"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 03 / Programa 2 | `"sistemas/sistemas.resolver"` | `"A"` = `"1 2\n2 5"`, `"b"` = `"5 13"`, `"metodo"` = `"gauss_jordan"` | F₂−2F₁ deja y=3. F₁−2F₂ da x=−1. | `"particular"` = `["-1", "3"]` | `"A"` = `""`. Solicita completar el campo vacío. |
| Sesión 04 | `"sistemas/original.sistema"` | `"matrix"` = `[["1", "2", "3"], ["2", "4", "6"]]` | La segunda ecuación es el doble de la primera. Queda una variable libre. | `"rango_A"` = `1`, `"rango_aumentada"` = `1` | `"matrix"` = `[["1", "2", "3"], ["2", "4", "7"]]`. `"rango_A"` = `1`, `"rango_aumentada"` = `2` |
| Sesión 05 / Programa 3 | `"vectores/vectores.combinacion"` | `"u"` = `"1 2"`, `"v"` = `"2 -1"`, `"alpha"` = `"2"`, `"beta"` = `"-1"` | 2(1,2)−(2,−1)=(0,5). | `"vector"` = `["0", "5"]` | `"v"` = `"2"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 06 / Programa 4 | `"vectores/vectores.analizar"` | `"vectores"` = `"1 2\n2 4"` | El segundo vector es el doble del primero. | `"dimension_generado"` = `1` | `"vectores"` = `""`. Solicita completar el campo vacío. |
| Sesión 07 | `"sistemas/sistemas.homogeneo"` | `"A"` = `"1 2\n2 4"` | x=−2y. El núcleo tiene dimensión uno. | `"dimension"` = `1` | `"A"` = `""`. Solicita completar el campo vacío. |
| Sesión 08 | `"sistemas/modelos.balance"` | `"A"` = `"1 -1"` | El balance a−b=0 tiene (1,1) como proporción primitiva positiva. | `"coeficientes_enteros_minimos"` = `[1, 1]` | `"A"` = `""`. Solicita completar el campo vacío. |
| Sesión 09 / Programa 5 | `"matrices/matrices.producto"` | `"A"` = `"1 2\n3 4"`, `"B"` = `"2\n1"` | Los dos productos punto son 2+2 y 6+4. | `"matrix"` = `[["4"], ["10"]]` | `"B"` = `"1 2"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 10 | `"matrices/matrices.inversa"` | `"A"` = `"1 2\n0 1"`, `"metodo"` = `"gauss_jordan"` | La inversa lleva −2 sobre la diagonal. Al multiplicar se recupera I. | `"matrix"` = `[["1", "-2"], ["0", "1"]]` | `"A"` = `"1 2\n2 4"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 11 | `"matrices/determinantes.calcular"` | `"A"` = `"2 1\n3 4"`, `"metodo"` = `"reduccion"` | 2·4−1·3=5. | `"valor"` = `"5"` | `"metodo"` = `"sarrus"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 12 / Programa 6 | `"sistemas/factorizacion.lu"` | `"A"` = `"2 1\n4 3"` | El factor es 2 y la última fila de U queda (0,1). LU recupera A. | `"L"` = `[["1", "0"], ["2", "1"]]`, `"U"` = `[["2", "1"], ["0", "1"]]` | `"A"` = `"0 1\n2 1"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 13 | `"vectores/espacios.subespacio"` | `"variables"` = `"x y"`, `"ecuaciones"` = `"x-y=0"` | La ecuación homogénea contiene el cero y se conserva por combinación lineal. | `"es_subespacio"` = `true` | `"ecuaciones"` = `"x-y=1"`. `"es_subespacio"` = `false` |
| Sesión 14 | `"vectores/espacios.base"` | `"vectores"` = `"1 0\n0 1\n1 1"` | Los dos primeros vectores son una base y su suma produce el tercero. | `"dimension_objetivo"` = `2` | `"vectores"` = `""`. Solicita completar el campo vacío. |
| Sesión 15 | `"vectores/espacios.fundamentales"` | `"A"` = `"1 2\n2 4"` | Una columna pivote y una variable libre dan rango y nulidad uno. | `"rango"` = `1`, `"nulidad"` = `1` | `"A"` = `""`. Solicita completar el campo vacío. |
| Sesión 16 | `"vectores/transformaciones.formula"` | `"variables"` = `"x y"`, `"componentes"` = `"x+y\nx-y"` | Las imágenes de e₁=(1,0) y e₂=(0,1) son (1,1) y (1,−1). | `"lineal"` = `true` | `"componentes"` = `"x+z"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 17 | `"vectores/transformaciones.formula"` | `"variables"` = `"x y"`, `"componentes"` = `"x^2\ny^2"` | T(2,0)=(4,0) mientras 2T(1,0)=(2,0). | `"lineal"` = `false` | `"componentes"` = `"x+"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 18 | `"errores/errores.calcular"` | `"referencia"` = `"4"`, `"aproximado"` = `"3"` | |4−3|=1 y el error relativo es 1/4. | `"respecto_referencia.absoluto"` = `"1"`, `"respecto_referencia.relativo"` = `"1/4"` | `"referencia"` = `"?"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 19 / Programa 7 | `"raices/raices.biseccion"` | `"expresion"` = `"x-2"`, `"inferior"` = `"1"`, `"superior"` = `"3"` | El primer punto medio es 2 y f(2)=0. | `"aproximacion"` = `"2"`, `"residual"` = `"0"` | `"expresion"` = `"1/(x-2)"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 20 | `"iterativos/iterativos.sor"` | `"A"` = `"2 0\n0 2"`, `"b"` = `"2 4"`, `"omega"` = `"1"` | Con ω=1 y matriz diagonal, cada componente es bᵢ/2. | `"vector"` = `["1", "2"]` | `"omega"` = `"2"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 21 / Programa 8 | `"iterativos/iterativos.comparar"` | `"A"` = `"2 0\n0 2"`, `"b"` = `"2 4"` | Los dos métodos dan (1,2) para la diagonal, con residuo cero. | `"referencia_exacta"` = `["1", "2"]` | `"b"` = `"1"`. Emite diagnóstico de entrada o de aplicabilidad. |
| Sesión 22 / Programa 9 | `"raices/raices.newton"` | `"expresion"` = `"2*x-4"`, `"inicial"` = `"0"` | La derivada es 2 y el paso desde cero es 0−(−4)/2=2. | `"aproximacion"` = `"2"`, `"residual"` = `"0"` | `"expresion"` = `"x^2-2"`. `"aproximacion"` = `"0"`, `"residual"` = `"2"` |

## V02 · Semanas de Cálculo I y II

Se contrastó la correspondencia de cada ejercicio con el índice de la carpeta docente y con el sílabo del curso. Se verificó una técnica representativa por semana. El ejercicio de la semana 10 de Cálculo II reproduce el formato de entrega solicitado en el segundo corte con funciones propias. El resultado contiene la integral y sus pasos de planteamiento. La comprobación exige la ausencia de un área numérica.

[Sílabo de Cálculo I](https://drive.google.com/file/d/1BM6N0-ff60uAEQufxCcrhaonq6AduDSe/view) · [Sílabo de Cálculo II](https://drive.google.com/file/d/1QpYVGO15xIMgqo9_WyRVg9SO3pXrmQXL/view) · [Segundo corte de Cálculo II](https://drive.google.com/file/d/13hz6jk7bKB29UIQk0-r7A43QXYue1mwJ/view)

| Semana y material | Operación | Entrada | Comprobación a mano | Resultado observado |
| --- | --- | --- | --- | --- |
| [Cálculo I · semana 01](https://drive.google.com/drive/folders/1zRj3qJX9Z7FtrtpSus3ZHW3I03xw_6Ua) | `"grafica/calculo.dominio"` | `"expresion"` = `"1/(x-2)"` | El denominador excluye x=2. | `"dominio"` = `"Union(Interval.open(-oo, 2), Interval.open(2, oo))"` |
| [Cálculo I · semana 02](https://drive.google.com/drive/folders/1ITNqZNb-FL4SaCQkoN-BgznsnST66zfT) | `"grafica/calculo.composicion"` | `"exterior"` = `"sqrt(x)"`, `"interior"` = `"x-2"`, `"punto"` = `"6"` | La función interior da 4 y √4=2. | `"valor"` = `"2"` |
| [Cálculo I · semana 03](https://drive.google.com/drive/folders/1stezUCTYWwD2u_N97vIkzwlBU6176Lh0) | `"grafica/calculo.inversa"` | `"expresion"` = `"x^2"`, `"inferior"` = `"0"`, `"superior"` = `"3"` | En la rama no negativa, y=x² implica x=√y. | `"inversa"` = `"sqrt(y)"` |
| [Cálculo I · semana 04](https://drive.google.com/drive/folders/1R4qO-TMLZDGvPxDapfJsKHU-u22YPJ5n) | `"grafica/calculo.limite_factorizacion"` | `"expresion"` = `"(x^2-4)/(x-2)"`, `"punto"` = `"2"` | Cancelar x−2 fuera de 2 deja x+2, con límite 4. | `"limite"` = `"4"` |
| [Cálculo I · semana 05](https://drive.google.com/drive/folders/1zg4DMcQmHfvywtVLtRFMNGLxeXfAUy3v) | `"grafica/calculo.derivada_definicion"` | `"expresion"` = `"x^2"` | El cociente incremental es 2x+h y su límite es 2x. | `"derivada"` = `"2*x"` |
| [Cálculo I · semana 06](https://drive.google.com/drive/folders/15QD-RyuuDOiXASwlQNwL-VSG2wFxsX4D) | `"grafica/calculo.derivada_cadena"` | `"expresion"` = `"(x^2+1)^3"` | Multiplicar 3(x²+1)² por 2x. | `"derivada"` = `"6*x*(x**2 + 1)**2"` |
| [Cálculo I · semana 07](https://drive.google.com/drive/folders/1CRncx_y-hnHfFdoYSNtEleVytjxYwDTD) | `"grafica/calculo.derivada_logaritmica"` | `"expresion"` = `"ln(2*x)"` | Para x>0, (2x)′/(2x)=1/x. | `"derivada"` = `"1/x"` |
| [Cálculo I · semana 08](https://drive.google.com/drive/folders/1yIFvLdSQvDt1gu8kQvVulwrlRtSLW_vM) | `"grafica/calculo.derivada_implicita"` | `"izquierda"` = `"x^2+y^2"`, `"derecha"` = `"4"` | 2x+2y·y′=0 da −x/y si y≠0. | `"derivada"` = `"-x/y"` |
| [Cálculo I · semana 09](https://drive.google.com/drive/folders/1JrU0_bEApK0V_zsL0xwnWoX6OhPkeM55) | `"grafica/calculo.parcial_sucesiva"` | `"expresion"` = `"x^2*y"`, `"orden"` = `"x y"` | Derivar primero respecto de x da 2xy y luego respecto de y da 2x. | `"derivada"` = `"2*x"` |
| [Cálculo I · semana 10](https://drive.google.com/drive/folders/1ySxoh9vtRYUhoF51ePwwTt2T4_RD7DQK) | `"grafica/calculo.signos"` | `"expresion"` = `"x^3-3*x"` | f″=6x cambia de signo en cero. | `"inflexiones"` = `["0"]` |
| [Cálculo I · semana 11](https://drive.google.com/drive/folders/1BzoYf7S1zT7qyrTO_w-XknvvUbpffb3l) | `"grafica/calculo.hessiano"` | `"expresion"` = `"x^2-y^2"`, `"x"` = `"0"`, `"y"` = `"0"` | El determinante del hessiano es −4 en el crítico. | `"clasificacion"` = `"Punto silla"` |
| [Cálculo I · semana 12](https://drive.google.com/drive/folders/1IrwUZR_ZoDiK2OAqZPFEKqq2dx3lU3m1) | `"grafica/calculo.rolle"` | `"expresion"` = `"x^2"`, `"inferior"` = `"-2"`, `"superior"` = `"2"`, `"entrega"` = `"resolver"` | Los extremos valen 4 y 2x se anula solo en cero. | `"puntos"` = `"{0}"` |
| [Cálculo I · semana 13](https://drive.google.com/drive/folders/1whlcF60t9JksQ9xmWNkvcVK_QIoIuQYu) | `"grafica/calculo.primitiva"` | `"expresion"` = `"3*x^2"` | x³+C verifica la primitiva por derivación. | `"expresion"` = `"1*x^3 + C"` |
| [Cálculo I · semana 14](https://drive.google.com/drive/folders/1h2wL5b2ZdK-9KzPnX6ome7H_eiqJWdIp) | `"grafica/calculo.sustitucion"` | `"expresion"` = `"2*x*(x^2+1)"`, `"sustitucion"` = `"x^2+1"`, `"inferior"` = `"0"`, `"superior"` = `"1"` | Integrar u entre 1 y 2 da (4−1)/2. | `"valor"` = `"3/2"` |
| [Cálculo I · semana 15](https://drive.google.com/drive/folders/14ZF6vgwjorZq4Dars3_iSAFbFOQLQHca) | `"grafica/calculo.promedio"` | `"expresion"` = `"x^2"`, `"inferior"` = `"0"`, `"superior"` = `"3"` | La integral vale 9 y la longitud 3. | `"valor"` = `"3"` |
| [Cálculo II · semana 01](https://drive.google.com/drive/folders/1_54lPsBiaPVGs-yKYnWOoZanZW_lUavT) | `"grafica/calculo.derivada_trigonometrica"` | `"expresion"` = `"sin(x)"` | La derivada de sen(x) es cos(x). | `"derivada"` = `"cos(x)"` |
| [Cálculo II · semana 02](https://drive.google.com/drive/folders/1-FuGh_mQ3nB64Ud43m86jjTOqQ4l8ebM) | `"grafica/calculo.primitiva"` | `"expresion"` = `"6*x^2"` | Derivar 2x³+C devuelve 6x². | `"expresion"` = `"2*x^3 + C"` |
| [Cálculo II · semana 03](https://drive.google.com/drive/folders/1AQAFrRV7U-L76trxjG58_Vh6LYdqSBI6) | `"grafica/calculo.por_partes"` | `"expresion"` = `"x*exp(x)"` | u=x y dv=eˣ dx dejan xeˣ−eˣ+C. | `"primitiva"` = `"(x - 1)*exp(x) + C"` |
| [Cálculo II · semana 04](https://drive.google.com/drive/folders/1cdcUUaeL0GCCwHdjLyfJPZHHsJgAEedJ) | `"grafica/calculo.fracciones_parciales"` | `"expresion"` = `"1/(x*(x+1))"` | 1/x−1/(x+1) recompone el numerador 1. | `"numerador_reconstruido"` = `"1"` |
| [Cálculo II · semana 05](https://drive.google.com/drive/folders/1_GDG0cD9htLx7_9aeB1zpsHyLwikgUhs) | `"grafica/calculo.potencias_trigonometricas"` | `"familia"` = `"seno_coseno"`, `"potencia"` = `"1"`, `"potencia_coseno"` = `"2"` | u=cos(x) da −u³/3+C. | `"primitiva"` = `"-cos(x)**3/3 + C"` |
| [Cálculo II · semana 06](https://drive.google.com/drive/folders/11wNcgrH3TZprOK8aWUdJpA7z9PMUFl7W) | `"grafica/calculo.potencias_trigonometricas"` | `"familia"` = `"secante"`, `"potencia"` = `"2"` | La derivada de tan(x) es sec²(x). | `"primitiva"` = `"tan(x) + C"` |
| [Cálculo II · semana 07](https://drive.google.com/drive/folders/1bimsWMOe5Mie47m1r4rHVMAjGI26TYID) | `"grafica/calculo.sustitucion_trigonometrica"` | `"familia"` = `"exterior"`, `"parametro"` = `"2"`, `"rama"` = `"positiva"` | El radical √(x²−4) exige x≥2 en esta rama. | `"dominio"` = `"Interval(2, oo)"` |
| [Cálculo II · semana 08](https://drive.google.com/drive/folders/15-VlW0fqjBi_CXEnKN8-qtz18_M3f-YC) | `"grafica/calculo.definida"` | `"expresion"` = `"x^2"`, `"inferior"` = `"0"`, `"superior"` = `"1"` | Evaluar x³/3 en 1 y 0 da 1/3. | `"valor"` = `"1/3"` |
| [Cálculo II · semana 09](https://drive.google.com/drive/folders/11-F330TQkyPFD3sYw_VENUbjH2No8PcM) | `"grafica/calculo.cambio_neto"` | `"expresion"` = `"3"`, `"inferior"` = `"0"`, `"superior"` = `"2"` | La tasa constante por el tiempo es 3·2=6. | `"cambio_neto"` = `"6"` |
| [Cálculo II · semana 10](https://drive.google.com/drive/folders/1vd6xSaOeAoMRg8pKyaxweeoy2F8xbSrT) | `"grafica/calculo.area"` | `"expresion"` = `"x"`, `"segunda"` = `"x^2"`, `"entrega"` = `"plantear"` | Los cortes 0 y 1 delimitan la región. En ella x≥x². El examen pide dejar escrita la integral. | `"cruces"` = `["0", "1"]` y $\int_0^1 (x-x^2)\,dx$ como planteamiento. |
| [Cálculo II · semana 11](https://drive.google.com/drive/folders/1R1va0r4E_2v2jrwjxpuGD7XvrXbyRvOu) | `"grafica/calculo.arandelas"` | `"expresion"` = `"2"`, `"segunda"` = `"1"`, `"inferior"` = `"0"`, `"superior"` = `"1"`, `"entrega"` = `"resolver"` | El área constante de la sección es π(2²−1²)=3π. | `"volumen"` = `"3*pi"` |
| [Cálculo II · semana 12](https://drive.google.com/drive/folders/13VPCXwf5BKPbfIgWqlGj4UZcbB1Ns95V) | `"grafica/calculo.longitud_arco"` | `"expresion"` = `"3*x/4"`, `"inferior"` = `"0"`, `"superior"` = `"4"`, `"entrega"` = `"resolver"` | El segmento avanza 4 y sube 3, por lo que mide 5. | `"valor"` = `"5"` |
| [Cálculo II · semana 13](https://drive.google.com/drive/folders/1uPauEJ7o_W7u51g9i7mUz1JNyxTOTpUf) | `"grafica/calculo.centro_masa"` | `"inferior"` = `"0"`, `"superior"` = `"2"`, `"densidad_izquierda"` = `"2"`, `"densidad_derecha"` = `"2"` | La masa 4 es uniforme y el centro está en x=1. | `"masa"` = `"4"`, `"centro_de_masa"` = `"1"` |
| [Cálculo II · semana 14](https://drive.google.com/drive/folders/1_Y6EhKXhfuDtH_kvnbfnsxzg_OdG5_Gs) | `"grafica/calculo.centroide"` | `"expresion"` = `"1"`, `"segunda"` = `"0"`, `"inferior"` = `"-1"`, `"superior"` = `"1"` | El centroide del rectángulo está en su centro por simetría. | `"centroide"` = `["0", "1/2"]` |
| [Cálculo II · semana 15](https://drive.google.com/drive/folders/15nrUsjLA4hibra_j36qFRZi072ETixWF) | `"grafica/calculo.trabajo_bombeo"` | `"altura"` = `"4"`, `"radio"` = `"2"`, `"entrega"` = `"resolver"` | r=h/2. Integrar γ·πh²/4·(4−h) de 0 a 4 da 16πγ/3. | `"trabajo"` = `"16*pi*gamma/3"` |
| [Cálculo II · semana 16](https://drive.google.com/drive/folders/12o3bU1MhOML5GTIEJub2mWlp9gvbVYln) | `"grafica/calculo.trabajo_resorte"` | `"constante"` = `"12"`, `"inferior"` = `"0"`, `"superior"` = `"1/2"`, `"entrega"` = `"resolver"` | La integral de 12x de 0 a 1/2 da 3/2. | `"trabajo"` = `"3/2"` |

Los 53 ejercicios y los 22 casos límite se ejecutaron en la interfaz Qt WebEngine a 390 y 1366 píxeles. La prueba automática del motor usa los mismos ejercicios y sus referencias independientes. Los comandos, plataforma y revisiones se indican en la [evidencia de entrega](docs/plan/08-entrega.md).
