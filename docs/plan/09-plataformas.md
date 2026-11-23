# Ejecución y distribución de Synapsis

**Entregables de esta guía:** abrir la ventana nativa desde `abrir.py`, usar **Go Live** sobre un `index.html` en la raíz, publicar la calculadora funcional en GitHub Pages, instalar Synapsis en Windows y abrir un APK firmado en Android. Cada fila es una fase independiente que se prueba y se integra en `main` según la [guía de ejecución](01-ejecucion.md).

## Base y arquitectura

En la base `bb9fb32`, `abrir.py` inicia PySide6/Qt WebEngine y sirve `dist/` en el equipo. El HTML está en `dist/index.html`. El catálogo, la resolución y el laboratorio consumen las rutas de `abrir.Handler`. Un servidor estático puede entregar los archivos, pero las tres operaciones requieren un motor de ejecución. Comprobá las tres desde el inicio.

Conservá una interfaz y el mismo cálculo Python. El adaptador de escritorio usa el servicio local actual. Para web, proponemos cargar Python con Pyodide en un trabajador web y llamar a `backend.catalog`, `backend.calculate` y las funciones de `kepler.py`. Para Android, empaquetá esa misma distribución en una WebView con origen HTTPS local. La primera prueba en dispositivo debe confirmar carga de WebAssembly, trabajador y dependencias. Si falla, evaluá como alternativa un puente Android al mismo paquete Python y registrá la decisión. Limitá Qt al escritorio. [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) · [Pyodide](https://pyodide.org/en/stable/) · [Recursos locales en Android](https://developer.android.com/develop/ui/views/layout/webapps/load-local-content)

| Fase | Una tarea | Prueba para integrar |
| --- | --- | --- |
| P01 | Convertir `abrir.py` en la entrada documentada del escritorio. | Con las dependencias instaladas, ejecutar el archivo desde el IDE o con Python abre la ventana propia; cerrar libera el puerto. Mostrar los errores de inicio en una forma legible también en modo gráfico. |
| P02 | Probar apertura gráfica en Windows. | Lanzar `pythonw.exe abrir.py` por acceso directo sin consola. Documentar la asociación necesaria si se desea doble clic sobre el .py. El usuario final también podrá usar P12. |
| P03 | Encapsular el transporte de catálogo. | La interfaz obtiene los mismos IDs con el adaptador de escritorio. Conservar las rutas y el historial actuales. |
| P04 | Encapsular el transporte de resolución. | Desde la misma tarjeta comprobar Solo LU, petición de pasos y un error de dominio antes y después. |
| P05 | Encapsular el transporte orbital. | La misma configuración produce las mismas muestras y unidades. Conservar compatibilidad con K01–K08. |
| P06 | Ejecutar el catálogo real en el trabajador Python web. | Cargar versiones compatibles de Python, SymPy y mpmath, comprobar importaciones del catálogo y registrar tiempo de primera carga. Mostrar progreso y permitir reintentar un fallo. |
| P07 | Conectar una resolución real en el trabajador. | Una derivada simbólica y Solo LU producen los mismos pasos y resultados que escritorio. Comprobar cancelación de un cálculo largo y nueva petición. |
| P08 | Conectar Kepler al trabajador. | Mover el tiempo funciona en un servidor estático con el servicio local de escritorio apagado. |
| P09 | Entregar la entrada raíz para Go Live. | Desde un clon limpio, abrir el `index.html` raíz con Live Server y resolver un caso. Incluir los recursos listos para ese recorrido o cargarlos automáticamente en primera apertura. Mantener una sola fuente de interfaz. Probar también bajo el prefijo `/Synapsis/`. |
| P10 | Preparar la publicación reproducible en Pages desde main. | El flujo de GitHub Actions genera el sitio con índice, módulos, fuentes, trabajador y dependencias en rutas relativas. En la URL de proyecto publicada probar catálogo, resolución y órbitas desde otro equipo. Registrar límites de tamaño y caché de la versión probada. |
| P11 | Generar el ejecutable Windows en Windows. | Construir en modo gráfico con PyInstaller, incluir Qt WebEngine, sus procesos auxiliares, archivos de interfaz y dependencias. En un equipo limpio abrir `Synapsis.exe` sin Python instalado, sin consola y resolver sin red. Distribuir el paquete completo si se elige modo carpeta. |
| P12 | Generar un instalador Windows. | Instalar `Synapsis-Setup.exe` por usuario. Verificar nombre, icono y versión de Synapsis en Inicio y Aplicaciones instaladas. Abrir desde Inicio, actualizar y desinstalar. |
| P13 | Abrir la aplicación web empaquetada en Android. | Generar APK de depuración y abrirlo en dispositivo. Cargar recursos internos con WebViewAssetLoader, verificar que el motor arranca en modo avión y registrar versión mínima probada de Android/WebView. |
| P14 | Ajustar la interacción táctil en Android. | En un teléfono, editar una fracción, resolver, ampliar la gráfica y regresar sin perder los datos. Comprobar teclado, orientación y pausa al ir al fondo. |
| P15 | Generar el APK de distribución. | Firmar la compilación release conservando la clave fuera del repositorio. Verificar firma, instalación y actualización desde la versión anterior con la misma identidad. Abrir desde el icono del sistema y repetir un ejercicio sin red. |
| P16 | Verificar paridad de una familia por sesión. | En Python nativo, EXE instalado, Go Live, Pages y APK comparar el mismo caso, sus pasos, el fallo esperado y los datos de la gráfica. Comparar exactamente los resultados racionales y fijar tolerancias justificadas para los numéricos. Registrar capacidad pendiente si algún entorno falla. |
| P17 | Preparar la entrega versionada. | Desde el mismo SHA de main producir ZIP completo, instalador Windows y APK firmado; enlazar el sitio Pages, publicar sumas SHA-256 y documentar comandos reproducibles y versiones probadas. |

Para P11 y P15 consultá las guías de [PyInstaller](https://pyinstaller.org/en/stable/usage.html) y [firma Android](https://developer.android.com/studio/publish/app-signing). La portada y la paleta se verifican con V04 antes de integrar cambios de entrada o empaquetado.
