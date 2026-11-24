# Synapsis

[Plan de refactorización en cinco fases](docs/plan/refactorizacion.md)

Calculadora para escritorio, navegador y Android para estudiar álgebra lineal y métodos numéricos. Esta edición parte de **Synapsis-Proyecto-Completo** e integra el solucionador de la **Calculadora de Álgebra Lineal del Grupo 4**. Incluye la portada animada, ocho tarjetas por tarea y el modo serio claro u oscuro.

## Cómo abrir Synapsis

| Plataforma | Inicio |
| --- | --- |
| Escritorio desde Python | Instalá `requirements.txt` y ejecutá `python abrir.py` desde el IDE o el intérprete. Se abre la ventana nativa de Synapsis. |
| Windows sin consola | Ejecutá `plataformas/windows/acceso-directo.ps1` una vez. El acceso directo de escritorio abre `abrir.py` con `pythonw.exe`. |
| Windows instalado | Descargá `Synapsis-Setup.exe` desde los [artefactos de compilación](https://github.com/Rolando8-03/Synapsis/actions/workflows/distribuciones.yml). Instala para tu usuario y crea el acceso en el menú Inicio. Para usar la edición portátil, extraé todo `Synapsis-Windows-x64.zip`. |
| VS Code y Go Live | Abrí la carpeta de Synapsis, seleccioná el `index.html` raíz y usá **Open with Live Server**. La primera carga descarga el runtime fijado y abre el motor en un trabajador. |
| Navegador | Abrí [Synapsis en GitHub Pages](https://rolando8-03.github.io/Synapsis/). Las fórmulas, los pasos y las órbitas se calculan con Python en el navegador. |
| Android | En los [artefactos de compilación](https://github.com/Rolando8-03/Synapsis/actions/workflows/distribuciones.yml), descargá y extraé `Synapsis-Android-debug` para obtener el `.apk` de prueba. El APK empaqueta los recursos y el motor Python para usarlos sin conexión. |

Para descargar los binarios, iniciá sesión en GitHub y abrí la última ejecución exitosa de **Distribuciones de Synapsis** para `main`. En **Artifacts**, elegí **Synapsis-Windows-x64** o **Synapsis-Android-debug**. Las dos descargas vienen en ZIP. La edición Android de distribución usa la firma del propietario.

Usá Python 3.12 para reproducir los builds automatizados. La instalación inicial de dependencias requiere conexión. El escritorio sirve su interfaz en `127.0.0.1`. También podés ejecutar `python abrir.py --web` para usar ese servidor local con tu navegador. El archivo índice requiere HTTP o HTTPS, como el que proporciona Live Server.

Para preparar la web con todas las dependencias en una carpeta independiente, ejecutá `python -m plataformas.web --output build/web` y abrí `build/web/index.html` con Go Live. Después de preparar el paquete, su ejecución puede hacerse sin conexión. La [guía de plataformas](docs/plan/09-plataformas.md) documenta builds, firma y pruebas.

## Cómo usar la calculadora

El menú ofrece **Cálculo**, **Sistemas lineales**, **Matrices**, **Vectores y espacios**, **Transformaciones lineales**, **Métodos numéricos**, **Graficadora** y **Laboratorio 3D**. La tarjeta de laboratorio abre la simulación de Kepler disponible.

- Abrí una tarjeta para trabajar a pantalla completa. La barra lateral permite cambiar de operación y se pliega a iconos con **«**. Su preferencia queda guardada.
- En **Sistemas lineales**, ingresá ecuaciones o una matriz aumentada. Conservá los datos al elegir Gauss, Jacobi u otro método, al clasificar o al comparar iteraciones.
- **Cargar ejemplo** llena los campos. **Resolver** ejecuta el cálculo y muestra el resultado en el lugar del formulario. **Editar datos** recupera el borrador.
- Para obtener exclusivamente los factores, elegí **Matrices → Factorización → Solo factorizar A = LU**. Usá **Solo factorizar PA = LU** para trabajar con pivoteo o **Sistemas lineales → Factorización → Resolver Ax=b mediante LU o PLU** cuando también querás calcular la solución.
- En **Cálculo**, usá las teclas de integral, derivada o límite. Podés elegir una técnica o dejar la selección en **Automática**.
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
| `index.html`, `dist/` | Entrada estática, única interfaz, animaciones, trabajador web y dependencias de presentación. |
| `motor_api.py`, `plataformas/` | Contrato JSON compartido, compilación para web, Windows y Android y verificación de paridad. |
| `motor_grupo4/` | Rutinas de cálculo y teoremas del Grupo 4 que usa Synapsis. |
| `motor_matematico/` | Algoritmos Python de álgebra lineal y métodos numéricos. |
| `recursos-originales/` | PNG originales de la nave y el paisaje. |

## Procedimientos de esta edición

La pestaña **Procedimiento** muestra las sustituciones y estados intermedios de la misma ejecución. Los productos separan cada fila y columna. Gauss-Jordan identifica el bloque aumentado y los pivotes en la matriz reducida. Newton-Raphson presenta la derivada, las aproximaciones, el error y el residuo, con sus tangentes en la gráfica. El comparador ejecuta Jacobi y Gauss-Seidel con una misma configuración.

Consultá la [cobertura de los procedimientos](COBERTURA.md). Para ejecutar las pruebas, desde la raíz del repositorio corré `python -m unittest discover -s pruebas -v`.

[Plan de implementación de Synapsis por fases pequeñas](docs/plan/README.md)
