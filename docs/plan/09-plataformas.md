# Ejecución y distribución de Synapsis

**Entregables de esta guía:** abrir la ventana nativa desde `abrir.py`, usar **Go Live** sobre un `index.html` en la raíz, publicar la calculadora funcional en GitHub Pages, instalar Synapsis en Windows y abrir un APK firmado en Android. Cada fila es una fase independiente que se prueba y se integra en `main` según la [guía de ejecución](01-ejecucion.md).

## Base y arquitectura

En la base `bb9fb32`, `abrir.py` inicia PySide6/Qt WebEngine y sirve `dist/` en el equipo. El HTML está en `dist/index.html`. El catálogo, la resolución y el laboratorio consumen las rutas de `abrir.Handler`. Un servidor estático puede entregar los archivos, pero las tres operaciones requieren un motor de ejecución. Comprobá las tres desde el inicio.

Conservá una interfaz y el mismo cálculo Python. El adaptador de escritorio usa el servicio local actual. Para web, proponemos cargar Python con Pyodide en un trabajador web y llamar a `motor_matematico.application.backend.catalog`, `motor_matematico.application.backend.calculate` y las funciones de `motor_matematico/algorithms/kepler.py`. Para Android, empaquetá esa misma distribución en una WebView con origen HTTPS local. La primera prueba en dispositivo debe confirmar carga de WebAssembly, trabajador y dependencias. Si falla, evaluá como alternativa un puente Android al mismo paquete Python y registrá la decisión. Limitá Qt al escritorio. [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) · [Pyodide](https://pyodide.org/en/stable/) · [Recursos locales en Android](https://developer.android.com/develop/ui/views/layout/webapps/load-local-content)

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

## Compilar y publicar

Las distribuciones de la versión `1.0.0` se generan con Python 3.12, PySide6 6.10.2, Pyodide 0.28.3, SymPy 1.14.0 y mpmath 1.3.0. El backend compartido despacha catálogo, cálculo, órbita histórica y escena de Kepler. El trabajador WebAssembly carga bajo demanda, informa el avance y se reinicia cuando se cancela un cálculo ya enviado. Los formularios, resultados y el laboratorio se comparten entre plataformas.

| Destino | Comando o flujo |
| --- | --- |
| Escritorio | `python -m pip install -r requirements.txt` y `python abrir.py`. En Windows, `./plataformas/windows/acceso-directo.ps1` crea el acceso con `pythonw.exe`. Si elegís doble clic sobre un `.py`, usá **Abrir con** y seleccioná el `pythonw.exe` del entorno que tiene las dependencias. La asociación se configura en Windows. |
| Go Live | Abrí `index.html` desde la raíz del clon. El índice conserva el enlace a cualquier módulo. Para usar un paquete independiente, ejecutá `python -m plataformas.web --output build/web` y abrí `build/web/index.html` con Live Server. |
| Pages | En **Settings → Pages → Build and deployment → Source**, la fuente es **GitHub Actions**. El flujo **Publicar Synapsis en GitHub Pages** construye el paquete, publica desde `main` y verifica su revisión, un ejercicio, la gráfica y un clon servido como web estática. [Sitio](https://rolando8-03.github.io/Synapsis/) · [Flujo](https://github.com/Rolando8-03/Synapsis/actions/workflows/pages.yml). |
| Windows x64 | Con Inno Setup 6 instalado, ejecutá `python -m pip install -r requirements.txt -r plataformas/windows/requirements-build.txt` y `./plataformas/windows/compilar.ps1` en PowerShell. La carpeta `build/windows` recibe el instalador y el ZIP portátil. Si solo necesitás compilar el ejecutable de carpeta, usá `-SoloEjecutable`. |
| Android | Con JDK 17, SDK 35, Build Tools 35.0.0 y Gradle 8.11.1, generá `build/web` y ejecutá `gradle -p plataformas/android assembleDebug`. El APK sale en `plataformas/android/app/build/outputs/apk/debug/`. El proyecto declara Android 8.0 como mínimo. El equipo debe tener Android System WebView con soporte para Worker y WebAssembly. |
| Release y ZIP | En **Actions → Distribuciones de Synapsis → Run workflow**, elegí `main` y marcá **Publicar la entrega firmada desde main**. El flujo exige que Pages muestre ese SHA. También se ejecuta al cambiar `plataformas/VERSION` en `main`. El flujo sube solo los dos instaladores a Releases y conserva los ZIP y el paquete web en CI. Publica las sumas SHA-256 en las notas. [Flujo](https://github.com/Rolando8-03/Synapsis/actions/workflows/distribuciones.yml). |

### Firma de Android

Para compilar una release local, configurá `SYNAPSIS_ANDROID_KEYSTORE` con la ruta de tu keystore y las variables `SYNAPSIS_ANDROID_STORE_PASSWORD`, `SYNAPSIS_ANDROID_KEY_ALIAS` y `SYNAPSIS_ANDROID_KEY_PASSWORD`. Generá `build/web`, ejecutá `gradle -p plataformas/android assembleRelease` y verificá con `apksigner verify --verbose --print-certs` el `app-release.apk`. Para el flujo de GitHub, guardá el archivo como un secreto `SYNAPSIS_ANDROID_KEYSTORE_BASE64` y agregá las otras tres variables como secretos de Actions. Base64 es un formato de transporte. Conservá la clave y su respaldo fuera de Git y usá la misma firma para que Android acepte actualizaciones. El APK de depuración se identifica como `io.github.rolando803.synapsis.debug` y se puede instalar junto a la edición `release`.

### GitHub Packages y versión pública

El flujo deposita los instaladores originales en `ghcr.io/rolando8-03/synapsis:1.0.0` con la revisión y el repositorio fuente en el manifiesto OCI. GitHub crea el paquete con visibilidad privada. En la primera publicación, un administrador del paquete debe abrir [GitHub Packages](https://github.com/Rolando8-03/Synapsis/pkgs/container/synapsis) y cambiar **Package settings → Change visibility → Public**. Luego se reintenta la ejecución de la misma versión. El flujo comprueba una descarga anónima y los SHA-256 del paquete antes de abrir la release estable.

El flujo prueba la instalación y arranque de Windows Server 2025 y, para la firma de distribución, la instalación y apertura en un emulador Android API 35. Las notas se generan tras ambas comprobaciones. Las pruebas con teléfonos físicos y actualización sobre una versión anterior se registran por separado.

### Paridad y caché

`python -m plataformas.verificar_web --directorio build/web --prefijo` usa un servidor HTTP de archivos y Qt WebEngine con las conexiones externas bloqueadas. Con `--url URL` probás el paquete publicado y con `--directorio . --cdn` probás el clon limpio y su primera descarga. En Linux sin pantalla, usá `QT_QPA_PLATFORM=offscreen` con el sandbox de Chromium cuando el entorno lo permita. El paquete local ocupa aproximadamente 23 MB y comprueba las sumas de sus dependencias al construirse. Pages puede conservar la distribución anterior hasta que venza la caché. Compará `version-compilada.json` con el SHA reclamado por la entrega.

Los casos comparan el catálogo, los factores exactos de Solo LU, la derivada simbólica y sus pasos, un fallo de dominio, la gráfica de bisección, el cálculo histórico y la escena 3D de Kepler. Las fracciones, los pasos y los textos deben coincidir exactamente. En números de punto flotante se admite tolerancia absoluta de $10^{-12}$ o relativa de $10^{-11}$ por variaciones de trigonometría entre CPython nativo y WebAssembly. Para comparar, instalá solo `requirements.txt` en un entorno nuevo. Así se usa mpmath tanto en escritorio como en web para el contraste numérico de referencia. En Android, completá la matriz de paridad ejecutando los mismos casos y comprobando `pausa`, teclado, zoom y rotación en un dispositivo.

## Evidencia y alcance de la verificación

| Subfases | Validación |
| --- | --- |
| P01–P05 | La ventana Qt usa `abrir.py` y el mismo contrato Python que el trabajador. Se prueba cierre del puerto, ejercicio con el teclado visual y paridad de Solo LU, procedimiento, errores y órbitas. |
| P06–P08 | En Debian 13 y Qt WebEngine 6.10.2, el paquete web ejecutó los siete casos con recursos internos bajo `/Synapsis/`. La primera carga medida tomó 6,3 s. Se observó la cancelación, una nueva petición, el resultado con KaTeX y el sector de Kepler a 0,50 años. |
| P09–P10 | El índice y el paquete estático bajo `/Synapsis/` se probaron con HTTP local. El flujo de Pages verifica la URL pública y repite el ejercicio con un clon limpio. La verificación usa un servidor de archivos equivalente a Live Server. |
| P11–P12 | PyInstaller e Inno Setup generaron el ZIP portátil y el instalador en Windows Server 2025. El flujo comprueba arranque con `pythonw`, registro, destino del acceso de Inicio, cálculo en la instalación, reinstalación y desinstalación. [Primera compilación Windows](https://github.com/Rolando8-03/Synapsis/actions/runs/45314773959). |
| P13–P14 | Se compiló el APK de depuración y `apksigner` verificó su firma. Queda por validar en dispositivo el modo avión, el teclado, el zoom, la orientación y el paso al fondo. [Primera compilación Android](https://github.com/Rolando8-03/Synapsis/actions/runs/45315145332). |
| P15 | Compilación y verificación de la firma `release` configuradas. El APK de distribución requiere la clave del propietario. La instalación y actualización de esa edición quedan para el dispositivo de prueba. |
| P16 | El mismo conjunto de casos compara el JSON de pasos, resultados, errores y muestras. La paridad en dispositivo Android queda pendiente. |
| P17 | El flujo genera artefactos del commit y un ZIP fuente con SHA-256. La publicación versionada condiciona la entrega a una firma Android válida y a la misma revisión en Pages. |
