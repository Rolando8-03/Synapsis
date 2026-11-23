# Synapsis · Observatorio matemático

Proyecto de escritorio para estudiar álgebra lineal y métodos numéricos. Esta edición parte de **Synapsis-Proyecto-Completo** e integra el solucionador de la **Calculadora de Álgebra Lineal del Grupo 4**. Incluye la portada animada, los ocho módulos, el modo serio claro u oscuro y el laboratorio de las tres leyes de Kepler.

## Abrir en Windows

1. Extraé el ZIP completo.
2. Instalá **Python 3.10–3.14 de 64 bits** si aún no está disponible.
3. Ejecutá **Abrir-Synapsis.cmd**. La primera vez prepara el entorno e instala las dependencias. Después abre Synapsis en su propia ventana.
4. Si preferís el navegador, ejecutá **Abrir-Synapsis-Web.cmd**. Mantené su terminal abierta mientras uses la calculadora.

La primera instalación necesita internet. Después, la aplicación funciona con el motor local de Python, imágenes y tipografías incluidas. El motor escucha en `127.0.0.1`. En Linux o macOS, instalá `requirements.txt` en un entorno virtual y ejecutá `python3 abrir.py`. El modo navegador usa `requirements-matematica.txt` y `python3 abrir.py --web`.

## Cómo usar la calculadora

- Abrí una tarjeta para trabajar a pantalla completa. La barra lateral permite cambiar de operación y se pliega a iconos con **«**. Su preferencia queda guardada.
- En **Sistemas lineales**, trabajá con la cuadrícula aumentada y la columna separada de `b`. Podés pegar una matriz, cambiar sus dimensiones y elegir qué partes del desarrollo mostrar.
- Al completar la cuadrícula se prepara el cálculo. **Resolver** muestra el resultado en el lugar del formulario. **Editar datos** vuelve a las entradas anteriores. **Cargar ejemplo** carga y resuelve un caso de la operación.
- Para obtener exclusivamente los factores, elegí **Sistemas lineales → Factorización → Solo factorizar A = LU**. Usá **Solo factorizar PA = LU** para trabajar con pivoteo o **Resolver Ax=b mediante LU o PLU** cuando también querás calcular la solución.
- **Temario del curso**, en la barra lateral, enlaza las 22 sesiones con sus operaciones y ejemplos. **Historial** reabre cálculos del módulo.

## Temario y formatos

| Sesiones | Herramientas |
| --- | --- |
| 1–4 | Notación matricial, operaciones por fila, ecuaciones, clasificación, rangos, pivotes, REF y RREF. |
| 5–7 | Combinaciones, paralelogramo, independencia de vectores y polinomios, núcleo y familia de soluciones. |
| 8 | Intercambio y equilibrio económico, balance por conteos, flujos y mezclas con restricciones no negativas. |
| 9–12 | Operaciones, inversa, teorema de invertibilidad, determinantes, Cramer numérico y paramétrico, LU y PLU. |
| 13–15 | Generación, bases, dimensión, subespacios por ecuaciones, suma e intersección. |
| 16–17 | Linealidad por componentes polinómicas, imágenes de una base, matriz, núcleo, imagen, rango y nulidad. |
| 18 | Errores, tolerancia, propagación, truncamiento, redondeo, precisión, punto flotante y bases numéricas. |
| 19–22 | Bisección y Newton-Raphson con tablas, Jacobi, Gauss-Seidel, SOR y gráfica comparativa. |

Las operaciones aceptan datos editables. Los enunciados de modelación se traducen a ecuaciones o matrices antes de resolver. El análisis de subespacios por ecuaciones se aplica a restricciones lineales. Cramer paramétrico admite un parámetro en matrices cuadradas de hasta orden cuatro, con ecuaciones polinómicas. Clasifica los casos singulares racionales y enumera las raíces algebraicas cuando aparecen. Las fórmulas se muestran con KaTeX y MathML, y las tablas conservan los valores exactos cuando el método los calcula.

## Archivos

| Archivo o carpeta | Contenido |
| --- | --- |
| `abrir.py`, `backend.py`, `curso.py`, `kepler.py`, `temario.py` | Inicio, cálculo local y catálogo del curso. |
| `dist/` | Interfaz, animaciones, simulaciones, KaTeX, Three.js y recursos de presentación. |
| `calculadora_original/` | Código y materiales de la calculadora del Grupo 4, con el crédito colectivo del Grupo 4. |
| `nexolineal/` | Algoritmos Python de álgebra lineal y métodos numéricos. |
| `recursos-originales/` | PNG originales de la nave y el paisaje. |
| `legado-frontend/` | Archivos de cálculo que acompañaban la edición web de origen. |


## Procedimientos de esta edición

La pestaña **Procedimiento** muestra las sustituciones y estados intermedios de la misma ejecución. Los productos separan cada fila y columna. Gauss-Jordan identifica el bloque aumentado y los pivotes en la matriz reducida. Newton-Raphson presenta la derivada, las aproximaciones, el error y el residuo, con sus tangentes en la gráfica. El comparador ejecuta Jacobi y Gauss-Seidel con una misma configuración.

Consultá la [cobertura de los procedimientos](COBERTURA.md). Para ejecutar las pruebas, desde la carpeta de Synapsis corré `python -m unittest discover -s pruebas -v`.
